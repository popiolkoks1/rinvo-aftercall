# aftercall · Grupa Auto Tama · call 2026-10-06 · as of 2026-10-19

47 items · 47 with a matching quote · 38 proposed actions · 6 blocked by the gate · recap to Kasia Malinowska (pl)

Gate: ✅ clear · ⛔ blocked · ⏳ waiting on dependency/condition · 🔑 needs client approval · 🕒 not before date

## Tickets → tickets.csv (5)
- ✅ `20261006-01` Agent intro does not allow client to interrupt
    - The virtual assistant's initial greeting and disclosure ("rozmowa jest nagrywana", "wirtualna asystentka") plays without a pause, preventing the client from speaking. The agent should allow for interruption before asking "przepraszam, jest pani w aucie?".
- ⏳ `20261006-04` Agent asks for model twice in one conversation
    - A client reported that the agent stopped responding to what they were saying and asked for the car model a second time during the conversation. No recording or specific number was provided by Ola.
    - _only if: Ola provides specific call details (number/recording)_
- ✅ `20261006-09` Agent redials numbers that disconnected within 3 seconds on the same day · due 2026-10-06, past due, status unknown
    - The agent is incorrectly redialing numbers that disconnected within 3 seconds on the same day. Six such cases were observed in one campaign in the afternoon, starting at 16:40, with one specific number ending in 14. This should not happen. The overall limit of 5 attempts should remain unchanged.
- ⏳ `20261006-17` Agent email to sales team is not clear
    - The email sent to the sales team after lead validation is a "wall of text" (transcription) and does not clearly highlight key information like the car model or dealership at the top. This makes it difficult for sales to quickly understand the lead's context.
    - _only if: Ola provides specific email/case number_
- ✅ `20261006-19` Dashboard filter for "interested" leads is broken · due 2026-10-06, past due, status unknown
    - The dashboard filter for "interested" leads does not correctly narrow down the list. When clicking on the "interested" tile (showing 9 leads), the system remains on the tile instead of displaying the filtered list. The list of contacts also shows all leads (received, not received, "bought elsewhere") instead of only interested ones. The date filter works correctly.

## Config / KB / launch checklist (5)
- ✅ `20261006-06` Update Włocławek dealership address in agent's knowledge base · due 2026-10-06, past due, status unknown
    - The agent currently states the Włocławek dealership is on Kapitulna street. This should be updated to Toruńska 120. The agent should state "Toruńska 120" for Włocławek.
- ✅ `20261006-07` Update Włocławek dealership hours in agent's knowledge base · due 2026-10-06, past due, status unknown
    - The agent should state the Włocławek dealership hours as "w tygodniu dziewiąta–osiemnasta, sobota dziewiąta–piętnasta". Toruń hours remain unchanged.
    - _amended within call; was: Update Włocławek dealership hours in agent's knowledge base | The agent should state the Włocławek dealership hours as "w tygodniu dziewiąta–osiemnasta, sobota dziewiąta–piętnasta". Toruń hours remain unchanged._
- ⛔ `20261006-10` Adjust agent calling hours · due 2026-10-06, past due, status unknown
    - Change agent calling hours to Monday-Friday 09:00-19:00 and Saturday 09:00-15:00. Sunday calling remains off. This is to align with dealership hours and avoid calls when the salon is closed.
- ⛔ `20261006-16` Launch agent for fresh leads for Peugeot and Citroën
    - Rinvo will launch the agent on the fresh leads file provided by Kasia for Peugeot and Citroën. The launch will not happen before Kasia sends the file. Old leads will not be re-processed. The launch is blocked during Kasia's vacation (2026-10-19 to 2026-10-23).
- ⛔ `20261006-21` Move "Nazwisko" column next to "Status" in contact list
    - In the contact list, the "Nazwisko" (Last Name) column should be moved to appear immediately after the "Status" column. This change should only be implemented if work is already being done on the contact list (e.g., fixing the filter).

## Product backlog (cross-client) (4)
- ⛔ `20261006-05` Implement A/B testing functionality in client panel
    - Allow clients to set up and manage A/B tests for different versions of conversation flows (e.g., intro text, question order) directly within the panel. The system should automatically split calls and display results, with "more full conversations" (with phone, model, and dealership confirmed) as the key success metric.
- ✅ `20261006-20` Implement click-through from dashboard tiles to filtered lists
    - Clicking on dashboard tiles (e.g., "interested" leads) should navigate the user to a filtered list displaying the corresponding leads. This functionality is currently missing.
- ✅ `20261006-22` Implement automated weekly email report for Paweł
    - Implement an automated weekly email report containing key metrics (calls made, calls answered, interested leads) to be sent to Paweł every Monday morning. This would save Kasia 30 minutes per week.
- 🔑 `20261006-28` Implement SMS fallback for unanswered calls
    - Implement a feature where the agent sends an SMS if a call is unanswered twice. The SMS would state something like "We called regarding your Peugeot inquiry, call back or click here." Kasia will provide the SMS content. This feature incurs separate costs per message.
    - _needs approval from Paweł_

## Follow-ups → followups.ics (14)
- ✅ `20261006-02` Remind Kasia Malinowska: Provide two versions of agent intro text for A/B testing (max 1 reminder) · due 2026-10-08, past due, status unknown
    - Kasia will provide two versions of the agent's introductory text. One version should be similar to the current one, and the second should be shorter but still include the virtual assistant's identity and recording disclosure.
- ⛔ `20261006-03` Configure A/B test for agent intro text · not before 2026-10-12
    - Rinvo will configure an A/B test using two versions of agent intro text provided by Kasia. The test will run for two days, either across both cities (Toruń and Włocławek) or split between them. The current week is excluded from launch.
- ⏳ `20261006-08` Notify Kasia when Włocławek address and hours are updated · due 2026-10-06, past due, status unknown
    - Marek will notify Kasia once the Włocławek dealership address and hours have been corrected in the agent's knowledge base. Kasia will then run a test herself.
    - _waiting on 20261006-06 'Update Włocławek dealership address in agent's knowledge base'; 20261006-07 'Update Włocławek dealership hours in agent's knowledge base'_
- ✅ `20261006-15` Remind Kasia Malinowska: Send file with fresh leads for Peugeot and Citroën (max 1 reminder) · due 2026-10-12, past due, status unknown
    - Kasia will send a file containing fresh leads from the last month (website and Facebook) for Peugeot and Citroën. These are leads that the sales team has not yet processed. Rinvo should not send a file template. The file should contain at least the phone number and city (Toruń or Włocławek). Old leads should not be re-processed.
- ⛔ `20261006-16` Launch agent for fresh leads for Peugeot and Citroën
    - Rinvo will launch the agent on the fresh leads file provided by Kasia for Peugeot and Citroën. The launch will not happen before Kasia sends the file. Old leads will not be re-processed. The launch is blocked during Kasia's vacation (2026-10-19 to 2026-10-23).
- ✅ `20261006-24` Remind Kasia Malinowska: Send assistance numbers and list of required fields for after-hours agent
    - Kasia will send a list of assistance numbers and required fields for the after-hours agent. This information is for Rinvo to hold internally and should not trigger any immediate development or launch of the after-hours agent.
- ✅ `20261006-25` Correct invoice for September from "Grupa Auto Tama sp. z o.o." to "Auto Tama Toruń sp. z o.o." · due 2026-10-16, past due, status unknown
    - The invoice for September was issued to "Grupa Auto Tama sp. z o.o.", but the contract is with "Auto Tama Toruń sp. z o.o.". A correction is required for accounting purposes.
- ✅ `20261006-26` Clarify billing policy for short calls and agent errors
    - Marek needs to check Rinvo's billing policy: whether calls are charged from the first second or for a started minute. Additionally, Rinvo needs to confirm if calls resulting from the agent's redialing bug (i9) will be deducted from the client's bill.
- ⏳ `20261006-27` Provide count of calls due to agent redialing bug and billing clarification
    - Marek will provide Kasia with the number of calls that occurred due to the agent redialing bug (i9) and clarify Rinvo's billing policy for short calls and agent errors (i26).
    - _waiting on 20261006-09 'Agent redials numbers that disconnected within 3 seconds on the same day'; 20261006-26 'Clarify billing policy for short calls and agent errors'_
- ✅ `20261006-29` Send SMS feature pricing and example text · due 2026-10-09, past due, status unknown
    - Marek will send Kasia the pricing for the SMS fallback feature (i28) and an example text for the SMS message. This is for Paweł's approval.
- ✅ `20261006-31` Chase confirmation (no invite until confirmed): Schedule a meeting with Paweł to discuss Rinvo's capabilities and CRM integration
    - Marek needs to schedule a 30-minute meeting with Paweł to discuss Rinvo's current capabilities, address concerns about CRM integration (which Rinvo does not currently offer in this quarter), and counter competitor claims. The proposed time is next Thursday, 2026-10-15, at 10:00, when Paweł is in Toruń. Kasia will confirm the meeting.
- ✅ `20261006-33` Prepare a cheat sheet for sales team on lead statuses
    - Rinvo will prepare a one-page cheat sheet explaining the meaning of different lead statuses ("zainteresowany", "oddzwonić", "niezweryfikowany") for the client's sales team. This will be sent to Kasia.
- ✅ `20261006-34` Chase confirmation (no invite until confirmed): Schedule online training for sales team on lead statuses
    - Rinvo will conduct a short (15-minute) online training session for the client's sales team to explain lead statuses. This training should only be scheduled after fresh leads are launched (i16), and Kasia will determine the exact date.
- ✅ `20261006-45` Issue corrected invoice for September · due 2026-10-16, past due, status unknown
    - Michał will issue a corrected invoice for September, changing the recipient from 'Grupa Auto Tama sp. z o.o.' to 'Auto Tama Toruń sp. z o.o.'. The correction should arrive next week.

## Internal notes → drafts/internal_notes.md (4)
- ✅ `20261006-12` Agent-qualified lead resulted in Peugeot 208 sale
    - A lead from July, previously untouched, was contacted by the agent on Friday, 2026-10-02, and the client purchased a Peugeot 208 on Saturday, 2026-10-03. This story can be used by Rinvo without the company name. Using the company name requires Paweł's approval.
- ✅ `20261006-25` Correct invoice for September from "Grupa Auto Tama sp. z o.o." to "Auto Tama Toruń sp. z o.o." · due 2026-10-16, past due, status unknown
    - The invoice for September was issued to "Grupa Auto Tama sp. z o.o.", but the contract is with "Auto Tama Toruń sp. z o.o.". A correction is required for accounting purposes.
- ✅ `20261006-30` Competitor VoiceDesk is being evaluated by Paweł
    - Paweł is evaluating a competitor, VoiceDesk, who claims to be 30% cheaper and offers CRM integration, which is a key interest for Paweł due to manual data entry by the sales team.
- ✅ `20261006-32` Present Peugeot 208 success story to Paweł during meeting
    - During the meeting with Paweł (i31), Marek should present the success story of the Peugeot 208 sale (i12) as evidence of Rinvo's value.

## Meeting brief → drafts/meeting_brief.md (5)
- ✅ `20261006-12` Agent-qualified lead resulted in Peugeot 208 sale
    - A lead from July, previously untouched, was contacted by the agent on Friday, 2026-10-02, and the client purchased a Peugeot 208 on Saturday, 2026-10-03. This story can be used by Rinvo without the company name. Using the company name requires Paweł's approval.
- ✅ `20261006-30` Competitor VoiceDesk is being evaluated by Paweł
    - Paweł is evaluating a competitor, VoiceDesk, who claims to be 30% cheaper and offers CRM integration, which is a key interest for Paweł due to manual data entry by the sales team.
- ✅ `20261006-31` Schedule a meeting with Paweł to discuss Rinvo's capabilities and CRM integration
    - Marek needs to schedule a 30-minute meeting with Paweł to discuss Rinvo's current capabilities, address concerns about CRM integration (which Rinvo does not currently offer in this quarter), and counter competitor claims. The proposed time is next Thursday, 2026-10-15, at 10:00, when Paweł is in Toruń. Kasia will confirm the meeting.
- ✅ `20261006-32` Present Peugeot 208 success story to Paweł during meeting
    - During the meeting with Paweł (i31), Marek should present the success story of the Peugeot 208 sale (i12) as evidence of Rinvo's value.
- ✅ `20261006-34` Schedule online training for sales team on lead statuses
    - Rinvo will conduct a short (15-minute) online training session for the client's sales team to explain lead statuses. This training should only be scheduled after fresh leads are launched (i16), and Kasia will determine the exact date.

## Client recap → drafts/recap_email.md (1)
- ✅ Send call recap to Kasia Malinowska · due 2026-10-06

## ⛔ Blocked by the gate (6)
- **Configure A/B test for agent intro text** (followup, change_config, would run 2026-10-19)
    - blocked by 20261006-36 'Blackout window for new launches during Kasia's vacation': forbids change_config on [all scopes] during 2026-10-19..2026-10-23 — "A, i od dziewiętnastego do dwudziestego trzeciego mam urlop. Cały tydzień."
- **Implement A/B testing functionality in client panel** (backlog, build, would run 2026-10-19)
    - blocked by 20261006-35 'Agent must not attempt to sell or offer used cars': forbids build on [conversation_flow] — "Nie sprzedaje. Jak ktoś mówi „już kupiłem” albo „rozmyśliłem się”, ma podziękować i się rozłączyć."
- **Adjust agent calling hours** (change_checklist, change_config, would run 2026-10-19)
    - blocked by 20261006-36 'Blackout window for new launches during Kasia's vacation': forbids change_config on [all scopes] during 2026-10-19..2026-10-23 — "A, i od dziewiętnastego do dwudziestego trzeciego mam urlop. Cały tydzień."
- **Launch agent for fresh leads for Peugeot and Citroën** (followup, launch, would run 2026-10-19)
    - blocked by 20261006-36 'Blackout window for new launches during Kasia's vacation': forbids launch on [all scopes] during 2026-10-19..2026-10-23 — "A, i od dziewiętnastego do dwudziestego trzeciego mam urlop. Cały tydzień."
- **Launch agent for fresh leads for Peugeot and Citroën** (change_checklist, launch, would run 2026-10-19)
    - blocked by 20261006-36 'Blackout window for new launches during Kasia's vacation': forbids launch on [all scopes] during 2026-10-19..2026-10-23 — "A, i od dziewiętnastego do dwudziestego trzeciego mam urlop. Cały tydzień."
- **Move "Nazwisko" column next to "Status" in contact list** (change_checklist, change_config, would run 2026-10-19)
    - blocked by 20261006-36 'Blackout window for new launches during Kasia's vacation': forbids change_config on [all scopes] during 2026-10-19..2026-10-23 — "A, i od dziewiętnastego do dwudziestego trzeciego mam urlop. Cały tydzień."

## Guardrails & blackouts captured (10)
- `20261006-11` Do not mark "on vacation" leads as uninterested · forbids [change_config] on [lead_qualification, status_management, sales_process]
- `20261006-14` Do not launch agent for Opel brand · forbids [launch] on [opel, brand_launch, campaign_settings] · lifted by Kasia Malinowska
- `20261006-35` Agent must not attempt to sell or offer used cars · forbids [build,change_config] on [agent_logic, sales_process, conversation_flow]
- `20261006-36` Blackout window for new launches during Kasia's vacation · forbids [launch,change_config] on [kasia, vacation, launch_freeze] · 2026-10-19..2026-10-23 · lifted by Kasia Malinowska
- `20261006-37` Do not enter agent settings during call · forbids [—] on [agent_settings]
- `20261006-41` Do not send file template for fresh leads · forbids [—] on [fresh_leads, file_template]
- `20261006-42` Do not re-process old leads · forbids [—] on [old_leads, agent_campaigns]
- `20261006-43` Do not contact Ola directly for lead validation email feedback · forbids [—] on [ola, communication, lead_validation_email]
- `20261006-44` Do not believe claims about after-hours agent launch without Kasia's confirmation · forbids [—] on [after_hours_agent, launch_approval, kasia]
- `20261006-46` Paweł must approve all features with separate costs · forbids [—] on [billing, feature_approval, pawel]

## Decisions — not doing / parked (4)
- `20261006-13` **parked** · Optimize agent calling times based on pickup rates
- `20261006-18` **parked** · Improve format of agent validation email to sales team
- `20261006-23` **parked** · Develop an agent for after-hours sales and service inquiries
- `20261006-38` **declined** · Do not send test recording for Włocławek address and hours update

## Superseded within the call (3)
- `20261006-39` ~~Do not change agent call attempt limit from five~~ → `20261006-09` Agent redials numbers that disconnected within 3 seconds on the same day
- `20261006-40` ~~Do not enable agent calling on Sundays~~ → `20261006-10` Adjust agent calling hours
- `20261006-47` ~~Provide SMS content for unanswered calls fallback~~ → `20261006-28` Implement SMS fallback for unanswered calls

## Needs a human check (0)

## Warnings
- reconcile: kept guardrail 20261006-41; refused supersession by waiting_on_client 20261006-15
- reconcile: kept guardrail 20261006-42; refused supersession by waiting_on_client 20261006-15
- reconcile: kept guardrail 20261006-44; refused supersession by waiting_on_client 20261006-24
- reconcile: kept guardrail 20261006-46; refused supersession by vendor_commitment 20261006-29
