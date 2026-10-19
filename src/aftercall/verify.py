"""Deterministic checks on LLM output: quotes exist, dates are sane."""

from __future__ import annotations

import re

from rapidfuzz import fuzz

from . import config
from .dates import parse_iso, weekday_mismatch
from .models import EvidenceCheck, Item
from .transcript import Transcript, normalize


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
ELISION_RE = re.compile(r"\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…)\s*")


def check_quote(quote: str, t: Transcript, threshold: float) -> EvidenceCheck:
    """A quote with an elision ("a [...] b") passes only if every part is found."""
    parts = [p for p in ELISION_RE.split(quote) if len(normalize(p)) >= 8]
    if len(parts) > 1:
        checks = [_check_one(p, t, threshold) for p in parts]
        first = checks[0]
        return EvidenceCheck(
            quote=quote, found=all(c.found for c in checks), score=min(c.score for c in checks),
            speaker=first.speaker, turn=first.turn, source=first.source,
        )
    single = _check_one(quote, t, threshold)
    if single.found:
        return single
    # Stitched quote: sentences from different places joined together. Accept only if every
    # sentence exists verbatim; mark it so the reviewer knows the quote isn't one span.
    sentences = [s for s in SENTENCE_RE.split(quote) if len(normalize(s)) >= 8]
    if len(sentences) > 1:
        checks = [_check_one(s, t, threshold) for s in sentences]
        if all(c.found for c in checks):
            first = checks[0]
            return EvidenceCheck(quote=quote, found=True, score=min(c.score for c in checks),
                                 speaker=first.speaker, turn=first.turn, source="stitched")
    return single


def _check_one(quote: str, t: Transcript, threshold: float) -> EvidenceCheck:
    q = normalize(quote)
    if len(q) < 8:
        return EvidenceCheck(quote=quote, found=False, score=0.0)

    best_turn, best_turn_score = None, 0.0
    for turn in t.turns:
        s = fuzz.partial_ratio(q, normalize(turn.text))
        if s > best_turn_score:
            best_turn, best_turn_score = turn, s

    if best_turn and best_turn_score >= threshold:
        return EvidenceCheck(quote=quote, found=True, score=best_turn_score, speaker=best_turn.speaker,
                             turn=best_turn.index, source="speech")

    # Fallback: whole document (no parsed turns, header facts, quotes spanning turns).
    s_header = fuzz.partial_ratio(q, normalize(t.header))
    s_all = fuzz.partial_ratio(q, normalize(t.raw))
    score = max(s_all, best_turn_score)
    if score >= threshold:
        source = "header" if s_header >= threshold else "speech"
        turn = best_turn.index if best_turn and source == "speech" else None
        return EvidenceCheck(quote=quote, found=True, score=score, turn=turn, source=source)
    return EvidenceCheck(quote=quote, found=False, score=score)


def verify_items(items: list[Item], t: Transcript) -> None:
    threshold = config.settings()["verify"]["quote_threshold"]
    for item in items:
        item.evidence = [check_quote(q, t, threshold) for q in item.evidence_quotes]
        if not item.evidence:
            item.flags.append("no_evidence")
        elif not any(e.found for e in item.evidence):
            item.flags.append("quote_not_found")
        elif not all(e.found for e in item.evidence):
            item.flags.append("some_quotes_not_found")
        if any(e.source == "stitched" for e in item.evidence):
            item.flags.append("quote_stitched")

        for field in ("due", "earliest_start", "window_start", "window_end"):
            raw = getattr(item, field)
            if raw and not parse_iso(raw):
                item.flags.append(f"bad_date:{field}={raw}")
                setattr(item, field, None)
        for phrase_field, iso_field in (("due_phrase", "due"), ("earliest_start_phrase", "earliest_start")):
            if msg := weekday_mismatch(getattr(item, phrase_field), getattr(item, iso_field)):
                item.flags.append(f"weekday_mismatch: {msg}")
