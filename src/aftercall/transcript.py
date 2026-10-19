"""Transcript parsing. Lenient by design: any text works, structure is a bonus.

We try to find (a) a meeting date in the header, (b) speaker turns. If no turns
are found the transcript is still usable; we just lose speaker attribution.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

MONTHS = {
    # Polish genitive + nominative stems, English
    "stycz": 1, "styc": 1, "lut": 2, "mar": 3, "kwiet": 4, "kwie": 4, "maj": 5, "maja": 5,
    "czerw": 6, "lip": 7, "sierp": 8, "wrze": 9, "paźdz": 10, "pazdz": 10, "listop": 11,
    "grud": 12,
    "jan": 1, "feb": 2, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
    "oct": 10, "nov": 11, "dec": 12,
}

# Lines like "**Kasia:** text", "Kasia: text", "Speaker 1: text", "[00:01] Kasia: text"
TURN_RE = re.compile(
    r"^\s*(?:\[?\(?\d{1,2}:\d{2}(?::\d{2})?\)?\]?\s*)?"  # optional timestamp
    r"\*{0,2}([^\s:*\[\]][^:*\n]{0,40}?)\*{0,2}\s*:\s*\*{0,2}\s+(\S.*)$"
)
TRANSCRIPT_HEADING_RE = re.compile(r"^#{1,6}\s*(transkrypcja|transcript|rozmowa|conversation)\b", re.I)


@dataclass
class Turn:
    index: int
    speaker: str
    text: str


@dataclass
class Transcript:
    path: Path
    raw: str
    header: str
    body: str
    turns: list[Turn] = field(default_factory=list)
    header_date: date | None = None

    @property
    def speakers(self) -> list[str]:
        return sorted({t.speaker for t in self.turns})


def normalize(text: str) -> str:
    """Lowercase, unify quotes/dashes, strip markdown emphasis, collapse whitespace."""
    text = unicodedata.normalize("NFC", text).lower()
    text = re.sub(r"[„”“\"«»]", '"', text)
    text = re.sub(r"[‘’‚`]", "'", text)
    text = re.sub(r"[–—]", "-", text)
    text = text.replace("*", "").replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_date(text: str) -> date | None:
    m = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    # "6 października 2026" / "6 October 2026"
    m = re.search(r"\b(\d{1,2})\.?\s+([a-ząćęłńóśźż]+)\s+(20\d{2})\b", text, re.I)
    if m and (month := _month(m[2])):
        return date(int(m[3]), month, int(m[1]))
    # "October 6, 2026"
    m = re.search(r"\b([a-z]+)\s+(\d{1,2}),?\s+(20\d{2})\b", text, re.I)
    if m and (month := _month(m[1])):
        return date(int(m[3]), month, int(m[2]))
    m = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](20\d{2})\b", text)
    if m:
        return date(int(m[3]), int(m[2]), int(m[1]))
    return None


def _month(word: str) -> int | None:
    w = word.lower()
    for stem, n in sorted(MONTHS.items(), key=lambda kv: -len(kv[0])):
        if w.startswith(stem):
            return n
    return None


def parse(path: Path) -> Transcript:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    # Split header/body at an explicit transcript heading if there is one.
    split_at = next((i for i, ln in enumerate(lines) if TRANSCRIPT_HEADING_RE.match(ln)), None)
    if split_at is not None:
        header, body_lines = "\n".join(lines[:split_at]), lines[split_at + 1 :]
    else:
        header, body_lines = "\n".join(lines[:15]), lines

    turns: list[Turn] = []
    for ln in body_lines:
        m = TURN_RE.match(ln)
        if m and not ln.lstrip().startswith(("-", "#", ">")):
            turns.append(Turn(len(turns), m[1].strip(), m[2].strip()))
        elif turns and ln.strip() and not ln.lstrip().startswith(("*[", "[", "#")):
            # continuation of the previous turn
            turns[-1].text += " " + ln.strip()

    return Transcript(
        path=path,
        raw=raw,
        header=header,
        body="\n".join(body_lines),
        turns=turns,
        header_date=find_date(header) or find_date(raw[:2000]),
    )
