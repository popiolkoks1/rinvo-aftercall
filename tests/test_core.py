from datetime import date
from pathlib import Path

from aftercall.dates import weekday_mismatch
from aftercall.gate import check
from aftercall.models import Action, ActionKind, EvidenceCheck, Item
from aftercall.transcript import Transcript, find_date, parse
from aftercall.verify import check_quote


def _item(**kw) -> Item:
    base = dict(
        ref="i1", type="config_change", title="t", detail="d", owner_side="vendor", owner_person=None,
        status="open", action_kind="launch", product_area="other", new_for_end_customers=False,
        client_requested=False, vendor_commitment_level="committed", blocked_on_input=None, blocked_on_person=None,
        scope_tags=[], visibility="client", due_phrase=None, due=None,
        earliest_start_phrase=None, earliest_start=None, trigger_condition=None, depends_on=[], related_refs=[],
        superseded_by_ref=None, approver=None, max_reminders=None, forbids_action_kinds=[], window_start=None,
        window_end=None, lifted_by=None, applies_to_all_work=False, demand_signal=False, evidence_quotes=["x"], confidence=0.9, id="a-01",
        evidence=[EvidenceCheck(quote="x", found=True, score=100)],
    )
    base.update(kw)
    return Item(**base)


def test_dates():
    assert find_date("6 października 2026 (wtorek)") == date(2026, 10, 6)
    assert find_date("Call on October 6, 2026") == date(2026, 10, 6)
    assert weekday_mismatch("czwartek, piętnastego", "2026-10-15") is None
    assert weekday_mismatch("do czwartku", "2026-10-09")  # Friday -> mismatch


def test_plain_speaker_format(tmp_path: Path):
    f = tmp_path / "t.txt"
    f.write_text("Meeting 2026-03-02\n\nSpeaker 1: Hello there, can you hear me?\nSpeaker 2: Yes. Let's start.\n")
    t = parse(f)
    assert [x.speaker for x in t.turns] == ["Speaker 1", "Speaker 2"]
    assert t.header_date == date(2026, 3, 2)


def test_quote_fuzzy_and_missing(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("## Transcript\n\n**Ann:** We are now at „Toruńska 120”, hours unchanged.\n")
    t = parse(f)
    assert check_quote('we are now at "Toruńska 120"', t, 85).found
    assert check_quote("We moved to Kapitulna 5 last year", t, 85).found is False


def test_blackout_blocks_launch_in_window_only():
    blackout = _item(id="g", type="blackout_window", action_kind="none", forbids_action_kinds=["launch"],
                     window_start="2026-10-19", window_end="2026-10-23", applies_to_all_work=True,
                     scope_tags=["vacation"])  # self-describing tag must not narrow an all-work blackout
    item = _item()
    a = Action(id="a", item_id="a-01", route="change_checklist", kind=ActionKind.launch, title="t")
    args = ([blackout], {}, [], )
    assert check(a, item, *args, as_of=date(2026, 10, 19), meeting_date=date(2026, 10, 6)).status == "blocked"
    assert check(a, item, *args, as_of=date(2026, 10, 26), meeting_date=date(2026, 10, 6)).status == "clear"
    fix = a.model_copy(update={"kind": ActionKind.fix})
    assert check(fix, item, *args, as_of=date(2026, 10, 19), meeting_date=date(2026, 10, 6)).status == "clear"


def test_scoped_guardrail_needs_tag_overlap():
    g = _item(id="g", type="guardrail", action_kind="none", forbids_action_kinds=["enable"], scope_tags=["opel"])
    a = Action(id="a", item_id="a-01", route="change_checklist", kind=ActionKind.enable, title="t", scope_tags=["peugeot"])
    assert check(a, _item(), [g], {}, [], date(2026, 10, 7), date(2026, 10, 6)).status == "clear"
    a.scope_tags = ["opel"]
    assert check(a, _item(), [g], {}, [], date(2026, 10, 7), date(2026, 10, 6)).status == "blocked"


def test_lifter_is_not_scope():
    # "Don't contact Ola, everything goes through me (Kasia)" must not block contacting Kasia.
    g = _item(id="g", type="guardrail", action_kind="none", forbids_action_kinds=["contact"],
              scope_tags=["ola", "kasia"], lifted_by="Kasia Malinowska")
    to_kasia = Action(id="a", item_id="a-01", route="followup", kind=ActionKind.contact, title="t", scope_tags=["kasia"])
    to_ola = to_kasia.model_copy(update={"scope_tags": ["ola"]})
    assert check(to_kasia, _item(), [g], {}, [], date(2026, 10, 7), date(2026, 10, 6)).status == "clear"
    assert check(to_ola, _item(), [g], {}, [], date(2026, 10, 7), date(2026, 10, 6)).status == "blocked"


def test_elided_quote_needs_every_part(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("## Transcript\n\n**A:** Do not rerun the old list, please.\n**B:** Sure, the old list stays off.\n")
    t = parse(f)
    assert check_quote("Do not rerun the old list [...] the old list stays off", t, 85).found
    assert not check_quote("Do not rerun the old list [...] we will delete everything", t, 85).found


def test_blackout_new_launch_vs_requested_change():
    blackout = _item(id="20261006-90", type="blackout_window", action_kind="none",
                     forbids_action_kinds=["launch", "change_config"], applies_to_all_work=True,
                     window_start="2026-10-19", window_end="2026-10-23")
    hours = _item(id="20261006-01", action_kind="change_config", client_requested=True)
    ab = _item(id="20261006-02", action_kind="change_config", client_requested=True, new_for_end_customers=True)
    act = lambda i: Action(id="a", item_id=i.id, route="change_checklist", kind=i.action_kind, title="t")
    run = lambda i: check(act(i), i, [blackout], {}, [], date(2026, 10, 19), date(2026, 10, 6)).status
    assert run(hours) == "clear"
    assert run(ab) == "blocked"


def test_guardrail_only_matches_same_product_area():
    g = _item(id="g", type="guardrail", action_kind="none", forbids_action_kinds=["build"],
              scope_tags=["upsell"], product_area="agent_conversation")
    panel = _item(product_area="panel_dashboard", action_kind="build")
    a = Action(id="a", item_id="a-01", route="backlog", kind=ActionKind.build, title="t", scope_tags=["upsell"])
    assert check(a, panel, [g], {}, [], date(2026, 10, 7), date(2026, 10, 6)).status == "clear"
    agent = panel.model_copy(update={"product_area": "agent_conversation"})
    assert check(a, agent, [g], {}, [], date(2026, 10, 7), date(2026, 10, 6)).status == "blocked"


def test_guardrail_never_blocks_primary_contact_or_on_generic_tags():
    g = _item(id="g", type="guardrail", action_kind="none", forbids_action_kinds=["send", "contact"],
              scope_tags=["kasia", "ola", "campaign"])
    recap = Action(id="r", item_id="x", route="recap", kind=ActionKind.send, title="t", scope_tags=["recap", "kasia"])
    assert check(recap, None, [g], {}, [], date(2026, 10, 7), date(2026, 10, 6), "Kasia Malinowska").status == "clear"
    camp = Action(id="c", item_id="a-01", route="change_checklist", kind=ActionKind.send, title="t", scope_tags=["campaign"])
    assert check(camp, _item(), [g], {}, [], date(2026, 10, 7), date(2026, 10, 6), "Kasia Malinowska").status == "clear"
    ola = recap.model_copy(update={"scope_tags": ["ola"]})
    assert check(ola, None, [g], {}, [], date(2026, 10, 7), date(2026, 10, 6), "Kasia Malinowska").status == "blocked"


def test_blackout_ignores_its_tags():
    b = _item(id="b", type="blackout_window", action_kind="none", forbids_action_kinds=["launch"],
              scope_tags=["vacation", "opel"], window_start="2026-10-19", window_end="2026-10-23", product_area="account")
    launch = _item(id="20261006-05", action_kind="launch", scope_tags=["fresh_leads"], product_area="campaigns_and_leads")
    a = Action(id="a", item_id=launch.id, route="change_checklist", kind=ActionKind.launch, title="t", scope_tags=["fresh_leads"])
    assert check(a, launch, [b], {}, [], date(2026, 10, 19), date(2026, 10, 6)).status == "blocked"
