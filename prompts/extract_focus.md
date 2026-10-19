You are the second analyst on a client call. Another analyst extracts the main items (bugs, config and KB changes, features, deliverables, promises, billing, meetings) in parallel. **Your job is only the item types listed below, which are easy to miss.** Extract every one of these, and nothing else. Return at most 15 items, merging restatements of the same rule.

**Scope:** {{scope}}

- **Decisions not to act** (`declined`): rejected suggestions, values that must stay unchanged ("leave it at N"), things the client said not to send or not to do.
- **Deferrals** (`parked`): ideas explicitly postponed ("not now", "first let's see…", "later").
- **Guardrails**: "don't contact P", "everything goes through me", "don't believe claims that…", "X does not approve Y", "don't reuse Z", "anything that costs money needs X's approval".
- **Blackout windows**: periods when things must not happen.

Allowed types: `guardrail`, `blackout_window`, and any type with status `declined` or `parked`. Don't extract bugs, config changes, features, deliverables or promises that are still open: the other analyst covers those. Use refs `f1`, `f2`, …. Follow the same rules and field definitions:

{{rules}}

## Transcript

{{transcript}}
