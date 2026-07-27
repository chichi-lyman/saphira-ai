# Stress Tests designed to break Saphira agents so they can relearn recovery
# Copyright © 2026 Chelsea Megan Woods

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.core.self_healing import SelfHealingOrchestrator
from src.agents.boundary_coach import BoundaryCoachAgent
from src.agents.lifestyle_orchestrator import LifestyleOrchestratorAgent
from src.agents.admin_resolver import AdminResolverAgent
from src.agents.relationship_agent import RelationshipAgent


@pytest.fixture
def mock_router():
    router = MagicMock()
    router.generate_response = AsyncMock(return_value="Recovered adaptive response.")
    return router


@pytest.mark.asyncio
async def test_boundary_coach_survives_timeout(mock_router):
    agent = BoundaryCoachAgent(mock_router)
    healer = SelfHealingOrchestrator(max_retries=3)

    async def call(payload):
        return await agent.run(payload)

    result = await healer.stress_run(
        call,
        {"situation": "boundary test", "emotion": "anxious", "biometrics": {"hrv": 30, "resting_hr": 90, "sleep_score": 45}},
        failure_mode="timeout"
    )
    assert result["status"] in ["success_after_stress", "exhausted_retries"]
    assert result["attempts"] >= 1


@pytest.mark.asyncio
async def test_lifestyle_survives_exception(mock_router):
    agent = LifestyleOrchestratorAgent(mock_router)
    healer = SelfHealingOrchestrator(max_retries=3)

    async def call(payload):
        return await agent.run(payload)

    result = await healer.stress_run(
        call,
        {"calendar": [], "biometrics": {"hrv": 40, "resting_hr": 80, "sleep_score": 50}},
        failure_mode="exception"
    )
    assert "recovery_log" in result


@pytest.mark.asyncio
async def test_all_agents_under_random_chaos(mock_router):
    agents = [
        BoundaryCoachAgent(mock_router),
        AdminResolverAgent(mock_router),
        RelationshipAgent(mock_router),
        LifestyleOrchestratorAgent(mock_router),
    ]
    healer = SelfHealingOrchestrator(max_retries=2)

    for agent in agents:
        async def call(payload, a=agent):
            return await a.run(payload)

        result = await healer.stress_run(
            call,
            {"situation": "chaos", "issue": "chaos", "people": [], "calendar": [], "biometrics": {"hrv": 35, "resting_hr": 85, "sleep_score": 40}},
            failure_mode="random"
        )
        assert result["attempts"] >= 1
