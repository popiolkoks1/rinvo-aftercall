"""Markdown report of a run: actions grouped by route, then everything that isn't an action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import ItemType, Status

if TYPE_CHECKING:
    from .pipeline import RunResult

ROUTES = [
    ("ticket", "Tickets → tickets.csv"),
    ("change_checklist", "Config / KB / launch checklist"),
    ("backlog", "Product backlog (cross-client)"),
    ("followup", "Follow-ups → followups.ics"),
    ("internal_note", "Internal notes → drafts/internal_notes.md"),
    ("meeting_brief", "Meeting brief → drafts/meeting_brief.md"),
    ("recap", "Client recap → drafts/recap_email.md"),
]
GATE_ICON = {"clear": "✅", "blocked": "⛔", "waiting": "⏳", "needs_approval": "🔑", "not_before": "🕒"}


def _when(item, action, as_of: str) -> str:
    bits = []
    if action.date:
        bits.append(f"due {action.date}")
    if item and item.earliest_start:
        bits.append(f"not before {item.earliest_start}")
    if action.date and action.date < as_of and action.route != "recap":
        bits.append("past due, status unknown")
    return f" · {', '.join(bits)}" if bits else ""


def render(r: "RunResult") -> str:
    by_id = {i.id: i for i in r.items}
    out = [
        f"# aftercall · {r.client_name} · call {r.meeting_date} · as of {r.as_of}",
        "",
        f"{len(r.items)} items · {sum(i.verified for i in r.items)} with a matching quote · "
        f"{len(r.actions)} proposed actions · "
        f"{sum(a.gate.status == 'blocked' for a in r.actions)} blocked by the gate · "
        f"recap to {r.primary_contact} ({r.language})",
        "",
        "Gate: ✅ clear · ⛔ blocked · ⏳ waiting on dependency/condition · 🔑 needs client approval · 🕒 not before date",
    ]

    for route, label in ROUTES:
        acts = [a for a in r.actions if a.route == route]
        if not acts:
            continue
        out += ["", f"## {label} ({len(acts)})"]
        for a in acts:
            item = by_id.get(a.item_id)
            icon = GATE_ICON.get(a.gate.status, "?")
            idtxt = f"`{item.id}` " if item else ""
            out.append(f"- {icon} {idtxt}{a.title}{_when(item, a, r.as_of.isoformat())}")
            if item and item.detail and route != "recap":
                out.append(f"    - {item.detail}")
            for reason in a.gate.reasons if a.gate.status != "blocked" else []:
                out.append(f"    - _{reason}_")
            for note in a.gate.notes:
                out.append(f"    - _gate note: {note}_")
            if item and any("amended" in f for f in item.flags):
                out.append(f"    - _amended within call; was: {item.amended_from}_")

    blocked = [a for a in r.actions if a.gate.status == "blocked"]
    out += ["", f"## ⛔ Blocked by the gate ({len(blocked)})"]
    if not blocked:
        out.append("- nothing blocked")
    for a in blocked:
        out.append(f"- **{a.title}** ({a.route}, {a.kind.value}, would run {a.gate.exec_date})")
        for reason in a.gate.reasons:
            out.append(f"    - blocked by {reason}")

    guards = [i for i in r.items if i.type in (ItemType.guardrail, ItemType.blackout_window) and i.active]
    out += ["", f"## Guardrails & blackouts captured ({len(guards)})"]
    for g in guards:
        window = f" · {g.window_start}..{g.window_end}" if g.window_start or g.window_end else ""
        forbids = ",".join(k.value for k in g.forbids_action_kinds) or "—"
        lift = f" · lifted by {g.lifted_by}" if g.lifted_by else ""
        out.append(f"- `{g.id}` {g.title} · forbids [{forbids}] on [{', '.join(g.scope_tags) or 'everything'}]{window}{lift}")

    decisions = [i for i in r.items if i.active and i.status in (Status.declined, Status.parked)
                 and i.type not in (ItemType.guardrail, ItemType.blackout_window)]
    out += ["", f"## Decisions — not doing / parked ({len(decisions)})"]
    for i in decisions:
        out.append(f"- `{i.id}` **{i.status.value}** · {i.title}")

    superseded = [i for i in r.items if i.superseded_by_ref]
    out += ["", f"## Superseded within the call ({len(superseded)})"]
    refs = {i.ref: i for i in r.items}
    for i in superseded:
        new = refs.get(i.superseded_by_ref)
        out.append(f"- `{i.id}` ~~{i.title}~~ → `{new.id if new else '?'}` {new.title if new else ''}")

    check = [i for i in r.items if not i.verified or any(f.startswith(("bad_date", "weekday")) for f in i.flags)]
    out += ["", f"## Needs a human check ({len(check)})"]
    for i in check:
        bad = [e.quote for e in i.evidence if not e.found]
        out.append(f"- `{i.id}` {i.title} · {', '.join(f for f in i.flags if not f.startswith(('superseded', 'amended')))}")
        for q in bad:
            out.append(f'    - quote not in transcript: "{q}"')

    if r.draft_flags or r.warnings:
        out += ["", "## Warnings"]
        out += [f"- recap check: {f}" for f in r.draft_flags]
        out += [f"- {w}" for w in r.warnings]
    return "\n".join(out) + "\n"
