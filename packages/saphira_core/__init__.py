"""Shared Saphira core package (monorepo)."""

__version__ = "0.2.1"

from packages.saphira_core.base_agent import (
    AgentResult,
    AgentStatus,
    AnomalyTier,
    BaseAgent,
)
from packages.saphira_core.registry import AGENTS, list_agents, policy_for
from packages.saphira_core.personas import persona_for

__all__ = [
    "__version__",
    "BaseAgent",
    "AgentResult",
    "AgentStatus",
    "AnomalyTier",
    "AGENTS",
    "list_agents",
    "policy_for",
    "persona_for",
]
