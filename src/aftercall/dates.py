"""Deterministic date checks. The LLM resolves relative dates; code double-checks."""

from __future__ import annotations

import re
from datetime import date

# weekday index -> stems (Polish in all cases, English)
WEEKDAY_STEMS = {
    0: ["poniedzia", "monday"],
    1: ["wtor", "wtork", "tuesday"],
    2: ["środ", "sroda", "srod", "wednesday"],
    3: ["czwart", "thursday"],
    4: ["piąt", "piat", "friday"],
    5: ["sobot", "saturday"],
    6: ["niedziel", "sunday"],
}


def parse_iso(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


def weekdays_named(phrase: str) -> set[int]:
    p = phrase.lower()
    found = set()
    for idx, stems in WEEKDAY_STEMS.items():
        if any(re.search(r"\b" + re.escape(s), p) for s in stems):
            found.add(idx)
    return found


def weekday_mismatch(phrase: str | None, iso: str | None) -> str | None:
    """Return a message if the phrase names a weekday that the ISO date isn't."""
    d = parse_iso(iso)
    if not phrase or not d:
        return None
    named = weekdays_named(phrase)
    if named and d.weekday() not in named:
        return f"'{phrase}' names a weekday but {d.isoformat()} is a {d.strftime('%A')}"
    return None
