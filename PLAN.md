# aftercall — build plan

## Repo layout

```
aftercall/
├── pyproject.toml              # uv; entry point `aftercall = aftercall.cli:app`
├── .env.example                # GEMINI_API_KEY, GEMINI_MODEL
├── README.md  ASSUMPTIONS.md  PLAN.md
├── config/
│   ├── settings.yaml           # vendor org names/domains, timezone, fuzzy threshold, cache on/off
│   └── taxonomy.yaml           # type -> routes[], default visibility, default approver side
├── prompts/
│   ├── extract.md
│   ├── reconcile.md
│   ├── draft_recap.md
│   ├── draft_internal.md
│   └── draft_brief.md          # meeting brief when churn_risk exists
├── src/aftercall/
│   ├── cli.py                  # Typer: run, approve, eval, client show
│   ├── pipeline.py             # the ONE pipeline; CLI and UI both call this
│   ├── models.py               # Item, Guardrail, Action, ClientState, Run
│   ├── transcript.py           # header metadata, speaker turns, normalised text
│   ├── dates.py                # weekday consistency check, overdue calc (as_of)
│   ├── llm.py                  # google-genai wrapper, response cache keyed by hash(prompt+input+model)
│   ├── extract.py
│   ├── verify.py               # rapidfuzz quote check + speaker check
│   ├── reconcile.py            # within-call supersession, then vs. client state
│   ├── route.py                # taxonomy.yaml -> actions
│   ├── gate.py                 # deterministic guardrail/blackout check
│   ├── drafts.py               # LLM drafts + "no invented dates / no internal leakage" checks
│   ├── memory.py               # data/clients/<slug>.json, backlog.json
│   ├── writers/                # tickets_csv.py, ics.py, markdown.py
│   └── adapters/base.py        # TicketSink / EmailSink / CalendarSink protocols, File* impls
├── app/streamlit_app.py        # thin UI over pipeline.py
├── data/clients/  data/backlog.json
├── samples/
│   ├── auto-tama_2026-10-06.md         # the given transcript
│   └── synthetic_<other-client>.md     # our own second call, different format/language
├── eval/
│   ├── gold/auto-tama.yaml
│   ├── gold/<synthetic>.yaml
│   └── (eval logic lives in src/aftercall/eval.py, exposed as `aftercall eval`)
├── tests/                      # dates, verify, gate, transcript parser — no LLM
└── runs/                       # gitignored
```

## CLI

```
aftercall run <transcript> --client <slug> [--meeting-date YYYY-MM-DD] [--as-of YYYY-MM-DD] [--no-cache] [--approve-all]
aftercall approve runs/<dir> [--ids a,b,c | --all]
aftercall eval [--client auto-tama]
aftercall client show <slug>
```

## Build order

Each step ends with something runnable. Steps 1–9 are the end-to-end CLI; the UI comes after.

1. **Scaffold.** uv project, Typer skeleton, settings loader, `.env`, `llm.py` with cache. Run `aftercall run` and confirm it echoes the parsed metadata.
2. **Transcript parser and dates.** Speaker turns, header metadata (date, participants), normalised text. Write unit tests for both the Auto Tama format and a plain `Speaker 1:` format.
3. **Extract.** Models, `prompts/extract.md`, Gemini structured output. Write `items.json`. Read the raw output once by hand.
4. **Verify.** Quote and speaker checks. Unverified items get `flags: [quote_not_found]`.
5. **Gold and eval, before tuning anything.** Write `eval/gold/auto-tama.yaml` (must-catch items and traps), run `aftercall eval`, and record the baseline recall and trap results. Every prompt change after this point is measured.
6. **Reconcile within the call.** Supersession (Saturday 14:00 → 15:00 in both calling hours and salon hours), and items linked to each other.
7. **Route, gate and writers.** `taxonomy.yaml` produces actions, the gate blocks or clears them, and the writers produce `tickets.csv`, `followups.ics`, `checklist.md`.
8. **Drafts.** Client recap in the transcript's language, internal notes, and a meeting brief. Add the leakage check and the invented-date check.
9. **Memory.** `approve` commits to client state. Reconcile against state. Idempotency test: running the same transcript twice gives 0 new items. **The CLI is end-to-end at this point.**
10. **Second synthetic transcript** (different client, different speaker format, ideally English). Run the pipeline and the eval on it to show nothing is specific to Auto Tama.
11. **Streamlit UI** over `pipeline.py`: upload, choose client, sections per route plus blocked and superseded items, approve/edit/reject.
12. **Deploy and README.** Community Cloud, `st.secrets`, a simple password gate so the Gemini key isn't open to the public, and a short demo script.

## Decisions from the design review (accepted 2026-10-19)

**Item schema**
- Replace `due date OR trigger` with separate fields: `earliest_start`, `due`, `trigger_condition`, `depends_on[]`. Each date keeps its raw phrase (`due_phrase`, `earliest_start_phrase`) so code can check the weekday.
- New statuses `declined` and `parked` mark non-actions. They are stored in memory and listed under "Decisions", but never routed.
- The extractor sets `superseded_by_ref` when a later statement in the call replaces an earlier one. Reconcile adds anything it missed, and can also *amend* an item when a change only partly replaces it (one change can affect items of different types, e.g. calling hours and salon hours).
- New fields: `visibility: client|internal`, `scope_tags[]`, `action_kind`, `related_refs[]`, `demand_signal`.
- Guardrails and blackouts carry `forbids_action_kinds[]`, `scope_tags[]`, `window_start/end`, `lifted_by`.
- Two types added: `question_to_answer` (we owe the client an answer) and `meeting_request` (a tentative meeting; it creates a "chase confirmation" follow-up, never an invite).

**Routing and gate**
- One item can produce several actions. `taxonomy.yaml` maps a type to a list of routes, and an `action_kind` can add routes too (e.g. `launch` → change checklist).
- The gate is deterministic and runs on *actions*. An action is checked against each guardrail on: action kind ∈ forbidden kinds, scope tags overlap (or the guardrail has no tags), and execution date inside the window. Execution date = max(as_of, earliest_start, action date).
- Results other than blocked: `waiting` (has `depends_on` or a trigger condition), `needs_approval` (has an approver), `not_before` (earliest_start is later than as_of).
- Per-person authority is stored in memory (`can_approve` / `cannot_approve` scope tags). If the approver lacks authority for an action, it is flagged.

**Drafts**
- Only client-visible items are given to the recap prompt; this filtering is done in code. Afterwards, checks flag internal terms that appear in the recap, and any dates in it that don't match an item date.

**Robustness**
- LLM responses are cached by input hash. `--client` is optional; without it, the slug is derived from the client name that extraction finds. The meeting date flag is `--date`, with `--meeting-date` as an alias.
- The sample transcript stays at the repo root, as provided (`transkrypcja-spotkanie.md`).
