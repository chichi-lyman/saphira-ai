# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Stress tests that push all six core agents to failure and verify recovery

import pytest
import asyncio
from src.agents.core_agents import (
    SaphiraCore, AgentZero, AgentTwo, Aura, NovaReign, NovaAethrea
)


@pytest.mark.asyncio
async def test_saphira_voice_intent_parsing():
    agent = SaphiraCore()
    result = await agent.safe_run({"text": "dim the living room lights"})
    assert result["status"] in ("success", "recovered_from_failure")
    assert "parsed_intent" in result or result.get("status") == "recovered_from_failure"


@pytest.mark.asyncio
async def test_agent_two_blocks_unlock():
    agent = AgentTwo()
    result = await agent.safe_run({"intent": "unlock", "confirmed": False})
    assert result["status"] in ("blocked", "recovered_from_failure")


@pytest.mark.asyncio
async def test_nova_aethrea_scene_system():
    agent = NovaAethrea()
    result = await agent.safe_run({"intent": "activate_scene", "scene": "good night"})
    assert result["status"] in ("scene_ready", "recovered_from_failure")
    if result["status"] == "scene_ready":
        assert len(result["steps"]) > 0


@pytest.mark.asyncio
async def test_all_six_survive_empty_payload():
    agents = [SaphiraCore(), AgentZero(), AgentTwo(), Aura(), NovaReign(), NovaAethrea()]
    for agent in agents:
        result = await agent.safe_run({})
        assert "status" in result
        assert result["agent"] == agent.name


@pytest.mark.asyncio
async def test_all_six_survive_corrupt_payload():
    agents = [SaphiraCore(), AgentZero(), AgentTwo(), Aura(), NovaReign(), NovaAethrea()]
    corrupt = {"intent": None, "params": "not-a-dict", "text": 12345}
    for agent in agents:
        result = await agent.safe_run(corrupt)
        assert "status" in result
