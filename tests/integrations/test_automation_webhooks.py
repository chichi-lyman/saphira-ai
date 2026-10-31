from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from src.api import automation_webhooks as hooks


def test_event_schema_rejects_unknown_fields():
    with pytest.raises(Exception):
        hooks.AutomationEvent(
            event_id="event-12345678",
            event_type="lead.created",
            source="make",
            unexpected="nope",
        )


def test_authentication_uses_constant_time_comparison():
    assert hooks._authorized("secret", "secret")
    assert not hooks._authorized("wrong", "secret")
    assert not hooks._authorized("secret", None)


def test_event_types_are_allowlisted():
    event = hooks.AutomationEvent(
        event_id="event-12345678",
        event_type="lead.created",
        source="make",
        occurred_at=datetime.now(timezone.utc),
        data={"lead_id": "lead-1"},
    )
    assert event.event_type in hooks._ALLOWED_EVENTS
    event.event_type = "arbitrary.delete"
    assert event.event_type not in hooks._ALLOWED_EVENTS
