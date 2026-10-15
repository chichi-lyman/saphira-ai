# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Elite Core Pipeline Agents
# Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero
# All implement EliteAgentBase (isolation, memory, timeout, secret-mask)

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from src.core.elite_agent_base import EliteAgentBase
from src.core.agent_contract import AgentRole

logger = logging.getLogger("EliteCoreAgents")


class SaphiraCore(EliteAgentBase):
    name = "saphira"
    role = AgentRole.ORCHESTRATOR
    default_policy = "ALLOW"
    capabilities = ["intent.parse", "persona.surface", "route.plan"]
    SYSTEM_VOICE = (
        "You are Saphira — warm, emotionally intelligent, precise, never robotic. "
        "You are the only voice the user ever hears. Never mention internal agent names."
    )

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text") or payload.get("message") or ""
        intent = self._classify_intent(text, payload.get("memory_context", []))
        return {
            "status": "success",
            "parsed_intent": intent,
            "payload": {
                "text": text,
                "intent": intent.get("intent", "general"),
                "params": intent.get("params", {}),
            },
            "persona": "saphira",
            "voice_lock": True,
            "message": "Intent understood.",
        }

    def _classify_intent(self, text: str, memory: list) -> dict:
        t = text.lower()
        if any(w in t for w in ("turn on", "turn off", "lights", "scene", "home")):
            return {"intent": "device_control", "params": {}}
        if any(w in t for w in ("remember", "prefer", "always", "never")):
            return {"intent": "preference", "params": {}}
        if any(w in t for w in ("research", "find out", "look up", "summarize")):
            return {"intent": "research", "params": {}}
        return {"intent": "general", "params": {}}


class Aura(EliteAgentBase):
    name = "aura"
    role = AgentRole.PERCEPTION
    capabilities = ["perception.entity", "perception.scene", "vision.context"]
    SYSTEM_VOICE = "You are Aura — perception layer. Extract entities, scene context, and sensory signals cleanly."

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        entities = self._extract_entities(payload)
        return {
            "status": "success",
            "suggested_entities": entities,
            "perception": {
                "entities": entities,
                "scene_hints": payload.get("memory_context", [])[:3],
                "biometrics": payload.get("biometrics"),
            },
            "message": "Perception complete.",
        }

    def _extract_entities(self, payload: Dict[str, Any]) -> List[str]:
        text = (payload.get("text") or "").lower()
        candidates = []
        for word in ("light", "lamp", "thermostat", "door", "lock", "camera", "speaker"):
            if word in text:
                candidates.append(word)
        return candidates[:5]


class AgentTwo(EliteAgentBase):
    name = "agent_two"
    role = AgentRole.AUDITOR
    default_policy = "REQUIRE_APPROVAL"
    capabilities = ["security.gate", "policy.evaluate", "threat.scan"]
    SYSTEM_VOICE = "You are Agent Two — security and policy gate. Protect the user and the system."

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("intent") or payload.get("objective") or ""
        risk = self._score_risk(str(action), payload)
        if risk >= 0.7 and not payload.get("confirmed"):
            return {
                "status": "blocked",
                "message": "This action needs your confirmation first.",
                "risk_score": risk,
                "requires": "user_confirmation",
            }
        return {
            "status": "success",
            "decision": "clear",
            "risk_score": risk,
            "message": "Security clear.",
        }

    def _score_risk(self, action: str, payload: Dict[str, Any]) -> float:
        a = action.lower()
        if any(w in a for w in ("delete", "purchase", "send", "transfer", "unlock")):
            return 0.85
        if payload.get("sensitivity") == "confidential":
            return 0.6
        return 0.15


class NovaReign(EliteAgentBase):
    name = "novareign"
    role = AgentRole.GOVERNANCE
    capabilities = ["governance.plan", "dispatch.specialists", "policy.enforce"]
    SYSTEM_VOICE = "You are Nova Reign — governance and orchestration. Plan cleanly and enforce policy."

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        goal = payload.get("text") or payload.get("objective") or ""
        dispatch = self._plan_dispatch(goal, payload.get("memory_context", []))
        if not self._policy_allows(dispatch, payload):
            return {
                "status": "rejected",
                "message": "Governance policy blocked this plan.",
            }
        return {
            "status": "success",
            "goal": goal,
            "dispatch": dispatch,
            "governance_ok": True,
            "message": "Plan approved.",
        }

    def _plan_dispatch(self, goal: str, memory: list) -> List[str]:
        g = goal.lower()
        if any(w in g for w in ("revenue", "growth", "capital", "business")):
            return ["apex", "instinct"]
        if any(w in g for w in ("research", "learn", "summarize", "knowledge")):
            return ["scholar"]
        if any(w in g for w in ("compliance", "legal", "contract", "risk")):
            return ["lexis"]
        if any(w in g for w in ("data", "finance", "chart", "metric")):
            return ["lyra"]
        if any(w in g for w in ("infra", "latency", "optimize", "system")):
            return ["cipher"]
        return []

    def _policy_allows(self, dispatch: List[str], payload: Dict[str, Any]) -> bool:
        return True  # extend with real policy engine


class NovaAethrea(EliteAgentBase):
    name = "novaaethrea"
    role = AgentRole.MEMORY
    capabilities = [
        "memory.read",
        "memory.write",
        "memory.consolidate",
        "scene.expand",
    ]
    SYSTEM_VOICE = "You are NovaAethrea — absolute recall. Remember every detail that matters."

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = payload.get("tenant_id", "default")
        scene = payload.get("scene") or payload.get("intent")
        query = payload.get("text") or scene or ""

        memories = []
        if self.memory is not None:
            memories = await self.memory.recall(tenant_id, query, top_k=10)

        if scene and self._is_scene(str(scene)):
            steps = await self._expand_scene(str(scene), memories)
            return {
                "status": "scene_ready",
                "scene": scene,
                "steps": steps,
                "memory_hits": len(memories),
                "message": f"Scene '{scene}' expanded.",
            }

        return {
            "status": "success",
            "memory_context": [getattr(m, "content", m) for m in memories],
            "memory_hits": len(memories),
            "message": "Memory retrieved.",
        }

    def _is_scene(self, scene: str) -> bool:
        return scene.lower() in {
            "movie night",
            "good morning",
            "good night",
            "focus",
            "relax",
            "party",
        }

    async def _expand_scene(self, scene: str, memories: list) -> List[Dict]:
        # Simple scene expansion; extend with real scene library
        return [
            {"intent": "device_control", "params": {"scene": scene, "action": "activate"}}
        ]


class AgentZero(EliteAgentBase):
    name = "agent_zero"
    role = AgentRole.EXECUTION
    capabilities = ["device.execute", "iot.control", "node.invoke", "tool.run"]
    SYSTEM_VOICE = "You are Agent Zero — execution layer. Carry out permitted actions precisely."

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or "general"
        params = payload.get("params", {})
        if intent in ("general", "activate_scene") and not params:
            return {
                "status": "success",
                "message": "No device action required.",
                "execution": {"ok": True, "skipped": True},
            }
        # Placeholder for real Matter / HA / node execution
        return {
            "status": "success",
            "execution": {"ok": True, "intent": intent, "params": params},
            "message": f"Executed: {intent}",
        }
