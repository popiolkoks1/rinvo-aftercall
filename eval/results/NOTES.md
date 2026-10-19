# Eval history: auto-tama (one run each, gemini-2.5-flash; LLM variance not measured)

| run | change | recall | traps |
|---|---|---|---|
| 1 | baseline: single pass | 17/29 (59%) | 13/14 |
| 2 | + second "omissions" pass, prompt rules, ±1-turn matching | 15/29 (52%) | 12/15 |
| 3 | + stitched-quote verification, lifter not in guardrail scope, `g*` dedupe hint | 27/29 (93%) | 12/15 → 14/15 after 3 trap spec fixes |
| 4–5 | + reconcile can't fold guardrails, guardrails never routed, recap date check reads detail dates | 28/29 (97%) | 14/15 |

Run 2 dropped because the model started stitching quotes across turns. Verification rejected 13 real items.

Known misses in run 5:
- `ola_case`: Kasia forwarding Ola's case was folded into a bug item, so there is no `waiting_on_client` item for it.
- `saturday_is_15`: the KB-hours item says "Toruń hours remain unchanged", but Kasia said Saturday 9–15 applies to **both** salons. This is a real error, and it is in the recap too.

Not covered by any trap:
- Bug `20261006-01` (intro can't be interrupted) is a ticket, and the recap says "we'll fix it". Marek only offered to *look into* shortening the intro, after the call.
- The invoice correction appears twice (`-25`, `-45`).
- The self-serve A/B panel feature is blocked by the "agent must not sell" guardrail, because both are tagged `conversation_flow`. This is a false positive.
