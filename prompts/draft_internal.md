Write internal notes for the team at {{vendor}} after a call with {{client}} ({{meeting_date}}). Write in English. These notes are never sent to the client.

1. `internal_note`: a short message for the team. Group it by who has to act: billing and invoices first (say what is wrong and what correction is needed), then anything else internal. Use concrete values from the items.
2. `meeting_brief`: only if a churn_risk item exists; otherwise null. It is a one-page brief to prepare for the next meeting with the client's decision-maker. Cover: the risk (what the competitor offers, as reported), what the decision-maker cares about, proof points we can show (success stories, with their usage restrictions), our known gaps (be honest), open commitments we must have delivered before the meeting, and the meeting status (confirmed or not).

Use ONLY the facts in the items. Mark anything uncertain as uncertain.

Items (JSON):
{{items}}
