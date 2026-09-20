# Copyright © 2026 Chelsea Megan Woods
"""Smoke tests for LangGraph pipeline adapter and policy models."""

import pytest
from src.orchestration.policy_models import PolicyAction, PolicyDecision, HandoffPayload


def test_policy_decision_allow():
    d = PolicyDecision(action=PolicyAction.ALLOW, reason="safe", agent="nova_reign")
    assert d.action == PolicyAction.ALLOW
    assert d.requires_human is False


def test_policy_decision_require_approval():
    d = PolicyDecision(
        action=PolicyAction.REQUIRE_APPROVAL,
        reason="spend",
        agent="agent_apex",
        requires_human=True,
    )
    assert d.requires_human is True
    assert d.model_dump()["action"] == "REQUIRE_APPROVAL"


def test_handoff_payload_forbid_extra():
    with pytest.raises(Exception):
        HandoffPayload(
            trace_id="t",
            from_agent="a",
            to_agent="b",
            task_id="x",
            objective="o",
            unexpected_field=True,  # type: ignore
        )


def test_langgraph_pipeline_optional():
    try:
        from src.orchestration.langgraph_pipeline import build_saphira_graph

        graph = build_saphira_graph()
        result = graph.invoke({"user_input": "hello", "context": {}})
        assert result.get("status") in ("success", "running", "blocked")
        assert "messages" in result
    except ImportError:
        pytest.skip("langgraph not installed in this environment")
