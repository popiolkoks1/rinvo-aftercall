# Assumptions

Each entry says what was assumed, why, and what would change it. Add new entries at the bottom; don't renumber.

## Inputs

- **A1.** The brief (brief.pdf) is not committed; it was read at the start of the build session.
- **A2. One transcript covers one client call.** Calls with more than one client, and internal-only calls, are out of scope.
- **A3. Transcript format is loose.** Speaker turns may be `**Name:**`, `Name:`, `Speaker 1:` or missing. The parser tries to find speaker turns; if it can't, the transcript is treated as plain text and quote verification still works (only speaker attribution is lost). Header sections (context, participants) are used as metadata, and quotes taken from them are labelled `source: header`, not speech.
- **A4. Meeting date** is read from the transcript header when present. A `--meeting-date` CLI flag overrides it. If neither is available, the run fails rather than guessing.
- **A5. The vendor side is identified by config**, not by the LLM: `config/settings.yaml` lists the vendor's org names and email domains (`rinvo`, `rinvo.io`). Everyone else counts as the client side.
- **A6. Timezone is Europe/Warsaw** for all dates and the ICS output.

## Dates

- **A7. Relative dates are resolved against the meeting date, never against `--as-of`.** `--as-of` is used only to decide what is due or past due.
- **A8. Weeks run Monday to Sunday.** "This week" (*w tym tygodniu*) means due on the Friday of the meeting week. "Next week" (*w przyszłym tygodniu*) means due on the Friday of the following week. "Next Thursday" means the Thursday of the following week. "Not this month" means the earliest start is the 1st of the next month.
- **A9. The LLM resolves dates and code checks them.** The LLM returns the raw phrase plus an ISO date. Code then checks that any weekday named in the phrase matches the ISO date (for example "czwartek, piętnastego" → 2026-10-15 is a Thursday). A mismatch flags the item; it does not silently fix it.
- **A10. "Past due" means "past due, status unknown".** We have no data on what happened between calls, so a run with `--as-of` after a due date does not claim the work wasn't done. It only says the date has passed and nobody has recorded an outcome.

## Extraction and verification

- **A11. Quote verification shows that the quote exists in the transcript, not that it supports the item.** It uses fuzzy matching (rapidfuzz `partial_ratio`, after lowercasing, unifying quote characters and collapsing whitespace) against the transcript text. The UI says "quote found", not "verified".
- **A12. LLM `confidence` is shown but never used for gating.** It isn't calibrated. Routing and blocking decisions use only the quote-verification result, reconcile flags and the guardrail gate.
- **A13. The Gemini structured-output schema is kept flat:** one `Item` model with optional fields, no unions, dates as strings that Pydantic validates afterwards. This avoids response-schema limitations.
- **A14. Prompts contain no examples from the Auto Tama transcript.** If few-shot examples are needed, they come from an invented, unrelated call, so that eval results on Auto Tama aren't inflated by the examples.

## Routing, gate, drafts

- **A15. Guardrails and blackouts are scoped.** They don't block everything: each one carries scope tags (brand, feature, channel, recipient), the action kinds it forbids, an optional time window or release condition, and who can lift it. A blackout like "nothing new during my vacation" forbids `launch` and `enable` actions. It does not forbid investigating bugs or preparing drafts.
- **A16. The recap email goes only to the primary client contact** on the call, and only includes items marked `visibility: client`. Churn risk, sales signals, competitor information and internal billing notes are internal-only.
- **A17. Drafts must not add commitments.** Every date or promise in the recap must trace back to an item. A check flags any date in the draft that doesn't match an item date.
- **A18. Tentative meetings are not turned into calendar invites.** `followups.ics` holds reminders for our own actions only, not events with the client.
- **A19. The Linear CSV uses** `Title, Description, Priority, Labels, Status`. Description holds the evidence quotes and a link back to the run.

## Memory and state

- **A20. Client memory changes only when a human approves.** A run writes proposals to `runs/`. `aftercall approve` (CLI) or the Streamlit UI commits them. `--approve-all` exists for demos only.
- **A21. Item identity across calls** comes from the reconcile step, which may only reference IDs that already exist in client state (code validates this) or create new IDs. Re-running the same transcript must produce zero new items. This is the idempotency test.
- **A22. The cross-client product backlog** is `data/backlog.json`. When a client says "others ask for this too" (*nie jesteście pierwsi*), that is stored as a separate flag. It does not increase the request count.
- **A23. Streamlit Community Cloud storage is temporary and shared by everyone using the app.** Client memory there resets when the app restarts. That is acceptable for a demo; the local CLI is the source of truth.

## Added during the first build (2026-10-19)

- **A24. The Gemini thinking budget is capped at 8192 tokens, with output at 65536.** Thinking tokens count against the output limit, and without the cap the extraction JSON was cut off. A response that ends with `MAX_TOKENS` is treated as an error, not parsed.
- **A25. A second extraction pass ("what did the first pass miss?") is part of the pipeline.** It costs about 1 extra minute. It catches decisions not to act, small promises and contact rules, which the first pass misses. Duplicates it creates are left to reconcile.
- **A26. "Stitched" quotes are accepted only if every sentence in them appears verbatim** in the transcript. Such quotes are flagged `quote_stitched`. A quote containing an ellipsis passes only if each part is found.
- **A27. The gate's guardrail rules.**
  - A guardrail's scope never includes the person who can lift it ("only Kasia decides X" protects X, not every action involving Kasia).
  - Guardrails and blackouts are never routed as actions, whatever `action_kind` the LLM gave them.
  - Reconcile may not fold a guardrail into a non-guardrail item.
- **A28. A blackout forbids whatever action kinds the extractor assigned to it.** In the current run that includes `change_config`, so config changes during the 19–23 Oct vacation are blocked. That is the cautious reading of "nic nowego nie odpalajcie" (launch nothing new).
- **A29. The execution date used by the gate is max(as_of, earliest_start, due, meeting date).** A past-due item is evaluated as if it ran on `--as-of`.
- **A30. Eval matching.** For recall, an item matches a gold item if a found quote overlaps the gold anchor or sits within ±1 speaker turn of it (statement and reply belong together). Trap checks use the turn window only when they also filter by type. Every gold change made after a run is commented in the YAML.
- **A31. LLM responses are cached** under `.cache/llm`, keyed by model, prompt and schema. `--no-cache` forces new calls. Tests with stubbed responses must use their own cache directory, because one stub run did pollute the real cache.
