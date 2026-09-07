# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Unit tests for Twilio voice connector and adapter (no live network)."""

from __future__ import annotations

import pytest

from src.connectors.twilio_connector import TwilioConnector
from src.integrations.twilio_voice_adapter import TwilioVoiceAdapter, VOICE_CAPABILITIES


def test_health_unconfigured():
    c = TwilioConnector(account_sid="", auth_token="", from_number="")
    h = c.health()
    assert h["status"] == "unconfigured"
    assert h["provider"] == "twilio"


def test_health_configured():
    c = TwilioConnector(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token="token",
        from_number="+15551234567",
    )
    h = c.health()
    assert h["status"] == "ready"
    assert h["from_number_set"] is True


def test_outbound_requires_approval():
    c = TwilioConnector(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token="token",
        from_number="+15551234567",
    )
    result = c.start_voice_call("+15557654321", say_text="Hello", approved=False)
    assert result["status"] == "denied"
    assert "approval" in result["message"].lower()


def test_sms_requires_approval():
    c = TwilioConnector(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token="token",
        from_number="+15551234567",
    )
    result = c.send_sms("+15557654321", "test", approved=False)
    assert result["status"] == "denied"


def test_build_say_twiml_escapes():
    xml = TwilioConnector.build_say_twiml('Hello <script>&\'"', voice="alice")
    assert "<?xml" in xml
    assert "<Say" in xml
    assert "<Hangup/>" in xml
    assert "<script>" not in xml
    assert "&lt;" in xml or "&amp;" in xml


def test_build_gather_twiml():
    xml = TwilioConnector.build_gather_twiml(
        "Press 1",
        action_url="https://example.com/gather",
        num_digits=1,
    )
    assert "<Gather" in xml
    assert "https://example.com/gather" in xml
    assert "Press 1" in xml


def test_call_requires_destination_and_content():
    c = TwilioConnector(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token="token",
        from_number="+15551234567",
    )
    r1 = c.start_voice_call("", say_text="hi", approved=True)
    assert r1["status"] == "error"
    r2 = c.start_voice_call("+15557654321", approved=True)
    assert r2["status"] == "error"
    assert "twiml_url or say_text" in r2["message"]


@pytest.mark.asyncio
async def test_adapter_health_and_twiml():
    c = TwilioConnector(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token="token",
        from_number="+15551234567",
    )
    adapter = TwilioVoiceAdapter(connector=c)
    health = await adapter.health()
    assert health["status"] == "ready"

    say = await adapter.invoke("voice.twiml.say", {"text": "Saphira online"})
    assert say["status"] == "ok"
    assert "Saphira online" in say["twiml"]

    denied = await adapter.invoke(
        "voice.call",
        {"to": "+15557654321", "say_text": "hi", "approved": False},
    )
    assert denied["status"] == "denied"

    bad = await adapter.invoke("unknown.capability", {})
    assert bad["status"] == "error"
    assert "supported" in bad


def test_voice_capabilities_nonempty():
    assert "voice.call" in VOICE_CAPABILITIES
    assert "sms.send" in VOICE_CAPABILITIES
