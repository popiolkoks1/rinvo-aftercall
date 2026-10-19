"""Data models.

The `*Out` models are what the LLM fills in (structured output). They have no
defaults on purpose: every field is required and nullable fields are explicit,
which keeps the response schema simple. Runtime models extend them with fields
filled by deterministic code.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ItemType(str, Enum):
    bug = "bug"
    config_change = "config_change"
    knowledge_base_fix = "knowledge_base_fix"
    feature_request = "feature_request"
    vendor_commitment = "vendor_commitment"
    waiting_on_client = "waiting_on_client"
    question_to_answer = "question_to_answer"
    meeting_request = "meeting_request"
    guardrail = "guardrail"
    blackout_window = "blackout_window"
    billing = "billing"
    sales_signal = "sales_signal"
    churn_risk = "churn_risk"
    success_story = "success_story"


class Status(str, Enum):
    open = "open"
    waiting = "waiting"
    done = "done"
    declined = "declined"
    parked = "parked"


class ActionKind(str, Enum):
    fix = "fix"
    investigate = "investigate"
    change_config = "change_config"
    update_kb = "update_kb"
    build = "build"
    send = "send"
    contact = "contact"
    schedule = "schedule"
    launch = "launch"
    enable = "enable"
    none = "none"


class Side(str, Enum):
    vendor = "vendor"
    client = "client"


class CommitmentLevel(str, Enum):
    committed = "committed"            # vendor said they will do it
    will_look_into = "will_look_into"  # vendor said they will check / look / see whether
    no_commitment = "no_commitment"    # client asked, vendor promised nothing (or not a vendor action)


class Visibility(str, Enum):
    client = "client"
    internal = "internal"


# ---------------------------------------------------------------- LLM output


class PersonOut(BaseModel):
    name: str
    side: Side
    role: Optional[str]
    email: Optional[str]
    present_on_call: bool
    can_approve: list[str] = Field(description="scope tags this person can approve")
    cannot_approve: list[str] = Field(description="scope tags this person explicitly cannot approve")


class ItemOut(BaseModel):
    ref: str = Field(description="short unique ref within this call: i1, i2, ...")
    type: ItemType
    title: str = Field(description="imperative, specific, in English")
    detail: str = Field(description="what exactly, with concrete values (numbers, addresses, hours), in English")
    owner_side: Side
    owner_person: Optional[str]
    status: Status
    action_kind: ActionKind = Field(description="what the vendor will do when executing this item")
    product_area: str = Field(description="one value from the product area list in the instructions")
    new_for_end_customers: bool = Field(description="executing this starts something end customers haven't experienced before")
    client_requested: bool = Field(description="the client explicitly asked for this on the call")
    vendor_commitment_level: CommitmentLevel
    blocked_on_input: Optional[str] = Field(description="what client-side input is needed before the vendor can act, if any")
    blocked_on_person: Optional[str] = Field(description="client-side person expected to provide that input")
    scope_tags: list[str]
    visibility: Visibility
    due_phrase: Optional[str] = Field(description="the words used for the deadline, verbatim")
    due: Optional[str] = Field(description="ISO date YYYY-MM-DD")
    earliest_start_phrase: Optional[str]
    earliest_start: Optional[str] = Field(description="ISO date; not before this date")
    trigger_condition: Optional[str]
    depends_on: list[str] = Field(description="refs of items that must happen first")
    related_refs: list[str]
    superseded_by_ref: Optional[str] = Field(description="ref of a later item in this call that replaces this one")
    approver: Optional[str] = Field(description="person whose approval is required before execution")
    max_reminders: Optional[int]
    forbids_action_kinds: list[ActionKind] = Field(description="guardrail/blackout only")
    window_start: Optional[str] = Field(description="guardrail/blackout only, ISO date")
    window_end: Optional[str] = Field(description="guardrail/blackout only, ISO date")
    lifted_by: Optional[str] = Field(description="guardrail/blackout only: who can lift it")
    applies_to_all_work: bool = Field(description="guardrail/blackout only: applies to every action of the forbidden kinds, whatever it touches")
    demand_signal: bool = Field(description="vendor said other clients ask for the same")
    evidence_quotes: list[str]
    confidence: float


class ItemsOut(BaseModel):
    items: list[ItemOut]


class ExtractionOut(BaseModel):
    language: str = Field(description="ISO 639-1 code of the conversation")
    client_name: str
    primary_client_contact: str
    people: list[PersonOut]
    items: list[ItemOut]


class SupersessionOut(BaseModel):
    ref: str
    superseded_by_ref: str
    reason: str


class AmendmentOut(BaseModel):
    ref: str
    new_title: str
    new_detail: str
    reason: str
    evidence_quote: str


class StateRelation(str, Enum):
    duplicate = "duplicate"
    update = "update"
    closes = "closes"
    conflict = "conflict"


class StateMatchOut(BaseModel):
    ref: str
    existing_id: str
    relation: StateRelation
    note: str


class ClosedExistingOut(BaseModel):
    existing_id: str
    reason: str
    evidence_quote: str


class ReconciliationOut(BaseModel):
    supersessions: list[SupersessionOut]
    amendments: list[AmendmentOut]
    state_matches: list[StateMatchOut]
    closed_existing: list[ClosedExistingOut]


class DraftOut(BaseModel):
    subject: str
    body: str


class InternalDraftsOut(BaseModel):
    internal_note: DraftOut
    meeting_brief: Optional[DraftOut]


# ---------------------------------------------------------------- runtime


class EvidenceCheck(BaseModel):
    quote: str
    found: bool
    score: float
    speaker: Optional[str] = None
    turn: Optional[int] = None
    source: Optional[str] = None  # "speech" | "header"


class Item(ItemOut):
    id: str = ""
    evidence: list[EvidenceCheck] = []
    flags: list[str] = []
    amended_from: Optional[str] = None
    state_match: Optional[StateMatchOut] = None

    @property
    def verified(self) -> bool:
        return any(e.found for e in self.evidence)

    @property
    def active(self) -> bool:
        return self.superseded_by_ref is None and self.verified


class GateResult(BaseModel):
    status: str  # clear | blocked | waiting | needs_approval | not_before
    exec_date: Optional[str] = None
    reasons: list[str] = []
    blocked_by: list[str] = []  # guardrail item ids
    notes: list[str] = []  # guardrails considered but not applied, and why


class Action(BaseModel):
    id: str
    item_id: str
    route: str
    kind: ActionKind
    title: str
    date: Optional[str] = None
    recipient: Optional[str] = None
    scope_tags: list[str] = []
    gate: Optional[GateResult] = None


class Person(PersonOut):
    pass


class ClientState(BaseModel):
    slug: str
    client_name: str = ""
    people: list[Person] = []
    items: list[Item] = []
    calls: list[dict] = []
