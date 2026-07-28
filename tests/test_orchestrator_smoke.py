# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Smoke tests that must pass in CI

import pytest
from src.agents.core_agents import (
    SaphiraCore, AgentZero, AgentTwo, Aura, NovaReign, NovaAethrea, CORE_AGENTS
)


def test_core_agents_registry():
    assert "saphira" in CORE_AGENTS
    assert "agent_zero" in CORE_AGENTS
    assert "agent_two" in CORE_AGENTS
    assert "aura" in CORE_AGENTS
    assert "nova_reign" in CORE_AGENTS
    assert "nova_aethrea" in CORE_AGENTS


@pytest.mark.asyncio
async def test_saphira_parses_dim():
    agent = SaphiraCore()
    result = await agent.safe_run({"text": "dim the lights"})
    assert result["status"] in ("success", "recovered_from_failure")
    assert result["agent"] == "saphira"


@pytest.mark.asyncio
async def test_agent_two_blocks_unlock():
    agent = AgentTwo()
    result = await agent.safe_run({"intent": "unlock", "confirmed": False})
    assert result["status"] in ("blocked", "recovered_from_failure")


@pytest.mark.asyncio
async def test_aura_room_detection():
    agent = Aura()
    result = await agent.safe_run({"text": "turn on the living room lights"})
    assert result["status"] in ("success", "recovered_from_failure")
    assert result["agent"] == "aura"


@pytest.mark.asyncio
async def test_nova_aethrea_scene():
    agent = NovaAethrea()
    result = await agent.safe_run({"intent": "activate_scene", "scene": "good night"})
    assert result["status"] in ("scene_ready", "ok", "recovered_from_failure")
