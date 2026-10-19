"""Gold-file evaluation. Matching is deterministic: an extracted item matches a
gold item when one of its *found* quotes overlaps the gold anchor and its type
is allowed. Traps are small predicates over the run outputs."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml
from rapidfuzz import fuzz

from .transcript import normalize, parse

MATCH = 80
TURN_WINDOW = 1  # a statement and its direct reply belong together (question/answer, request/ack)
_anchor_turns: dict[str, set[int]] = {}


def _overlaps(quote: str, anchor: str) -> bool:
    return fuzz.partial_ratio(normalize(anchor), normalize(quote)) >= MATCH


def _near(e: dict, anchor: str) -> bool:
    turns = _anchor_turns.get(anchor, set())
    return e.get("turn") is not None and any(abs(e["turn"] - t) <= TURN_WINDOW for t in turns)


def _matching(items: list[dict], anchor: str, types: list[str] | None, active_only=True, window=True) -> list[dict]:
    out = []
    for i in items:
        if active_only and (i["superseded_by_ref"] or not any(e["found"] for e in i["evidence"])):
            continue
        if types and i["type"] not in types:
            continue
        if any(_overlaps(e["quote"], anchor) or (window and _near(e, anchor)) for e in i["evidence"] if e["found"]):
            out.append(i)
    return out


def _index_anchors(gold: dict, transcript_path: str | None) -> None:
    _anchor_turns.clear()
    if not transcript_path or not Path(transcript_path).exists():
        return
    turns = parse(Path(transcript_path)).turns
    for g in gold["must_catch"] + gold["traps"]:
        a = g.get("anchor")
        if a:
            na = normalize(a)
            _anchor_turns[a] = {t.index for t in turns if fuzz.partial_ratio(na, normalize(t.text)) >= 95}


def _text(i: dict) -> str:
    return f"{i['title']} {i['detail']}"


def run(run_dir: Path, gold_path: Path, echo=print) -> bool:
    data = json.loads((run_dir / "items.json").read_text())
    items, actions = data["items"], data["actions"]
    frozen = gold_path.parent / "FROZEN.sha256"
    if frozen.exists():
        digest = hashlib.sha256(gold_path.read_bytes()).hexdigest()
        expected = {ln.split()[1].split("/")[-1]: ln.split()[0] for ln in frozen.read_text().splitlines() if ln.strip()}
        if gold_path.name in expected and expected[gold_path.name] != digest:
            echo(f"ERROR: {gold_path.name} changed since it was frozen (see {frozen.name}); refusing to score.")
            return False
    gold = yaml.safe_load(gold_path.read_text())
    _index_anchors(gold, data.get("transcript"))
    recap = (run_dir / "drafts" / "recap_email.md").read_text() if (run_dir / "drafts" / "recap_email.md").exists() else ""
    ics = (run_dir / "followups.ics").read_text() if (run_dir / "followups.ics").exists() else ""
    gate_by_item: dict[str, list[str]] = {}
    for a in actions:
        gate_by_item.setdefault(a["item_id"], []).append(a["gate"]["status"])

    echo(f"# eval {run_dir.name} vs {gold_path.name}\n")
    caught = 0
    for g in gold["must_catch"]:
        hits = _matching(items, g["anchor"], g.get("types"))
        if g.get("status"):
            hits = [h for h in hits if h["status"] in g["status"]]
        ok = bool(hits)
        caught += ok
        echo(f"{'✓' if ok else '✗'} {g['id']}: {g['desc']}" + (f"  ({', '.join(h['id'] for h in hits)})" if hits else ""))
    recall = caught / len(gold["must_catch"])
    echo(f"\nrecall: {caught}/{len(gold['must_catch'])} = {recall:.0%}\n")

    passed = 0
    for t in gold["traps"]:
        ok, note = _trap(t, items, recap, ics, gate_by_item, data.get("people", []))
        passed += ok
        echo(f"{'✓' if ok else '✗'} trap {t['id']}: {t['desc']}" + (f"  — {note}" if note else ""))
    echo(f"\ntraps: {passed}/{len(gold['traps'])} passed")
    return recall >= gold.get("min_recall", 0.8) and passed == len(gold["traps"])


def _trap(t: dict, items, recap: str, ics: str, gate_by_item, people) -> tuple[bool, str]:
    kind = t["check"]
    active = [i for i in items if not i["superseded_by_ref"] and any(e["found"] for e in i["evidence"])]
    actionable = [i for i in active if i["status"] not in ("declined", "parked", "done")]

    if kind == "no_actionable_item_matching":
        # No open/waiting item of these types whose text matches the regex.
        pool = [i for i in actionable if not t.get("types") or i["type"] in t["types"]]
        bad = [i for i in pool if re.search(t["regex"], _text(i), re.I)]
        return not bad, ", ".join(f"{i['id']} '{i['title']}'" for i in bad)

    if kind == "anchored_status":
        # Turn window only when the trap is narrowed by type, otherwise it over-matches.
        hits = _matching(items, t["anchor"], t.get("types"), window=bool(t.get("types")))
        if not hits:
            return bool(t.get("absent_ok")), "no item found for anchor"
        bad = [h for h in hits if h["status"] not in t["status"]]
        return not bad, ", ".join(f"{h['id']} is {h['status']}" for h in bad)

    if kind == "active_text_matches":
        # Every active item of these types that mentions `about` must also match `regex`.
        pool = [i for i in active if (not t.get("types") or i["type"] in t["types"]) and re.search(t["about"], _text(i), re.I)]
        if not pool:
            return False, "no item about this"
        bad = [i for i in pool if not re.search(t["regex"], _text(i), re.I) or (t.get("not_regex") and re.search(t["not_regex"], _text(i), re.I))]
        return not bad, ", ".join(f"{i['id']} '{i['detail'][:90]}'" for i in bad)

    if kind == "recap_excludes":
        m = re.search(t["regex"], recap, re.I)
        return not m, f"found '{m[0]}'" if m else ""

    if kind == "ics_excludes":
        m = re.search(t["regex"], ics, re.I)
        return not m, f"found '{m[0]}'" if m else ""

    if kind == "anchored_gate_not_clear":
        hits = _matching(items, t["anchor"], t.get("types"), window=False)
        statuses = [s for h in hits for s in gate_by_item.get(h["id"], [])]
        if not statuses:
            return False, "no actions for anchor"
        bad = [s for s in statuses if s == "clear"]
        return not bad, f"gate statuses {statuses}"

    if kind == "person_cannot_approve":
        p = next((p for p in people if p["name"].split()[0].lower() == t["person"].lower()), None)
        if not p:
            return False, "person not found"
        can = any(re.search(t["tag_regex"], x, re.I) for x in p["can_approve"])
        cannot = any(re.search(t["tag_regex"], x, re.I) for x in p["cannot_approve"])
        return cannot and not can, f"can={p['can_approve']} cannot={p['cannot_approve']}"

    return False, f"unknown check {kind}"
