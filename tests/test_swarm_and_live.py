# Tests for SwarmOrchestrator and LiveAgentOrchestrator
# Copyright © 2026 Chelsea Megan Woods

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.core.swarm_orchestrator import SwarmOrchestrator
from src.core.live_orchestrator import LiveAgentOrchestrator
from src.integrations.wearable_connector import wearable_connector
from src.agents.biometric_stress import BiometricStressDetector


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.run = AsyncMock(return_value={
        "status": "success",
        "agent": "mock",
        "suggestions": "mock response",
    })
    return agent


@pytest.mark.asyncio
async def test_live_orchestrator_injects_biometrics(mock_agent):
    orch = LiveAgentOrchestrator({"test_agent": mock_agent})
    result = await orch.process_user_intent_with_biometrics(
        "I need help setting a boundary",
        {"emotion": "anxious"},
    )
    assert result["status"] == "success"
    assert "stress_level" in result
    assert "biometrics" in result
    assert "agent_outputs" in result
    assert "test_agent" in result["agent_outputs"]
    # Ensure the agent received biometrics in context
    call_args = mock_agent.run.call_args[0][0]
    assert "biometrics" in call_args
    assert "stress_level" in call_args


@pytest.mark.asyncio
async def test_swarm_parallel_execution(mock_agent):
    swarm = SwarmOrchestrator(
        specialist_agents={
            "a": mock_agent,
            "b": mock_agent,
        }
    )
    result = await swarm.run_swarm("plan my evening")
    assert result["status"] == "success"
    assert len(result["agents_run"]) == 2
    assert "stress_level" in result
    assert "specialist_outputs" in result


def test_stress_detector_full_analysis():
    det = BiometricStressDetector()
    analysis = det.analyze({"hrv": 25, "resting_hr": 95, "sleep_score": 40})
    assert analysis["stress_level"] == "high"
    assert "stress_score" in analysis
    assert "tone_guidance" in analysis
    assert "components" in analysis


def test_wearable_freshness_and_mock():
    # Force a mock read
    wearable_connector._latest_payload = None
    reading = wearable_connector.fetch_live_biometrics()
    assert "hrv" in reading
    assert "resting_hr" in reading
    assert "sleep_score" in reading
    assert reading["source"] in ("mock", "mock_fallback")
