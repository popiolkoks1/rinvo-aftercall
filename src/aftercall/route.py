"""Turn items into actions, per config/taxonomy.yaml."""

from __future__ import annotations

from . import config
from .models import Action, ActionKind, Item, ItemType


def routes_for(item: Item) -> list[str]:
    tax = config.taxonomy()
    routes = list(tax["types"][item.type.value]["routes"])
    if routes == ["memory"]:
        return routes  # guardrails/blackouts are rules, never actions, whatever action_kind says
    kind = ActionKind.launch if item.new_for_end_customers else item.action_kind
    for extra in tax.get("action_kind_routes", {}).get(kind.value, []):
        if extra not in routes:
            routes.append(extra)
    return routes


def build_actions(items: list[Item], primary_contact: str) -> list[Action]:
    tax = config.taxonomy()
    skip_status = set(tax["non_action_statuses"])
    actions: list[Action] = []

    for item in items:
        if not item.active or item.status.value in skip_status:
            continue
        for route in routes_for(item):
            if route == "memory":
                continue
            kind, recipient, date = item.action_kind, None, item.due
            title = item.title
            if route == "followup" and item.type == ItemType.waiting_on_client:
                # Our action is a reminder to the client, on the reminder date.
                kind, recipient = ActionKind.contact, item.owner_person
                title = f"Remind {item.owner_person or 'client'}: {item.title}"
                if item.max_reminders is not None:
                    title += f" (max {item.max_reminders} reminder{'s' if item.max_reminders != 1 else ''})"
            elif route == "followup" and item.type == ItemType.meeting_request:
                kind, recipient = ActionKind.contact, primary_contact
                title = f"Chase confirmation (no invite until confirmed): {item.title}"
            elif route == "change_checklist" and item.type == ItemType.waiting_on_client:
                # Execution once the client delivers: not on the reminder date.
                date = None
                if item.new_for_end_customers:
                    kind = ActionKind.launch
                    title = f"Launch once received: {item.title}"
            elif route in ("internal_note", "meeting_brief"):
                kind = ActionKind.none
            if route in ("ticket", "change_checklist") and item.vendor_commitment_level.value == "will_look_into":
                title = f"Look into (no fix promised): {title}"
            tags = list(item.scope_tags)
            if recipient:
                tags.append(recipient.split()[0].lower())
            actions.append(
                Action(
                    id=f"{item.id}/{route}",
                    item_id=item.id,
                    route=route,
                    kind=kind,
                    title=title,
                    date=date,
                    recipient=recipient,
                    scope_tags=tags,
                )
            )
    return actions


def recap_action(meeting_date: str, primary_contact: str) -> Action:
    return Action(
        id="recap/email",
        item_id="recap",
        route="recap",
        kind=ActionKind.send,
        title=f"Send call recap to {primary_contact}",
        date=meeting_date,
        recipient=primary_contact,
        scope_tags=["recap", primary_contact.split()[0].lower()],
    )
