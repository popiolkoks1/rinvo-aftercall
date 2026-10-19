"""Per-client state and the cross-client backlog. Changes only on approval."""

from __future__ import annotations

import json
from datetime import datetime

from rapidfuzz import fuzz

from . import config
from .models import ClientState, Item, ItemType, Person


def load(slug: str) -> ClientState:
    f = config.path("clients") / f"{slug}.json"
    if f.exists():
        return ClientState.model_validate_json(f.read_text())
    return ClientState(slug=slug)


def save(state: ClientState) -> None:
    d = config.path("clients")
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{state.slug}.json").write_text(state.model_dump_json(indent=2))


def commit(state: ClientState, items: list[Item], people: list[Person], call: dict) -> dict:
    """Upsert approved items into client state. Returns counts."""
    by_id = {i.id: i for i in state.items}
    added = updated = 0
    for item in items:
        target = item.state_match.existing_id if item.state_match else item.id
        if target in by_id:
            item = item.model_copy(update={"id": target})
            updated += 1
        else:
            added += 1
        by_id[target] = item
    state.items = list(by_id.values())

    known = {p.name.lower(): p for p in state.people}
    for p in people:
        known[p.name.lower()] = p
    state.people = list(known.values())
    state.calls.append({**call, "committed_at": datetime.now().isoformat(timespec="seconds"),
                        "added": added, "updated": updated})
    save(state)
    _update_backlog(state.slug, [i for i in items if i.type == ItemType.feature_request])
    return {"added": added, "updated": updated}


def _update_backlog(slug: str, requests: list[Item]) -> None:
    f = config.path("backlog")
    backlog = json.loads(f.read_text()) if f.exists() else []
    for r in requests:
        match = next((b for b in backlog if fuzz.token_set_ratio(b["title"], r.title) >= 80), None)
        if not match:
            match = {"title": r.title, "clients": [], "request_count": 0, "demand_signals": 0, "items": []}
            backlog.append(match)
        if r.id in match["items"]:
            continue
        match["items"].append(r.id)
        if slug not in match["clients"]:
            match["clients"].append(slug)
            match["request_count"] = len(match["clients"])
        match["demand_signals"] += int(r.demand_signal)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(backlog, ensure_ascii=False, indent=2))
