# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Full Orchestrator Chain for the Six Core Agents
# Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero
# + Avatar state hints for the holographic Chelsea-look UI
# + Optional Node invokes (code / canvas / camera)

from typing import Dict, Any, List, Optional
import logging
from src.agents.core_agents import (
    SaphiraCore,
    AgentZero,
    AgentTwo,
    Aura,
    NovaReign,
    NovaAethrea,
)

logger = logging.getLogger("SaphiraOrchestrator")


def _avatar_state_for(final: Dict[str, Any], intent: str = "general") -> str:
    """Map pipeline outcome → SaphiraAvatarView state."""
    status = final.get("status", "")
    if status == "needs_confirmation":
        return "confirm"
    if status in ("blocked", "rejected"):
        return "thinking"
    if status == "scene_executed":
        return "glow"
    if intent in ("general",) or status == "success":
        return "talking"
    if intent not in ("general", "activate_scene"):
        return "talking"
    return "idle"


class SaphiraOrchestrator:
    """
    Runs the complete multi-agent pipeline:

    1. Saphira     – NLP + intent parsing
    2. Aura        – perception / room / entity context
    3. Agent Two   – security gate
    4. Nova Reign  – governance / policy
    5. NovaAethrea – memory + scene expansion
    6. Agent Zero  – final execution (Matter / HA / system / nodes)
    """

    def __init__(self, router=None):
        self.saphira = SaphiraCore(router)
        self.aura = Aura(router)
        self.agent_two = AgentTwo(router)
        self.nova_reign = NovaReign(router)
        self.nova_aethrea = NovaAethrea(router)
        self.agent_zero = AgentZero(router)

    async def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        trace: List[Dict[str, Any]] = []

        # ---- 1. Saphira: NLP + intent ----
        saphira_result = await self.saphira.safe_run({
            "text": user_input,
            "message": user_input,
            **context,
        })
        trace.append(saphira_result)
        if saphira_result.get("status") not in ("success", "recovered_from_failure"):
            return self._finalize(trace, saphira_result, intent="general")

        payload = saphira_result.get("payload", {"text": user_input})
        intent = payload.get("intent") or saphira_result.get("parsed_intent", {}).get("intent", "general")

        # ---- 2. Aura: perception & entity suggestions ----
        aura_result = await self.aura.safe_run({
            **payload,
            "context": context,
            "intent": intent,
        })
        trace.append(aura_result)

        params = payload.get("params", {})
        if not params.get("entity_id") and aura_result.get("suggested_entities"):
            params["entity_id"] = aura_result["suggested_entities"][0]
            payload["params"] = params

        # ---- 3. Agent Two: security ----
        security_result = await self.agent_two.safe_run({
            **payload,
            "intent": intent,
            "confirmed": context.get("confirmed", False),
        })
        trace.append(security_result)
        if security_result.get("status") == "blocked":
            return self._finalize(trace, {
                "status": "needs_confirmation",
                "message": security_result.get("message"),
                "intent": intent,
            }, intent=intent)

        # ---- 4. Nova Reign: governance ----
        governance_result = await self.nova_reign.safe_run({
            **payload,
            "intent": intent,
        })
        trace.append(governance_result)
        if governance_result.get("status") == "rejected":
            return self._finalize(trace, governance_result, intent=intent)

        # ---- 5. NovaAethrea: memory + scenes ----
        memory_result = await self.nova_aethrea.safe_run({
            **payload,
            "intent": intent,
            "scene": payload.get("matched_phrase") or intent,
        })
        trace.append(memory_result)

        if memory_result.get("status") == "scene_ready":
            step_results = []
            for step in memory_result.get("steps", []):
                step_payload = {
                    "intent": step["intent"],
                    "params": step.get("params", {}),
                    "confirmed": True,
                }
                exec_result = await self.agent_zero.safe_run(step_payload)
                step_results.append(exec_result)
            return self._finalize(trace, {
                "status": "scene_executed",
                "scene": memory_result.get("scene"),
                "steps": step_results,
                "message": f"Scene '{memory_result.get('scene')}' completed.",
            }, intent=intent)

        # ---- 6. Agent Zero: single action / node execution ----
        if intent not in ("general", "activate_scene"):
            exec_result = await self.agent_zero.safe_run({
                **payload,
                "intent": intent,
                "params": params,
            })
            trace.append(exec_result)
            return self._finalize(trace, exec_result, intent=intent)

        return self._finalize(trace, {
            "status": "success",
            "message": "Request processed. No device action required.",
            "intent": intent,
            "memory": memory_result,
        }, intent=intent)

    def _finalize(
        self,
        trace: List[Dict[str, Any]],
        final: Dict[str, Any],
        intent: str = "general",
    ) -> Dict[str, Any]:
        avatar_state = _avatar_state_for(final, intent)
        return {
            "final": final,
            "trace": trace,
            "agents_involved": [t.get("agent") for t in trace if t.get("agent")],
            "avatar_state": avatar_state,
            "owner": "Chelsea Megan Woods",
        }
