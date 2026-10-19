from __future__ import annotations

import json

from . import config, llm
from .models import ClientState, Item, ItemType, ReconciliationOut, Status
from .transcript import Transcript
from .verify import check_quote


def _compact(item: Item, key: str) -> dict:
    return {
        key: getattr(item, key),
        "type": item.type.value,
        "title": item.title,
        "detail": item.detail,
        "status": item.status.value,
        "due": item.due,
        "earliest_start": item.earliest_start,
        "scope_tags": item.scope_tags,
        "superseded_by_ref": item.superseded_by_ref,
        "quotes": item.evidence_quotes,
    }


def reconcile(items: list[Item], state: ClientState, t: Transcript, use_cache: bool = True) -> list[str]:
    """Apply LLM reconciliation in place. Returns warnings about rejected suggestions."""
    stored_open = [i for i in state.items if i.status not in (Status.done, Status.declined)]
    out = llm.generate(
        "reconcile",
        ReconciliationOut,
        use_cache=use_cache,
        items=json.dumps([_compact(i, "ref") for i in items], ensure_ascii=False, indent=1),
        state=json.dumps([_compact(i, "id") for i in stored_open], ensure_ascii=False, indent=1) or "[]",
        transcript=t.raw,
    )

    by_ref = {i.ref: i for i in items}
    existing_ids = {i.id for i in state.items}
    threshold = config.settings()["verify"]["quote_threshold"]
    warnings: list[str] = []

    guard_types = (ItemType.guardrail, ItemType.blackout_window)
    for s in out.supersessions:
        old, new = by_ref.get(s.ref), by_ref.get(s.superseded_by_ref)
        if old and new and old.type in guard_types and new.type not in guard_types:
            # Folding a guardrail into an ordinary item would silently remove it from the gate.
            warnings.append(f"reconcile: kept guardrail {old.id}; refused supersession by {new.type.value} {new.id}")
            continue
        if s.ref in by_ref and s.superseded_by_ref in by_ref and s.ref != s.superseded_by_ref:
            if by_ref[s.ref].superseded_by_ref is None:
                by_ref[s.ref].superseded_by_ref = s.superseded_by_ref
                by_ref[s.ref].flags.append(f"superseded (reconcile): {s.reason}")
        else:
            warnings.append(f"reconcile: ignored supersession with unknown ref {s.ref}->{s.superseded_by_ref}")

    for a in out.amendments:
        item = by_ref.get(a.ref)
        if not item:
            warnings.append(f"reconcile: ignored amendment for unknown ref {a.ref}")
            continue
        ev = check_quote(a.evidence_quote, t, threshold)
        if not ev.found:
            warnings.append(f"reconcile: amendment to {a.ref} rejected, quote not found: {a.evidence_quote!r}")
            continue
        item.amended_from = f"{item.title} | {item.detail}"
        item.title, item.detail = a.new_title, a.new_detail
        item.evidence_quotes.append(a.evidence_quote)
        item.evidence.append(ev)
        item.flags.append(f"amended (reconcile): {a.reason}")

    for m in out.state_matches:
        if m.ref in by_ref and m.existing_id in existing_ids:
            by_ref[m.ref].state_match = m
        else:
            warnings.append(f"reconcile: ignored state match {m.ref}->{m.existing_id} (unknown id)")

    for c in out.closed_existing:
        if c.existing_id not in existing_ids:
            warnings.append(f"reconcile: ignored close of unknown id {c.existing_id}")
        else:
            warnings.append(f"reconcile: proposes closing stored item {c.existing_id}: {c.reason}")

    return warnings
