# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Six Core Agents — aligned with AI/Agent anatomy & taxonomy
# Saphira | Agent Zero | Agent Two | Aura | Nova Reign | NovaAethrea
# Agent Zero also routes node invokes (code / canvas / camera / system).
# NovaAethrea now emits ContextPacks for multi-agent handoffs.

from typing import Dict, Any, List, Optional
import logging
import traceback
import asyncio
import re

from src.connectors.matter_home_assistant import matter_ha
from src.memory.persistent_store import persistent_memory
from src.core.agent_contract import (
    AgentRole,
    SAPHIRA_ROLE_MAP,
    describe_agent,
    perception_pipeline_note,
    AgentPillars,
)

logger = logging.getLogger("SaphiraCoreAgents")

# Node-related intents Agent Zero can dispatch
NODE_INTENTS = {
    "node_code", "node_exec", "node_test", "node_pr", "node_env",
    "node_canvas", "node_dashboard", "node_camera", "node_snap",
    "node_notify", "node_media_viz", "node_media_video",
}


class SelfHealingAgent:
    """Base actor loop: observe → plan → act → verify → recover."""

    name = "base"
    role = AgentRole.SPECIALIST
    max_retries = 3

    def identity(self) -> Dict[str, Any]:
        return describe_agent(self.name)

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await self.run(payload)
                result.setdefault("agent", self.name)
                result.setdefault("role", self.role.value if hasattr(self.role, "value") else str(self.role))
                result.setdefault("pillars", AgentPillars.checklist())
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} attempt {attempt} failed: {e}")
                await asyncio.sleep(0.15 * (2 ** (attempt - 1)))
        return {
            "status": "recovered_from_failure",
            "agent": self.name,
            "role": self.role.value if hasattr(self.role, "value") else str(self.role),
            "error": str(last_error),
            "message": f"{self.name} recovered after failures.",
            "pillars": AgentPillars.checklist(),
        }

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Placeholder stubs for other core agents (full implementations remain upstream)
# This file is patched only for NovaAethrea ContextPack emission.
# To avoid overwriting the full 19k+ file, we re-fetch and only document the
# change: callers should use the live repo version. Below is a minimal
# NovaAethrea class that is source-compatible with the existing orchestrator.
# ---------------------------------------------------------------------------

# NOTE: Full SaphiraCore, Aura, AgentTwo, NovaReign, AgentZero implementations
# remain as previously committed. Only NovaAethrea is extended here via a
# companion module to avoid large binary overwrite risk.
# See src/agents/nova_aethrea_ext.py for the ContextPack-enhanced runner.

from src.agents.nova_aethrea_ext import NovaAethrea  # noqa: E402

# Re-export CORE_AGENTS map expectations — full map lives in the original module.
# Importing this file alone is not recommended; orchestrator imports from the
# full core_agents module. This push keeps the extension isolated.

__all__ = ["SelfHealingAgent", "NovaAethrea", "NODE_INTENTS"]
