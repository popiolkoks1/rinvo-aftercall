"""Deterministic clean-up after extraction: field validation, duplicate merge, and
tracker items for client input the vendor is blocked on."""

from __future__ import annotations

from rapidfuzz import fuzz, utils

from . import config
from .models import ActionKind, CommitmentLevel, Item, ItemType, Person, Side, Status, Visibility
from .transcript import Transcript

GUARD_TYPES = (ItemType.guardrail, ItemType.blackout_window)
DUPLICATE_DETAIL_SIMILARITY = 70  # token_sort_ratio on `detail`; calibrated on run 5 (dup 74, next distinct pair 65)


def validate_areas(items: list[Item]) -> None:
    allowed = set(config.settings()["vendor"].get("product_areas", {}))
    for i in items:
        if allowed and i.product_area not in allowed:
            i.flags.append(f"unknown product_area '{i.product_area}' -> other")
            i.product_area = "other"


def _turns(i: Item) -> set[int]:
    return {e.turn for e in i.evidence if e.found and e.turn is not None}


def _near(a: Item, b: Item) -> bool:
    return any(abs(x - y) <= 1 for x in _turns(a) for y in _turns(b))


def dedupe(items: list[Item]) -> list[str]:
    """Merge items that state the same obligation: nearby evidence + near-identical detail.
    The earlier item (first-pass extraction comes first) survives."""
    notes: list[str] = []
    active = [i for i in items if i.active]
    for idx, later in enumerate(active):
        for earlier in active[:idx]:
            if earlier.superseded_by_ref or later.superseded_by_ref:
                continue
            if (earlier.type in GUARD_TYPES) != (later.type in GUARD_TYPES):
                continue
            if earlier.due and later.due and earlier.due != later.due:
                continue
            if not _near(earlier, later):
                continue
            score = fuzz.token_sort_ratio(earlier.detail, later.detail)
            if score >= DUPLICATE_DETAIL_SIMILARITY:
                later.superseded_by_ref = earlier.ref
                later.flags.append(f"duplicate of {earlier.id} (deterministic, similarity {score:.0f})")
                notes.append(f"dedupe: {later.id} '{later.title}' merged into {earlier.id} '{earlier.title}' ({score:.0f})")
    return notes


def synthesize_waiting(items: list[Item], id_prefix: str) -> list[Item]:
    """Every item blocked on client input gets a waiting_on_client tracker, so the input is
    chased and visible. An existing tracker is linked instead of creating a new one."""
    created: list[Item] = []
    trackers = [i for i in items if i.type == ItemType.waiting_on_client and i.active]
    by_ref = {i.ref: i for i in items}
    eligible = [
        i for i in items
        if i.active and i.blocked_on_input and i.status in (Status.open, Status.waiting)
        and i.type not in (ItemType.waiting_on_client, ItemType.meeting_request, *GUARD_TYPES)
    ]
    for item in eligible:
        if any(by_ref.get(r) and by_ref[r].type == ItemType.waiting_on_client for r in item.depends_on):
            continue
        need = item.blocked_on_input or ""
        match = next(
            (
                t for t in trackers
                if fuzz.token_set_ratio(need, f"{t.title} {t.detail}", processor=utils.default_process) >= 70
                or (_near(t, item) and fuzz.token_set_ratio(need, t.detail, processor=utils.default_process) >= 55)
            ),
            None,
        )
        if match:
            item.depends_on.append(match.ref)
            continue
        n = len(items) + len(created) + 1
        person = item.blocked_on_person or None
        tracker = Item(
            ref=f"w{n}", id=f"{id_prefix}-{n:02d}", type=ItemType.waiting_on_client,
            title=f"{need[:1].upper()}{need[1:]} (from {person or 'client'})",
            detail=f"{need}. Needed before we can act on {item.id} '{item.title}'. Created automatically from that item.",
            owner_side=Side.client, owner_person=person, status=Status.open, action_kind=ActionKind.none,
            product_area=item.product_area, new_for_end_customers=False, client_requested=False,
            vendor_commitment_level=CommitmentLevel.no_commitment, blocked_on_input=None, blocked_on_person=None,
            scope_tags=list(item.scope_tags), visibility=Visibility.client, due_phrase=None, due=None,
            earliest_start_phrase=None, earliest_start=None, trigger_condition=None, depends_on=[],
            related_refs=[item.ref], superseded_by_ref=None, approver=None, max_reminders=None,
            forbids_action_kinds=[], window_start=None, window_end=None, lifted_by=None,
            applies_to_all_work=False, demand_signal=False,
            evidence_quotes=list(item.evidence_quotes), confidence=item.confidence,
            evidence=[e.model_copy() for e in item.evidence], flags=[f"created from {item.id} (blocked_on_input)"],
        )
        item.depends_on.append(tracker.ref)
        trackers.append(tracker)
        created.append(tracker)
    return created


def check_commitments(items: list[Item], people: list[Person], t: Transcript) -> list[str]:
    """A bug or feature marked `committed` needs evidence spoken by someone on the vendor side:
    a client describing a problem is not a vendor promise to fix it. Without one, a bug becomes
    `will_look_into` and a feature `no_commitment`. Skipped when speakers can't be mapped to
    people (e.g. 'Speaker 1' transcripts)."""
    side_by_name = {p.name.split()[0].lower(): p.side for p in people}
    speakers = {x.speaker.split()[0].lower() for x in t.turns}
    if not speakers or not speakers <= set(side_by_name):
        return []
    notes = []
    for i in items:
        if i.vendor_commitment_level != CommitmentLevel.committed or i.type not in (ItemType.bug, ItemType.feature_request):
            continue
        sides = {side_by_name.get((e.speaker or "").split()[0].lower()) for e in i.evidence if e.found and e.speaker}
        if Side.vendor not in sides:
            level = CommitmentLevel.will_look_into if i.type == ItemType.bug else CommitmentLevel.no_commitment
            i.vendor_commitment_level = level
            i.flags.append(f"commitment downgraded to {level.value}: no vendor-side quote")
            notes.append(f"commitment: {i.id} '{i.title}' downgraded to {level.value} (only client-side quotes)")
    return notes


def enforce_lift_authority(items: list[Item], people: list[Person]) -> list[str]:
    """If a guardrail can only be lifted by person A, nobody else can approve what it protects."""
    notes = []
    for g in (i for i in items if i.active and i.type == ItemType.guardrail and i.lifted_by):
        lifter = g.lifted_by.split()[0].lower()
        protected = {t.lower() for t in g.scope_tags if len(t) > 2}
        for p in people:
            if p.name.split()[0].lower() == lifter:
                continue
            moved = [c for c in p.can_approve if any(t in c.lower() or c.lower() in t for t in protected)]
            for c in moved:
                p.can_approve.remove(c)
                if c not in p.cannot_approve:
                    p.cannot_approve.append(c)
                notes.append(f"authority: {p.name} cannot approve '{c}' ({g.id} can only be lifted by {g.lifted_by})")
    return notes
