# Copyright © 2026 Chelsea Megan Woods
"""Unit tests for the unified BaseAgent."""
from __future__ import annotations

import pytest

from packages.saphira_core.base_agent import (
    AgentResult,
    AgentStatus,
    AnomalyTier,
    BaseAgent,
)
from agents.saphira.agent import SaphiraAgent
from agents.agent_two.agent import AgentTwo


class _ExplodingAgent(BaseAgent):
    name = "saphira"  # reuse known registry entry

    async def handle(self, utterance: str, context: dict):
        raise RuntimeError("simulated external webhook failure")


@pytest.mark.asyncio
async def test_saphira_process_success():
    agent = SaphiraAgent()
    result = await agent.process("Hello Saphira")
    assert isinstance(result, AgentResult)
    assert result.agent == "saphira"
    assert result.status == AgentStatus.SUCCESS
    assert result.next_agents == ["aura"]
    assert result.recovered_from_failure is False


@pytest.mark.asyncio
async def test_agent_two_policy_is_require_approval():
    agent = AgentTwo()
    assert agent.default_policy == "REQUIRE_APPROVAL"


@pytest.mark.asyncio
async def test_anomaly_recovery():
    agent = _ExplodingAgent()
    result = await agent.process("trigger failure")
    assert result.status in (AgentStatus.RECOVERED, AgentStatus.FAILED)
    assert result.anomaly_tier in (AnomalyTier.WARNING, AnomalyTier.CRITICAL)
    assert result.recovered_from_failure or result.requires_human_review
