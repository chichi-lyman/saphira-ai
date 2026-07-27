# Integration Test: Biometric Data Through All Four High-Impact Agents
# Copyright © 2026 Chelsea Megan Woods

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.agents.boundary_coach import BoundaryCoachAgent
from src.agents.admin_resolver import AdminResolverAgent
from src.agents.relationship_agent import RelationshipAgent
from src.agents.lifestyle_orchestrator import LifestyleOrchestratorAgent


@pytest.fixture
def mock_router():
    router = MagicMock()
    router.generate_response = AsyncMock(return_value="Mock adaptive response based on stress level.")
    return router


@pytest.fixture
def high_stress_biometrics():
    return {
        "hrv": 25,          # Low HRV = high stress
        "resting_hr": 95,   # Elevated
        "sleep_score": 40   # Poor sleep
    }


@pytest.fixture
def low_stress_biometrics():
    return {
        "hrv": 75,
        "resting_hr": 58,
        "sleep_score": 88
    }


@pytest.mark.asyncio
async def test_boundary_coach_high_stress(mock_router, high_stress_biometrics):
    agent = BoundaryCoachAgent(mock_router)
    result = await agent.run({
        "situation": "I need to set a boundary with a family member",
        "emotion": "anxious",
        "biometrics": high_stress_biometrics
    })
    assert result["status"] == "success"
    assert result["agent"] == "boundary_coach"
    assert result["stress_level"] == "high"
    assert "suggestions" in result


@pytest.mark.asyncio
async def test_admin_resolver_high_stress(mock_router, high_stress_biometrics):
    agent = AdminResolverAgent(mock_router)
    result = await agent.run({
        "issue": "Disputed medical bill of $1200",
        "documents": ["policy.pdf"],
        "biometrics": high_stress_biometrics
    })
    assert result["status"] == "success"
    assert result["agent"] == "admin_resolver"
    assert result["stress_level"] == "high"
    assert "plan" in result


@pytest.mark.asyncio
async def test_relationship_agent_low_stress(mock_router, low_stress_biometrics):
    agent = RelationshipAgent(mock_router)
    result = await agent.run({
        "people": ["Jordan", "Sam"],
        "context": "Haven't talked in 3 weeks",
        "biometrics": low_stress_biometrics
    })
    assert result["status"] == "success"
    assert result["agent"] == "relationship"
    assert result["stress_level"] == "low"
    assert "suggestions" in result


@pytest.mark.asyncio
async def test_lifestyle_orchestrator_medium_stress(mock_router):
    agent = LifestyleOrchestratorAgent(mock_router)
    medium_biometrics = {"hrv": 45, "resting_hr": 72, "sleep_score": 65}
    result = await agent.run({
        "calendar": ["Meeting 10am", "Deadline 4pm"],
        "biometrics": medium_biometrics
    })
    assert result["status"] == "success"
    assert result["agent"] == "lifestyle_orchestrator"
    assert result["stress_level"] in ["low", "medium", "high"]
    assert "plan" in result


@pytest.mark.asyncio
async def test_all_four_agents_receive_biometrics(mock_router, high_stress_biometrics):
    """End-to-end check that every high-impact agent accepts and reacts to biometrics."""
    agents = [
        BoundaryCoachAgent(mock_router),
        AdminResolverAgent(mock_router),
        RelationshipAgent(mock_router),
        LifestyleOrchestratorAgent(mock_router),
    ]
    payloads = [
        {"situation": "boundary test", "emotion": "stressed", "biometrics": high_stress_biometrics},
        {"issue": "bill dispute", "documents": [], "biometrics": high_stress_biometrics},
        {"people": ["Alex"], "context": "check-in", "biometrics": high_stress_biometrics},
        {"calendar": [], "biometrics": high_stress_biometrics},
    ]

    for agent, payload in zip(agents, payloads):
        result = await agent.run(payload)
        assert result["status"] == "success"
        assert "stress_level" in result
        assert result["stress_level"] == "high"
