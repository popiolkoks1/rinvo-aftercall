Write the follow-up email that {{vendor_person}} from {{vendor}} sends to {{recipient}} after today's call ({{meeting_date}}).

Rules:
- Write in language `{{language}}`, using the same register as the call (if they were on first-name terms, keep that).
- Keep it short and scannable: one greeting line, then brief sections — what we'll do (with dates), what we're waiting for from you, what we agreed NOT to do or to put on hold. Close with one line.
- Each item has `commitment`. Match the wording to it exactly:
  - `committed`: we will do it.
  - `will_look_into`: we'll check or look into it, and nothing more. Never "we'll fix it" or "we'll change it".
  - `no_commitment`: if you mention it at all, list it as noted, with no promise.
- Items of type guardrail / blackout_window and items with status declined / parked go only in the "not doing / on hold" section, one short line each. Leave out rules about our own internal process that the client doesn't need to hear.
- If several items say the same thing, write it once.
- Use ONLY the items below. Don't add promises, dates, prices or deadlines that aren't in the items. If an item has no date, give it none. Never write "soon" or "this quarter" when no date was given.
- Never mention competitors, prices other vendors offered, or the client considering alternatives, even if an item hints at it. Don't mention anything that isn't in the items: no competitors, no internal processes, no names of people who weren't on the call unless an item names them.
- Write dates the way a person would in that language (e.g. "do czwartku 8 października" / "by Thursday, 8 October"), never in ISO format. Leave out dates that are already in the past relative to the meeting date.
- Accuracy rules. These take precedence over everything above:
  - Never write a date the speaker didn't say. Use the speaker's own words for timing (e.g. "w tym tygodniu", "w przyszłym tygodniu"), even if an item has a resolved date.
  - Keep conditions word for word (e.g. "jeśli to nasz błąd"). Never drop an "if".
  - "Will look into" is never "will fix".
  - Parked or deferred is not declined. Never write "we won't do X" for something put on hold; write "wracamy do tego, gdy…" with the condition.
  - Every committed bug fix must appear under "what we'll do".
  - Leave out in-call remarks (e.g. what to click during screen sharing) and any statement about who can or cannot approve what.
  - Text the client said they will write themselves (e.g. SMS text, intro text) is theirs: never offer to send or write it.
  - At most 20 bullets in total.
- Plain text, no markdown headings. Lists with "-" are fine. Use real line breaks (`\n`) between the greeting, each section, each list item and the sign-off.

Items (JSON):
{{items}}

Before you answer, check the email against this list and fix it:
1. 20 bullets or fewer in total. Merge, and drop internal rules the client doesn't need.
2. Bug fixes and things we will check go under "what we'll do" (use "sprawdzimy" for will_look_into), never under "not doing".
3. No date that the speaker didn't say. Use their words ("w tym tygodniu", "w przyszłym tygodniu"). Don't invent start dates or "earliest" dates.
4. Every condition kept word for word ("jeśli to nasz błąd").
5. On hold = "wracamy do tego, gdy…", not "nie będziemy".
6. Nothing about who can or cannot approve what. No in-call remarks.
7. Text the client will write themselves (SMS, intro) is not something we send.
