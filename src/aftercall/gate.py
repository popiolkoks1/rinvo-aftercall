"""Deterministic guardrail gate. No LLM: a block must be explainable by a rule."""

from __future__ import annotations

import unicodedata
from datetime import date

from . import config
from .dates import parse_iso
from .models import Action, ActionKind, GateResult, Item, ItemType, Person, Status

GUARD_TYPES = (ItemType.guardrail, ItemType.blackout_window)


def active_guardrails(items: list[Item]) -> list[Item]:
    return [
        i for i in items
        if i.type in GUARD_TYPES and i.active and i.status not in (Status.done, Status.declined)
    ]


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("ł", "l").replace("Ł", "L"))
    return s.encode("ascii", "ignore").decode().strip().lower()


def _tags(values: list[str]) -> set[str]:
    return {_fold(v) for v in values if v.strip()}


def _person_tags(name: str | None) -> set[str]:
    return {_fold(name.split()[0]), _fold(name).replace(" ", "_")} if name and name.strip() else set()


def guard_scope(g: Item, primary_contact: str | None = None) -> set[str]:
    """What a guardrail protects. Not part of its scope:
    - the person who can lift it ('only Kasia decides X' protects X, not everything touching Kasia);
    - for guardrails, the primary client contact: rules agreed with them don't forbid talking to them
      (a time-bound 'don't contact me' is a blackout, which keeps its person tags);
    - broad words from config gate.generic_tags."""
    tags = _tags(g.scope_tags) - _person_tags(g.lifted_by)
    if g.type == ItemType.guardrail:
        tags -= _person_tags(primary_contact)
    return tags - _tags(config.settings().get("gate", {}).get("generic_tags", []))


def check(
    action: Action,
    item: Item | None,
    guardrails: list[Item],
    items_by_ref: dict[str, Item],
    people: list[Person],
    as_of: date,
    meeting_date: date,
    primary_contact: str | None = None,
) -> GateResult:
    start = parse_iso(item.earliest_start) if item else None
    planned = parse_iso(action.date)
    exec_date = max(d for d in (as_of, start, planned, meeting_date) if d)
    result = GateResult(status="clear", exec_date=exec_date.isoformat())

    if action.kind == ActionKind.none:
        return result

    # 1. Guardrails and blackouts: kind forbidden + same product area + scope overlaps + date inside window.
    kinds = effective_kinds(action, item)
    a_tags = _tags(action.scope_tags)
    for g in guardrails:
        if item and g.id == item.id:
            continue
        hit = kinds & set(g.forbids_action_kinds)
        if not hit:
            continue
        # A blackout is a time window: it covers all work of its forbidden kinds, whatever its tags say
        # (tag scoping proved unreliable for blackouts). Guardrails are always scoped.
        all_work = g.type == ItemType.blackout_window
        if g.type == ItemType.blackout_window and item and _client_requested_exempt(g, item, kinds):
            result.notes.append(f"{g.id} '{g.title}' doesn't apply: not a new launch, and the client asked for it on the call")
            continue
        if not all_work and _areas_differ(g, item):
            continue
        g_tags = set() if all_work else guard_scope(g, primary_contact)
        if not g_tags and not all_work:
            continue  # an unscoped "don't" is too vague to block on; it stays visible in memory
        if g_tags and not (g_tags & a_tags):
            continue
        ws, we = parse_iso(g.window_start), parse_iso(g.window_end)
        if (ws and exec_date < ws) or (we and exec_date > we):
            continue
        quote = next((e.quote for e in g.evidence if e.found), "")
        overlap = ", ".join(sorted(g_tags & a_tags)) or "all scopes"
        window = f" during {g.window_start}..{g.window_end}" if (ws or we) else ""
        as_new = " (new for end customers)" if ActionKind.launch in hit and action.kind != ActionKind.launch else ""
        result.blocked_by.append(g.id)
        result.reasons.append(
            f"{g.id} '{g.title}': forbids {'/'.join(sorted(k.value for k in hit))}{as_new} on [{overlap}]{window} — \"{quote}\""
        )
    if result.blocked_by:
        result.status = "blocked"
        return result

    if not item:
        return result

    # 2. Not yet: earliest start in the future.
    if start and start > as_of:
        result.status = "not_before"
        result.reasons.append(f"not before {start.isoformat()} ({item.earliest_start_phrase or 'earliest_start'})")

    # 3. Dependencies and triggers. A reminder is itself how we chase the dependency.
    if action.kind != ActionKind.contact:
        pending = [
            r for r in item.depends_on
            if r in items_by_ref and items_by_ref[r].status not in (Status.done,)
        ]
        if pending:
            result.status = "waiting"
            result.reasons.append(
                "waiting on " + "; ".join(f"{items_by_ref[r].id} '{items_by_ref[r].title}'" for r in pending)
            )
        if item.trigger_condition:
            result.status = "waiting"
            result.reasons.append(f"only if: {item.trigger_condition}")

    # 4. Approvals, and whether the approver has authority.
    if item.approver and action.kind not in (ActionKind.contact,):
        if result.status == "clear":
            result.status = "needs_approval"
        result.reasons.append(f"needs approval from {item.approver}")
        approver = next((p for p in people if _same_person(p.name, item.approver)), None)
        if approver and (_tags(approver.cannot_approve) & _tags(action.scope_tags)):
            result.reasons.append(
                f"WARNING: {approver.name} cannot approve "
                f"[{', '.join(sorted(_tags(approver.cannot_approve) & _tags(action.scope_tags)))}]"
            )

    return result


# Kinds that never put anything live, so "new for end customers" can't turn them into a launch.
NON_EXECUTING = {ActionKind.contact, ActionKind.send, ActionKind.none, ActionKind.investigate, ActionKind.build}
NEW_KINDS = {ActionKind.launch, ActionKind.enable}


def effective_kinds(action: Action, item: Item | None) -> set[ActionKind]:
    """Executing something new for end customers counts as a launch, whatever the LLM called it."""
    kinds = {action.kind}
    if item and item.new_for_end_customers and action.kind not in NON_EXECUTING:
        kinds.add(ActionKind.launch)
    return kinds


def _client_requested_exempt(g: Item, item: Item, kinds: set[ActionKind]) -> bool:
    """A blackout doesn't stop non-new changes the client asked for in the same (or a later) call."""
    return item.client_requested and not (kinds & NEW_KINDS) and item.id[:8] >= g.id[:8]


def _areas_differ(g: Item, item: Item | None) -> bool:
    if not item:
        return False
    ga, ia = (g.product_area or "other"), (item.product_area or "other")
    return "other" not in (ga, ia) and ga != ia


def _same_person(a: str, b: str) -> bool:
    a, b = a.lower().strip(), b.lower().strip()
    if not a or not b:
        return False
    return a == b or a.split()[0] == b.split()[0]
