"""File outputs. Each writer stands in for a real integration (Linear, Calendar, Gmail)."""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from ..models import Action, Item

PRIORITY = {"bug": "High", "config_change": "Medium", "knowledge_base_fix": "High"}


def tickets_csv(path: Path, actions: list[Action], items: dict[str, Item]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Title", "Description", "Priority", "Labels", "Status"])
        for a in actions:
            i = items[a.item_id]
            quotes = "\n".join(f'> "{e.quote}"' for e in i.evidence if e.found)
            gate = f"\n\nGate: {a.gate.status} — " + "; ".join(a.gate.reasons) if a.gate and a.gate.reasons else ""
            w.writerow([
                i.title,
                f"{i.detail}\n\nEvidence:\n{quotes}{gate}\n\naftercall item {i.id}",
                PRIORITY.get(i.type.value, "Medium"),
                ",".join(i.scope_tags),
                "Triage" if i.vendor_commitment_level.value == "will_look_into"
                else "Todo" if (not a.gate or a.gate.status == "clear") else "Backlog",
            ])


def _ics_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    out, b = [], line.encode()
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:  # don't split a UTF-8 sequence
            cut -= 1
        out.append(b[:cut].decode())
        b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)


def followups_ics(path: Path, actions: list[Action], as_of: date, tz: str) -> None:
    """Reminders for OUR follow-ups. Never events with the client (see ASSUMPTIONS A18)."""
    stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//aftercall//EN", "CALSCALE:GREGORIAN"]
    for a in actions:
        day = date.fromisoformat(a.gate.exec_date) if a.gate and a.gate.exec_date else as_of
        status = a.gate.status if a.gate else "clear"
        desc = "; ".join(a.gate.reasons) if a.gate else ""
        lines += [
            "BEGIN:VEVENT",
            f"UID:{a.id.replace('/', '-')}@aftercall",
            f"DTSTAMP:{stamp}",
            f"DTSTART;TZID={tz}:{day:%Y%m%d}T090000",
            f"DTEND;TZID={tz}:{day:%Y%m%d}T091500",
            _fold(f"SUMMARY:{_ics_escape(('[' + status.upper() + '] ' if status != 'clear' else '') + a.title)}"),
            _fold(f"DESCRIPTION:{_ics_escape(desc or 'aftercall follow-up')}"),
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
