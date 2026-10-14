# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""Unit tests for the Saphira WebSocket dispatcher routing and agent execution."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from src.api.saphira_dispatcher import (
    AgentExecutionEngine,
    AgentResponse,
    ClientEvent,
    ConnectionManager,
    NovaAgentRegistry,
)


def _event(
    event_type: str = "text_intent",
    session_id: str = "sess-1",
    target_agent: Optional[str] = "saphira",
    payload: Optional[Dict[str, Any]] = None,
    timestamp: str = "2026-10-14T00:00:00Z",
) -> ClientEvent:
    return ClientEvent(
        event_type=event_type,
        session_id=session_id,
        target_agent=target_agent,
        payload=payload or {},
        timestamp=timestamp,
    )


SAMPLE_SCREEN_TREE = {
    "package_name": "com.example.searchapp",
    "root_node": {
        "class_name": "android.widget.FrameLayout",
        "bounds": [0, 0, 1080, 2400],
        "children": [
            {
                "class_name": "android.widget.EditText",
                "text": "Search",
                "content_desc": "Search field",
                "is_clickable": True,
                "is_editable": True,
                "is_focused": True,
                "view_id_resource_name": "com.example:id/search_box",
                "bounds": [40, 120, 1040, 220],
                "children": [],
            },
            {
                "class_name": "android.widget.Button",
                "text": "Submit",
                "content_desc": "Submit query",
                "is_clickable": True,
                "is_editable": False,
                "view_id_resource_name": "com.example:id/submit_btn",
                "bounds": [400, 300, 680, 400],
                "children": [],
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_client_event_requires_core_fields():
    with pytest.raises(ValidationError):
        ClientEvent(event_type="text_intent", payload={})  # type: ignore[call-arg]


def test_client_event_defaults():
    event = _event()
    assert event.target_agent == "saphira"
    assert event.payload == {}


def test_agent_response_defaults():
    resp = AgentResponse(
        source_agent="saphira",
        event_type="text_response",
        payload={"text": "hi"},
    )
    assert resp.requires_client_action is False


# ---------------------------------------------------------------------------
# NovaAgentRegistry routing
# ---------------------------------------------------------------------------


def test_resolve_explicit_supported_agent():
    event = _event(target_agent="novareign", event_type="text_intent")
    assert NovaAgentRegistry.resolve_target_agent(event) == "novareign"


def test_resolve_explicit_unsupported_falls_through_to_event_type():
    event = _event(target_agent="unknown_agent", event_type="a11y_screen_state")
    assert NovaAgentRegistry.resolve_target_agent(event) == "novareign"


def test_resolve_a11y_and_screen_events_to_novareign():
    for et in ("a11y_screen_state", "screen_update", "click_request", "A11Y_DUMP"):
        event = _event(event_type=et, target_agent=None)
        assert NovaAgentRegistry.resolve_target_agent(event) == "novareign"


def test_resolve_audio_voice_to_aura():
    for et in ("user_voice_chunk", "audio_frame", "VOICE_START"):
        event = _event(event_type=et, target_agent=None)
        assert NovaAgentRegistry.resolve_target_agent(event) == "aura"


def test_resolve_memory_recall_to_agent_two():
    for et in ("memory_query", "recall_context", "MEMORY_WRITE"):
        event = _event(event_type=et, target_agent=None)
        assert NovaAgentRegistry.resolve_target_agent(event) == "agent_two"


def test_resolve_default_to_saphira():
    event = _event(event_type="text_intent", target_agent=None)
    assert NovaAgentRegistry.resolve_target_agent(event) == "saphira"


def test_supported_agents_catalog():
    expected = {
        "saphira",
        "aura",
        "agent_two",
        "novareign",
        "novaaethrea",
        "agent_zero",
    }
    assert set(NovaAgentRegistry.SUPPORTED_AGENTS.keys()) == expected


# ---------------------------------------------------------------------------
# AgentExecutionEngine — novareign / a11y path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_novareign_with_tree_and_intent():
    event = _event(
        event_type="a11y_screen_state",
        target_agent="novareign",
        payload={
            "screen_tree": SAMPLE_SCREEN_TREE,
            "target_intent": "Submit",
        },
    )
    resp = await AgentExecutionEngine.dispatch_to_agent("novareign", event)

    assert resp.source_agent == "novareign"
    assert resp.event_type == "execute_a11y_command"
    assert resp.requires_client_action is True
    assert resp.payload["package_name"] == "com.example.searchapp"
    plan = resp.payload["action_plan"]
    assert plan["action"] == "click"
    assert plan["target_type"] == "element_match"
    assert plan["node_id"] == "com.example:id/submit_btn"
    assert plan["center_point"]["x"] == 540
    assert plan["center_point"]["y"] == 350


@pytest.mark.asyncio
async def test_dispatch_novareign_with_tree_without_intent():
    event = _event(
        event_type="a11y_screen_state",
        target_agent="novareign",
        payload={"screen_tree": SAMPLE_SCREEN_TREE},
    )
    resp = await AgentExecutionEngine.dispatch_to_agent("novareign", event)

    assert resp.source_agent == "novareign"
    assert resp.requires_client_action is True
    plan = resp.payload["action_plan"]
    assert plan["action"] == "screen_parsed"
    assert plan["interactive_count"] >= 2
    assert plan["focused_input"] == "com.example:id/search_box"


@pytest.mark.asyncio
async def test_dispatch_novareign_raw_action_fallback():
    event = _event(
        event_type="a11y_screen_state",
        target_agent="novareign",
        payload={"action": {"command": "tap", "target": "com.example:id/ok"}},
    )
    resp = await AgentExecutionEngine.dispatch_to_agent("novareign", event)

    assert resp.source_agent == "novareign"
    assert resp.event_type == "execute_a11y_command"
    assert resp.requires_client_action is True
    assert resp.payload["command"] == "tap"
    assert resp.payload["target"] == "com.example:id/ok"


@pytest.mark.asyncio
async def test_dispatch_novareign_empty_tree_uses_fallback():
    event = _event(
        event_type="a11y_screen_state",
        target_agent="novareign",
        payload={"screen_tree": {}, "action": {"command": "back"}},
    )
    resp = await AgentExecutionEngine.dispatch_to_agent("novareign", event)
    assert resp.payload.get("command") == "back"


@pytest.mark.asyncio
async def test_dispatch_novareign_unknown_intent_still_returns_plan():
    event = _event(
        event_type="a11y_screen_state",
        target_agent="novareign",
        payload={
            "screen_tree": SAMPLE_SCREEN_TREE,
            "target_intent": "NonexistentControl",
        },
    )
    resp = await AgentExecutionEngine.dispatch_to_agent("novareign", event)
    plan = resp.payload["action_plan"]
    assert plan["action"] == "unknown"
    assert plan["target_type"] == "none"


# ---------------------------------------------------------------------------
# AgentExecutionEngine — aura / saphira
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_aura():
    event = _event(event_type="user_voice_chunk", target_agent="aura")
    resp = await AgentExecutionEngine.dispatch_to_agent("aura", event)

    assert resp.source_agent == "aura"
    assert resp.event_type == "audio_processed"
    assert resp.payload["status"] == "received"
    assert resp.payload["sample_rate"] == 16000
    assert resp.requires_client_action is False


@pytest.mark.asyncio
async def test_dispatch_saphira_default():
    event = _event(
        event_type="text_intent",
        target_agent="saphira",
        payload={"content": "plan my day"},
    )
    resp = await AgentExecutionEngine.dispatch_to_agent("saphira", event)

    assert resp.source_agent == "saphira"
    assert resp.event_type == "text_response"
    assert "plan my day" in resp.payload["text"]
    assert resp.requires_client_action is False


@pytest.mark.asyncio
async def test_dispatch_unknown_agent_key_falls_to_saphira_branch():
    event = _event(payload={"content": "hello"})
    resp = await AgentExecutionEngine.dispatch_to_agent("novaaethrea", event)
    assert resp.source_agent == "saphira"
    assert resp.event_type == "text_response"


# ---------------------------------------------------------------------------
# ConnectionManager
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_connection_manager_connect_and_disconnect():
    manager = ConnectionManager()
    ws = AsyncMock()
    ws.accept = AsyncMock()

    await manager.connect("client-a", ws)
    assert "client-a" in manager.active_connections
    ws.accept.assert_awaited_once()

    manager.disconnect("client-a")
    assert "client-a" not in manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_disconnect_unknown_is_safe():
    manager = ConnectionManager()
    manager.disconnect("never-connected")  # should not raise


@pytest.mark.asyncio
async def test_connection_manager_send_response():
    manager = ConnectionManager()
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()

    await manager.connect("client-b", ws)
    resp = AgentResponse(
        source_agent="saphira",
        event_type="text_response",
        payload={"text": "ok"},
    )
    await manager.send_response("client-b", resp)

    ws.send_text.assert_awaited_once()
    sent = ws.send_text.await_args.args[0]
    assert "saphira" in sent
    assert "text_response" in sent


@pytest.mark.asyncio
async def test_connection_manager_send_to_missing_session_is_noop():
    manager = ConnectionManager()
    resp = AgentResponse(
        source_agent="saphira",
        event_type="text_response",
        payload={"text": "noop"},
    )
    await manager.send_response("missing", resp)  # should not raise


# ---------------------------------------------------------------------------
# End-to-end routing helper (registry → engine)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_route_a11y_event_through_registry_and_engine():
    event = _event(
        event_type="a11y_screen_state",
        target_agent=None,
        payload={
            "screen_tree": SAMPLE_SCREEN_TREE,
            "target_intent": "Search",
        },
    )
    agent = NovaAgentRegistry.resolve_target_agent(event)
    assert agent == "novareign"

    resp = await AgentExecutionEngine.dispatch_to_agent(agent, event)
    assert resp.source_agent == "novareign"
    assert resp.requires_client_action is True
    assert resp.payload["action_plan"]["action"] == "click"
