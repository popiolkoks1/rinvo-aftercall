# aftercall · Grupa Auto Tama · call 2026-10-06 · as of 2026-10-19

31 items · 30 with a matching quote · 28 proposed actions · 0 blocked by the gate · recap to Kasia Malinowska (pl)

Gate: ✅ clear · ⛔ blocked · ⏳ waiting on dependency/condition · 🔑 needs client approval · 🕒 not before date

## Tickets → tickets.csv (3)
- ⏳ `20261006-03` Investigate agent asking for model twice in one call
    - Investigate an issue where the agent reportedly asked for the car model twice in a single conversation, failing to respond to the client's input. Client did not provide a recording or phone number for this specific instance.
    - _only if: Client provides specific call details (recording/number)_
- ✅ `20261006-06` Investigate and fix agent calling twice after short hang-up
    - Investigate why the agent called a client twice on the same day after a hang-up within 3 seconds, despite a rule against it. Example: campaign, 16:40, number ending in 14. Fix the issue to prevent duplicate calls.
- ✅ `20261006-16` Fix dashboard filter for 'interested' leads
    - Investigate and fix the issue where clicking on the 'interested' leads tile or applying the 'interested' filter in the contacts list does not correctly narrow down the displayed list of leads.

## Config / KB / launch checklist (5)
- ⏳ `20261006-02` Configure and A/B test two agent intro versions · not before 2026-10-12
    - Configure two versions of the agent's introductory text provided by Kasia. One version will be as currently, the other shorter but still stating virtual assistant and recording. Deploy for two days or across Toruń and Włocławek. Do not deploy this week (before 2026-10-12).
    - _waiting on 20261006-01 'Receive two versions of agent intro text from Kasia'_
    - _only if: Kasia sends intro text versions_
- ✅ `20261006-05` Update Włocławek salon address to Toruńska 120 · due 2026-10-06, past due, status unknown
    - Correct the Włocławek salon address in the agent's knowledge base from Kapitulna to Toruńska 120. Operating hours remain 9:00-18:00 on weekdays and 9:00-15:00 on Saturdays. Toruń address is unchanged. Notify Kasia when updated.
    - _amended within call; was: Update Włocławek salon address to Toruńska 120 | Correct the Włocławek salon address in the agent's knowledge base from Kapitulna to Toruńska 120. Operating hours remain 9:00-18:00 on weekdays and 9:00-14:00 on Saturdays. Toruń address is unchanged. Notify Kasia when updated._
- ✅ `20261006-08` Adjust agent calling hours to weekdays 9-19, Saturday 9-15 · due 2026-10-06, past due, status unknown
    - Change the agent's calling hours to weekdays 9:00-19:00 and Saturdays 9:00-15:00. Sundays remain off. This updates the previous instruction for Saturday hours.
- ✅ `20261006-09` Update salon hours in agent knowledge base to Saturday 9-15 · due 2026-10-06, past due, status unknown
    - Update the salon operating hours provided by the agent to clients for both Toruń and Włocławek. Weekday hours remain 9:00-18:00, and Saturday hours should be changed to 9:00-15:00.
- ⏳ `20261006-18` Reorder contact list columns: last name after status
    - Adjust the column order in the contact list to place the 'last name' column immediately after the 'status' column. This will be done if work on the contact list is required for the filter fix (i16); otherwise, it will not be prioritized as a standalone task this week.
    - _waiting on 20261006-16 'Fix dashboard filter for 'interested' leads'_
    - _only if: Marek works on contact list for filter fix_

## Product backlog (cross-client) (1)
- 🔑 `20261006-24` Provide SMS pricing and example text for missed calls · due 2026-10-09, past due, status unknown
    - Provide Kasia with pricing information for sending SMS messages to clients who do not answer agent calls after two attempts. Also, provide an example SMS text. The content of the SMS will be written by Kasia, and any costs must be approved by Paweł.
    - _needs approval from Paweł_

## Follow-ups → followups.ics (10)
- ✅ `20261006-01` Remind Kasia Malinowska: Receive two versions of agent intro text from Kasia (max 1 reminder) · due 2026-10-08, past due, status unknown
    - Kasia will provide two versions of the agent's introductory text for A/B testing. The text should include the virtual assistant introduction and recording notification. Marek will remind Kasia once if not received by Thursday.
- ✅ `20261006-12` Remind Kasia Malinowska: Receive file with fresh leads from Kasia (max 1 reminder) · due 2026-10-12, past due, status unknown
    - Kasia will send a file containing fresh leads from the last month (website and Facebook). The file should include phone numbers and city (Toruń or Włocławek). Marek will send one reminder email if the file is not received by Monday. Do not use the old database again.
- ✅ `20261006-14` Remind Kasia Malinowska: Receive specific email example from Ola via Kasia
    - Kasia will forward an email from Ola (sales) that demonstrates a service inquiry being miscategorized as a sales lead. This is needed for Rinvo to investigate the agent's qualification process.
- ✅ `20261006-21` Remind Kasia Malinowska: Receive assistance numbers and field list for 'after hours' agent from Kasia
    - Kasia will send a list of assistance numbers and required data fields for the proposed 'after hours' agent. These details are for planning purposes and do not constitute approval for activation.
- ✅ `20261006-22` Issue corrected September invoice to 'Auto Tama Toruń sp. z o.o.' · due 2026-10-16, past due, status unknown
    - Issue a corrected invoice for September, changing the recipient from 'Grupa Auto Tama sp. z o.o.' to 'Auto Tama Toruń sp. z o.o.'. The corrected invoice is expected to be sent next week.
- ⏳ `20261006-23` Investigate billing for calls with short hang-ups and duplicate calls
    - Investigate whether calls with hang-ups within 3 seconds are being billed, and if so, whether they are billed per second or per started minute. If duplicate calls (i6) due to a bug are billed, these should be deducted from the client's invoice. Inform Kasia about the findings and the amount to be deducted.
    - _waiting on 20261006-06 'Investigate and fix agent calling twice after short hang-up'_
- ✅ `20261006-26` Chase confirmation (no invite until confirmed): Schedule meeting between Marek and Paweł to discuss Rinvo capabilities
    - Schedule a 30-minute meeting between Marek Rewoliński (Rinvo) and Paweł (Grupa Auto Tama) to discuss Rinvo's capabilities, particularly regarding CRM integration, and address Paweł's concerns raised by a competitor's presentation. The proposed time is next Thursday (October 15th) at 10:00, when Paweł is in Toruń. Kasia will confirm the meeting.
- ⏳ `20261006-27` Present Peugeot 208 success story during meeting with Paweł · due 2026-10-15, past due, status unknown
    - During the meeting with Paweł (i26), Marek will present the success story of the Peugeot 208 sale (i10) as evidence of Rinvo's value.
    - _waiting on 20261006-26 'Schedule meeting between Marek and Paweł to discuss Rinvo capabilities'_
    - _only if: Meeting with Paweł is confirmed_
- ✅ `20261006-28` Prepare status cheat sheet for sales team
    - Prepare a one-page cheat sheet explaining the meaning of different lead statuses ('interested', 'call back', 'unverified') for the client's sales team.
- ✅ `20261006-29` Chase confirmation (no invite until confirmed): Schedule online training for sales team on lead statuses
    - Schedule a 15-minute online training session for the client's sales team to explain lead statuses. This training should only occur after fresh leads are active, and Kasia will determine the exact date.

## Internal notes → drafts/internal_notes.md (4)
- ✅ `20261006-10` Document Peugeot 208 sale from old lead via bot
    - A client from Toruń, an old lead from July, purchased a Peugeot 208 on Saturday after a bot call on Friday. This can be used as a success story without the company name. Using the company name 'Grupa Auto Tama' requires Paweł's approval.
- ✅ `20261006-22` Issue corrected September invoice to 'Auto Tama Toruń sp. z o.o.' · due 2026-10-16, past due, status unknown
    - Issue a corrected invoice for September, changing the recipient from 'Grupa Auto Tama sp. z o.o.' to 'Auto Tama Toruń sp. z o.o.'. The corrected invoice is expected to be sent next week.
- ✅ `20261006-23` Investigate billing for calls with short hang-ups and duplicate calls
    - Investigate whether calls with hang-ups within 3 seconds are being billed, and if so, whether they are billed per second or per started minute. If duplicate calls (i6) due to a bug are billed, these should be deducted from the client's invoice. Inform Kasia about the findings and the amount to be deducted.
- ✅ `20261006-25` Client evaluating competitor VoiceDesk for lead bot services
    - The client is evaluating VoiceDesk, a competitor offering lead bot services. VoiceDesk claims to be ~30% cheaper and offers CRM integration, which is a key interest for Paweł as current lead data requires manual transcription.

## Meeting brief → drafts/meeting_brief.md (4)
- ✅ `20261006-10` Document Peugeot 208 sale from old lead via bot
    - A client from Toruń, an old lead from July, purchased a Peugeot 208 on Saturday after a bot call on Friday. This can be used as a success story without the company name. Using the company name 'Grupa Auto Tama' requires Paweł's approval.
- ✅ `20261006-25` Client evaluating competitor VoiceDesk for lead bot services
    - The client is evaluating VoiceDesk, a competitor offering lead bot services. VoiceDesk claims to be ~30% cheaper and offers CRM integration, which is a key interest for Paweł as current lead data requires manual transcription.
- ✅ `20261006-26` Schedule meeting between Marek and Paweł to discuss Rinvo capabilities
    - Schedule a 30-minute meeting between Marek Rewoliński (Rinvo) and Paweł (Grupa Auto Tama) to discuss Rinvo's capabilities, particularly regarding CRM integration, and address Paweł's concerns raised by a competitor's presentation. The proposed time is next Thursday (October 15th) at 10:00, when Paweł is in Toruń. Kasia will confirm the meeting.
- ✅ `20261006-29` Schedule online training for sales team on lead statuses
    - Schedule a 15-minute online training session for the client's sales team to explain lead statuses. This training should only occur after fresh leads are active, and Kasia will determine the exact date.

## Client recap → drafts/recap_email.md (1)
- ✅ Send call recap to Kasia Malinowska · due 2026-10-06

## ⛔ Blocked by the gate (0)
- nothing blocked

## Guardrails & blackouts captured (4)
- `20261006-11` Do not enable Opel for lead validation · forbids [enable] on [opel, lead_validation, kasia, paweł] · lifted by Kasia Malinowska
- `20261006-20` Do not activate 'after hours' agent without Kasia's confirmation · forbids [launch,enable] on [after_hours, agent_config, kasia] · lifted by Kasia Malinowska
- `20261006-30` Agent must not attempt to sell used cars or other products · forbids [build,enable] on [agent_behavior, sales_process]
- `20261006-31` Blackout window for new deployments during Kasia's vacation · forbids [launch,enable] on [deployments, kasia, vacation] · 2026-10-19..2026-10-23

## Decisions — not doing / parked (4)
- `20261006-04` **parked** · Implement self-service A/B testing for agent conversation flows
- `20261006-15` **parked** · Improve lead validation email format for sales team
- `20261006-17` **parked** · Enable clickable dashboard tiles to filter contact list
- `20261006-19` **parked** · Implement automated weekly email report for Paweł

## Superseded within the call (1)
- `20261006-07` ~~Adjust agent calling hours to weekdays 9-19, Saturday 9-14~~ → `20261006-08` Adjust agent calling hours to weekdays 9-19, Saturday 9-15

## Needs a human check (1)
- `20261006-13` Do not use old lead database again · quote_not_found
    - quote not in transcript: "Starej bazy drugi raz nie puszczajcie. [...] Starej bazy drugi raz nie puszczam"

