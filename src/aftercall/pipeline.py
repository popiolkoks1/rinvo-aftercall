"""The one pipeline. CLI and UI both call `run()`."""

from __future__ import annotations

import json
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import config, drafts, llm, gate, memory, postprocess, reconcile, report, route, transcript, verify
from .extract import extract_all
from .models import Action, ClientState, DraftOut, InternalDraftsOut, Item, ItemType, Person, Side


@dataclass
class RunResult:
    run_dir: Path
    transcript_path: Path
    slug: str
    client_name: str
    meeting_date: date
    as_of: date
    language: str
    primary_contact: str
    people: list[Person]
    items: list[Item]
    actions: list[Action]
    recap: DraftOut | None = None
    internal: InternalDraftsOut | None = None
    draft_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(sp|z|o|oo|s\.?a|gmbh|ltd|inc|llc|grupa|group)\b\.?", " ", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "client"


def _fix_sides(people: list[Person]) -> None:
    """Vendor side comes from config (email domain / org name), not from the LLM."""
    domains = [d.lower() for d in config.settings()["vendor"]["email_domains"]]
    for p in people:
        if p.email and any(p.email.lower().endswith("@" + d) for d in domains):
            p.side = Side.vendor


def run(
    transcript_path: Path,
    client_slug: str | None = None,
    meeting_date: date | None = None,
    as_of: date | None = None,
    use_cache: bool = True,
    log=print,
) -> RunResult:
    t = transcript.parse(transcript_path)
    meeting_date = meeting_date or t.header_date
    if not meeting_date:
        raise ValueError("No meeting date found in the transcript header; pass --date YYYY-MM-DD")
    if t.header_date and t.header_date != meeting_date:
        log(f"! --date {meeting_date} differs from the header date {t.header_date}; using --date")
    as_of = as_of or date.today()
    log(f"· parsed {transcript_path.name}: {len(t.turns)} turns, speakers {', '.join(t.speakers) or '(none found)'}")

    clock = time.perf_counter()
    lap = lambda: f"{time.perf_counter() - clock:.0f}s"
    log("· extracting (parallel Gemini calls)…")
    ex = extract_all(t, meeting_date, use_cache, log)
    people = [Person(**p.model_dump()) for p in ex.people]
    _fix_sides(people)

    slug = client_slug or slugify(ex.client_name)
    state = memory.load(slug)
    warnings: list[str] = []
    if state.client_name and slugify(state.client_name) != slugify(ex.client_name):
        warnings.append(f"client '{ex.client_name}' in transcript doesn't match stored '{state.client_name}' for slug {slug}")

    # Stable ids: <meeting date>-<nn>. Remap refs so depends_on etc. keep working.
    items: list[Item] = []
    seen: set[str] = set()
    for n, out in enumerate(ex.items, 1):
        item = Item(**out.model_dump(), id=f"{meeting_date:%Y%m%d}-{n:02d}")
        if out.ref.startswith("f"):
            item.flags.append("found in focus pass")
        if item.ref in seen:
            item.ref = f"{item.ref}_{n}"
        seen.add(item.ref)
        items.append(item)
    log(f"· [{lap()}] {len(items)} items extracted; verifying quotes, merging duplicates…")
    verify.verify_items(items, t)
    postprocess.validate_areas(items)
    warnings += postprocess.dedupe(items)

    log(f"· [{lap()}] reconciling (Gemini)…")
    warnings += reconcile.reconcile(items, state, t, use_cache)
    items += postprocess.synthesize_waiting(items, f"{meeting_date:%Y%m%d}")
    warnings += postprocess.check_commitments(items, people, t)
    warnings += postprocess.enforce_lift_authority(items, people)
    by_ref = {i.ref: i for i in items}
    for i in items:
        if i.superseded_by_ref and i.superseded_by_ref not in by_ref:
            i.flags.append(f"unknown superseded_by_ref {i.superseded_by_ref}")
            i.superseded_by_ref = None

    # Route + gate. Guardrails come from this call and from memory.
    primary = ex.primary_client_contact
    actions = route.build_actions(items, primary)
    actions.append(route.recap_action(meeting_date.isoformat(), primary))
    guards = gate.active_guardrails(items) + gate.active_guardrails(
        [i for i in state.items if i.id not in {x.id for x in items}]
    )
    by_id = {i.id: i for i in items}
    all_people = people + [p for p in state.people if p.name.lower() not in {x.name.lower() for x in people}]
    for a in actions:
        a.gate = gate.check(a, by_id.get(a.item_id), guards, by_ref, all_people, as_of, meeting_date, primary)

    result = RunResult(
        run_dir=config.path("runs") / f"{meeting_date.isoformat()}_{slug}",
        transcript_path=transcript_path.resolve(),
        slug=slug,
        client_name=ex.client_name,
        meeting_date=meeting_date,
        as_of=as_of,
        language=ex.language,
        primary_contact=primary,
        people=people,
        items=items,
        actions=actions,
        warnings=warnings,
    )

    log(f"· [{lap()}] drafting recap + internal notes (parallel Gemini calls)…")
    vendor_person = next((p.name for p in people if p.side == Side.vendor and p.present_on_call), "")
    active = [i for i in items if i.active]
    result.recap, result.internal, result.draft_flags = drafts.generate(
        active, ex.client_name, primary, vendor_person, ex.language, meeting_date, use_cache
    )
    if not any(i.type == ItemType.churn_risk for i in active):
        result.internal.meeting_brief = None

    write(result)
    log(f"· [{lap()}] done · uncached Gemini calls: " + (", ".join(f"{n} {s}s" for n, s in llm.timings) or "none"))
    return result


def write(r: RunResult) -> None:
    from .writers import files

    d = r.run_dir
    (d / "drafts").mkdir(parents=True, exist_ok=True)
    items_by_id = {i.id: i for i in r.items}

    (d / "items.json").write_text(json.dumps({
        "client": r.client_name, "slug": r.slug, "meeting_date": r.meeting_date.isoformat(),
        "as_of": r.as_of.isoformat(), "transcript": str(r.transcript_path), "language": r.language, "primary_contact": r.primary_contact,
        "people": [p.model_dump(mode="json") for p in r.people],
        "items": [i.model_dump(mode="json") for i in r.items],
        "actions": [a.model_dump(mode="json") for a in r.actions],
        "draft_flags": r.draft_flags, "warnings": r.warnings,
    }, ensure_ascii=False, indent=2))

    files.tickets_csv(d / "tickets.csv", [a for a in r.actions if a.route == "ticket"], items_by_id)
    files.followups_ics(
        d / "followups.ics", [a for a in r.actions if a.route == "followup"], r.as_of, config.settings()["timezone"]
    )
    if r.recap:
        (d / "drafts" / "recap_email.md").write_text(
            f"To: {r.primary_contact}\nSubject: {r.recap.subject}\n\n{r.recap.body}\n"
            + ("\n---\nChecks:\n" + "\n".join(f"- {f}" for f in r.draft_flags) + "\n" if r.draft_flags else "")
        )
    if r.internal:
        (d / "drafts" / "internal_notes.md").write_text(f"# {r.internal.internal_note.subject}\n\n{r.internal.internal_note.body}\n")
        if r.internal.meeting_brief:
            (d / "drafts" / "meeting_brief.md").write_text(f"# {r.internal.meeting_brief.subject}\n\n{r.internal.meeting_brief.body}\n")
    (d / "report.md").write_text(report.render(r))
    from . import html_report

    html_report.build(d)


def approve(run_dir: Path, ids: list[str] | None) -> dict:
    data = json.loads((run_dir / "items.json").read_text())
    items = [Item.model_validate(i) for i in data["items"]]
    if ids:
        chosen = [i for i in items if i.id in set(ids)]
    else:  # --all: everything that is verified and not superseded
        chosen = [i for i in items if i.active]
    state = memory.load(data["slug"])
    state.client_name = state.client_name or data["client"]
    people = [Person.model_validate(p) for p in data["people"]]
    return memory.commit(state, chosen, people, {"meeting_date": data["meeting_date"], "run": str(run_dir)})
