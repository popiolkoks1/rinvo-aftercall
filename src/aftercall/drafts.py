"""Draft generation and the checks that keep drafts honest."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from . import config, llm
from .models import DraftOut, InternalDraftsOut, Item, ItemType, Visibility

POLISH_MONTHS = ["stycz", "lut", "mar", "kwie", "maj", "czerw", "lip", "sierp", "wrze", "paźdz", "listop", "grud"]
EN_MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def _payload(items: list[Item]) -> str:
    return json.dumps(
        [
            {
                "type": i.type.value,
                "title": i.title,
                "detail": i.detail,
                "owner": f"{i.owner_side.value}:{i.owner_person or ''}",
                "commitment": i.vendor_commitment_level.value,
                "status": i.status.value,
                "due": i.due,
                "earliest_start": i.earliest_start,
                "trigger": i.trigger_condition,
                "approver": i.approver,
            }
            for i in items
        ],
        ensure_ascii=False,
        indent=1,
    )


def generate(
    items: list[Item],
    client: str,
    recipient: str,
    vendor_person: str,
    language: str,
    meeting_date: date,
    use_cache: bool = True,
) -> tuple[DraftOut, InternalDraftsOut, list[str]]:
    vendor = ", ".join(config.settings()["vendor"]["org_names"])
    # The leak guard is here, in code: the recap prompt never sees internal items.
    client_items = [i for i in items if i.visibility == Visibility.client and i.type not in config_internal_types()]
    internal_items = [i for i in items if i not in client_items or i.type == ItemType.billing]

    with ThreadPoolExecutor(max_workers=2) as pool:
        recap_f = pool.submit(
            llm.generate, "draft_recap", DraftOut, use_cache,
            vendor=vendor, vendor_person=vendor_person, recipient=recipient,
            meeting_date=meeting_date.isoformat(), language=language, items=_payload(client_items),
        )
        internal_f = pool.submit(
            llm.generate, "draft_internal", InternalDraftsOut, use_cache,
            vendor=vendor, client=client, meeting_date=meeting_date.isoformat(), items=_payload(internal_items),
        )
        recap, internal = recap_f.result(), internal_f.result()

    flags = check_recap(recap, client_items, internal_items, meeting_date)
    leaks = [f for f in flags if f.startswith("possible leak")]
    if leaks:  # one retry, telling the model exactly what it must not say
        recap = llm.generate(
            "draft_recap", DraftOut, use_cache,
            vendor=vendor, vendor_person=vendor_person, recipient=recipient,
            meeting_date=meeting_date.isoformat(), language=language,
            items=_payload(client_items) + "\n\nYOUR PREVIOUS DRAFT WAS REJECTED. Do not mention: "
            + "; ".join(leaks),
        )
        flags = check_recap(recap, client_items, internal_items, meeting_date)
        flags.insert(0, f"recap regenerated once because of: {'; '.join(leaks)}")
    return recap, internal, flags


def config_internal_types() -> set[ItemType]:
    return {ItemType(t) for t in config.taxonomy().get("internal_types", [])}


def check_recap(recap: DraftOut, client_items: list[Item], internal_items: list[Item], meeting_date: date) -> list[str]:
    text = f"{recap.subject}\n{recap.body}".lower()
    flags: list[str] = []

    # 1. Internal-only terms that leaked: tags of internal items not shared with client items.
    client_tags = {t.lower() for i in client_items for t in i.scope_tags}
    for i in internal_items:
        for tag in i.scope_tags:
            word = tag.lower().replace("_", " ")
            if tag.lower() not in client_tags and len(word) > 3 and re.search(r"\b" + re.escape(word) + r"\b", text):
                flags.append(f"possible leak: internal term '{word}' (from {i.id} '{i.title}')")

    # 1b. Configured leak words, and capitalised names that only internal items mention.
    for term in config.settings().get("recap", {}).get("leak_terms", []):
        if term.lower() in text:
            flags.append(f"possible leak: '{term}'")
    client_text = " ".join(f"{i.title} {i.detail}" for i in client_items).lower()
    for i in internal_items:
        if i.type in config_internal_types():
            for name in set(re.findall(r"\b[A-Z][a-zA-Z]{3,}[A-Z][a-zA-Z]+\b|\b[A-Z]{3,}\b", f"{i.title} {i.detail}")):
                if name.lower() in text and name.lower() not in client_text:
                    flags.append(f"possible leak: internal name '{name}' (from {i.id})")

    # 2. Dates that no item backs.
    known = {(meeting_date.month, meeting_date.day)}
    for i in client_items:
        for v in (i.due, i.earliest_start, i.window_start, i.window_end):
            if v:
                known.add((int(v[5:7]), int(v[8:10])))
        for m in re.finditer(r"\b20\d{2}-(\d{2})-(\d{2})\b", i.detail):  # dates stated in the detail text
            known.add((int(m[1]), int(m[2])))
    for m in re.finditer(r"\b(\d{1,2})[./](\d{1,2})\b", text):
        d, mo = int(m[1]), int(m[2])
        if 1 <= mo <= 12 and (mo, d) not in known:
            flags.append(f"date not backed by any item: '{m[0]}'")
    for m in re.finditer(r"\b(\d{1,2})\.?\s+([a-ząćęłńóśźż]{3,})", text):
        word = m[2]
        mo = next((n + 1 for n, s in enumerate(POLISH_MONTHS) if word.startswith(s)), None) or next(
            (n + 1 for n, s in enumerate(EN_MONTHS) if word.startswith(s)), None
        )
        if mo and (mo, int(m[1])) not in known:
            flags.append(f"date not backed by any item: '{m[0]}'")
    return flags
