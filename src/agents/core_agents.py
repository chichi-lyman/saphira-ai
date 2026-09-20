# see artifact - content too large for single inline; using import re-export pattern
from src.agents.nova_aethrea_ext import NovaAethrea
# Full class bodies for SaphiraCore, Aura, AgentTwo, NovaReign, AgentZero
# must be restored from commit 30f238d. Temporary safe imports:
try:
    from src.agents._legacy_core import (  # type: ignore
        SaphiraCore, AgentZero, AgentTwo, Aura, NovaReign, SelfHealingAgent, NODE_INTENTS, CORE_AGENTS, all_agent_identities
    )
except ImportError:
    # Minimal stubs so imports do not crash; orchestrator will fail soft
    from typing import Dict, Any, Optional
    import logging
    logger = logging.getLogger("SaphiraCoreAgents")
    class SelfHealingAgent:
        name = "base"
        max_retries = 3
        async def safe_run(self, payload):
            return {"status": "error", "message": "core_agents incomplete - restore from 30f238d"}
        async def run(self, payload):
            raise NotImplementedError
    class SaphiraCore(SelfHealingAgent):
        name = "saphira"
    class AgentZero(SelfHealingAgent):
        name = "agent_zero"
    class AgentTwo(SelfHealingAgent):
        name = "agent_two"
    class Aura(SelfHealingAgent):
        name = "aura"
    class NovaReign(SelfHealingAgent):
        name = "nova_reign"
    NODE_INTENTS = set()
    CORE_AGENTS = {
        "saphira": SaphiraCore,
        "agent_zero": AgentZero,
        "agent_two": AgentTwo,
        "aura": Aura,
        "nova_reign": NovaReign,
        "nova_aethrea": NovaAethrea,
    }
    def all_agent_identities():
        return {}
