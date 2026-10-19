"""Extraction, run as parallel Gemini calls.

The transcript is split into N turn ranges. Each call sees the WHOLE transcript (for
context and final values) but only extracts items whose key statement is in its
range, which keeps every response short and fast. A "focus" pass for easy-to-miss
items (refusals, deferrals, guardrails, small promises) runs at the same time.
Duplicates between calls are removed later (postprocess.dedupe + reconcile).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

from . import config, llm
from .models import ExtractionOut, ItemOut, ItemsOut, PersonOut
from .transcript import Transcript


def numbered(t: Transcript) -> str:
    """Header + one line per turn prefixed with [T<n>]. Quotes are taken from the turn text."""
    if not t.turns:
        return t.raw
    lines = [f"[T{x.index}] {x.speaker}: {x.text}" for x in t.turns]
    return t.header.strip() + "\n\n## Transcript (turns numbered)\n\n" + "\n".join(lines)


def _ranges(t: Transcript, n: int) -> list[tuple[int, int]]:
    if n <= 1 or len(t.turns) < 20:
        return [(0, max(len(t.turns) - 1, 0))]
    total = sum(len(x.text) for x in t.turns)
    bounds, acc, start = [], 0, 0
    for x in t.turns:
        acc += len(x.text)
        if len(bounds) < n - 1 and acc >= total * (len(bounds) + 1) / n:
            bounds.append((start, x.index))
            start = x.index + 1
    bounds.append((start, t.turns[-1].index))
    return bounds


def _values(t: Transcript, meeting_date: date) -> dict[str, str]:
    friday = meeting_date + timedelta(days=(4 - meeting_date.weekday()) % 7)
    areas = config.settings()["vendor"].get("product_areas", {"other": "anything"})
    return dict(
        vendor=", ".join(config.settings()["vendor"]["org_names"]),
        meeting_date=meeting_date.isoformat(),
        meeting_weekday=meeting_date.strftime("%A"),
        this_friday=friday.isoformat(),
        next_friday=(friday + timedelta(days=7)).isoformat(),
        product_areas="\n".join(f"  - `{k}`: {v}" for k, v in areas.items()),
        transcript=numbered(t),
    )


def _prefix(items: list[ItemOut], p: str) -> list[ItemOut]:
    """Make refs unique across parallel calls, keeping references inside a call intact."""
    mapping = {i.ref: f"{p}{n}" for n, i in enumerate(items, 1)}
    fix = lambda refs: [mapping.get(r, r) for r in refs]
    for i in items:
        i.ref = mapping[i.ref]
        i.depends_on, i.related_refs = fix(i.depends_on), fix(i.related_refs)
        if i.superseded_by_ref:
            i.superseded_by_ref = mapping.get(i.superseded_by_ref)
    return items


def extract_all(t: Transcript, meeting_date: date, use_cache: bool = True, log=print) -> ExtractionOut:
    values = _values(t, meeting_date)
    ranges = _ranges(t, config.settings()["llm"].get("extract_chunks", 2))
    rules = llm.render(config.prompt("extract"), **{**values, "scope": "", "transcript": "(see below)"})
    rules = rules.split("## Transcript")[0]

    def chunk(rng: tuple[int, int]) -> ExtractionOut:
        out = _chunk(rng)
        if len(ranges) > 1:  # keep only items with at least one quote in (or next to) the range
            out.items = [i for i in out.items if _in_range(i, rng)]
        return out

    def _in_range(i: ItemOut, rng: tuple[int, int]) -> bool:
        turns = [x.index for q in i.evidence_quotes for x in t.turns if q[:40] and q[:40] in x.text]
        return not turns or any(rng[0] - 2 <= n <= rng[1] + 2 for n in turns)

    def _chunk(rng: tuple[int, int]) -> ExtractionOut:
        scope = (
            f"Extract only items whose key statement is in turns T{rng[0]}–T{rng[1]}. "
            "Use the whole transcript for context and for final values."
            if len(ranges) > 1 else "Extract items from the whole call."
        )
        return llm.generate("extract", ExtractionOut, use_cache=use_cache, **{**values, "scope": scope})

    focus_ranges = _ranges(t, config.settings()["llm"].get("focus_chunks", 1))

    def focus(rng: tuple[int, int]) -> ItemsOut:
        scope = (
            f"Only items whose key statement is in turns T{rng[0]}–T{rng[1]}; use the whole transcript for context."
            if len(focus_ranges) > 1 else "The whole call."
        )
        return llm.generate("extract_focus", ItemsOut, use_cache=use_cache,
                            rules=rules, scope=scope, transcript=values["transcript"])

    with ThreadPoolExecutor(max_workers=len(ranges) + len(focus_ranges)) as pool:
        chunk_futs = [pool.submit(chunk, r) for r in ranges]
        focus_futs = [pool.submit(focus, r) for r in focus_ranges]
        parts = [f.result() for f in chunk_futs]
        extra = ItemsOut(items=[i for f in focus_futs for i in _prefix(f.result().items, f"f{focus_futs.index(f)}_")])
    log(f"· extraction: {' + '.join(str(len(p.items)) for p in parts)} items from {len(ranges)} range(s), "
        f"{len(extra.items)} from the focus pass")

    first = parts[0]
    people: dict[str, PersonOut] = {}
    items: list[ItemOut] = []
    for k, p in enumerate(parts):
        items += _prefix(p.items, "abcdefgh"[k])
        for person in p.people:
            people.setdefault(person.name.split()[0].lower(), person)
    items += extra.items
    return ExtractionOut(
        language=first.language, client_name=first.client_name,
        primary_client_contact=first.primary_client_contact, people=list(people.values()), items=items,
    )
