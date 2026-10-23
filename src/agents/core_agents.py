# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Six Core Agents — aligned with AI/Agent anatomy & taxonomy
# Saphira | Agent Zero | Agent Two | Aura | Nova Reign | NovaAethrea
# Agent Zero also routes node invokes (code / canvas / camera / system).

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
# 1. Saphira — Orchestrator
# ---------------------------------------------------------------------------
class SaphiraCore(SelfHealingAgent):
    name = "saphira"
    role = AgentRole.ORCHESTRATOR

    VOICE_PATTERNS = [
        (r"\b(turn on|switch on|lights? on)\b", "turn_on"),
        (r"\b(turn off|switch off|lights? off)\b", "turn_off"),
        (r"\b(dim|set brightness|brightness)\b", "set_brightness"),
        (r"\b(set (the )?temperature|thermostat|make it (warmer|cooler))\b", "set_temperature"),
        (r"\b(lock (the )?(front )?door)\b", "lock"),
        (r"\b(unlock (the )?(front )?door)\b", "unlock"),
        (r"\b(close (the )?(blinds|shades)|open (the )?(blinds|shades))\b", "set_cover"),
        (r"\b(good night|evening scene|movie mode|i'?m home|i am home)\b", "activate_scene"),
        # Node / physical agency patterns
        (r"\b(take a (photo|picture|selfie)|snap (a )?(photo|pic)|camera)\b", "node_snap"),
        (r"\b(show (me )?(a )?dashboard|mission control|visual briefing)\b", "node_dashboard"),
        (r"\b(run (the )?tests?|pytest|test suite)\b", "node_test"),
        (r"\b(open (a )?pr|pull request|push (the )?code)\b", "node_pr"),
        (r"\b(spin up|create).*(env|environment|postgres|redis)\b", "node_env"),
        (r"\b(render|animate).*(chart|graph|viz)\b", "node_media_viz"),
        (r"\b(make|render).*(intro|video clip)\b", "node_media_video"),
    ]

    def __init__(self, router=None):
        self.router = router

    def parse_voice_intent(self, text: str) -> Dict[str, Any]:
        text_l = text.lower().strip()
        for pattern, intent in self.VOICE_PATTERNS:
            if re.search(pattern, text_l):
                return {"intent": intent, "raw": text, "matched": pattern}
        return {"intent": "general", "raw": text, "matched": None}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text") or payload.get("message") or ""
        parsed = self.parse_voice_intent(text) if text else {
            "intent": payload.get("intent", "general"),
            "raw": text,
        }
        return {
            "status": "success",
            "agent": "saphira",
            "role": self.role.value,
            "parsed_intent": parsed,
            "payload": {**payload, **parsed},
            "message": "Orchestrator: intent parsed; ready to delegate.",
            "next_agents": ["aura", "agent_two", "nova_reign", "nova_aethrea", "agent_zero"],
            "identity": self.identity(),
        }


# ---------------------------------------------------------------------------
# 2. Agent Zero — Execution (+ Nodes)
# ---------------------------------------------------------------------------
class AgentZero(SelfHealingAgent):
    name = "agent_zero"
    role = AgentRole.EXECUTION

    def __init__(self, router=None):
        self.router = router
        self.matter = matter_ha

    async def _invoke_node(self, command: str, params: Optional[Dict[str, Any]] = None,
                           preferred_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            from src.nodes.invoke import node_invoker
            return await node_invoker.invoke_any(command, params or {}, preferred_type=preferred_type)
        except Exception as e:
            logger.warning("Node invoke failed: %s", e)
            return {"status": "error", "error": str(e), "command": command}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "")
        params = payload.get("params", {})

        if intent == "activate_scene":
            return {
                "status": "delegated",
                "agent": "agent_zero",
                "role": self.role.value,
                "message": "Scenes handled by NovaAethrea then executed here as steps.",
            }

        # --- Node surfaces ---
        if intent == "node_snap":
            result = await self._invoke_node("camera.snap", {"facing": params.get("facing", "front")}, "mobile_android")
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result, "message": "Camera snap requested on a capable node."}

        if intent == "node_dashboard":
            result = await self._invoke_node(
                "canvas.dashboard",
                {"title": params.get("title", "Saphira Mission Control"),
                 "sources": params.get("sources", ["calendar", "notion", "todos"])},
                "canvas",
            )
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result}

        if intent == "node_test":
            result = await self._invoke_node("code.test", {"suite": params.get("suite", "pytest")}, "headless")
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result}

        if intent == "node_pr":
            result = await self._invoke_node(
                "code.pr",
                {"title": params.get("title", "Saphira automated PR"),
                 "branch": params.get("branch", "saphira/auto")},
                "headless",
            )
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result}

        if intent == "node_env":
            result = await self._invoke_node(
                "code.env",
                {"name": params.get("name", "saphira-dev"),
                 "services": params.get("services", ["postgres", "redis"])},
                "headless",
            )
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result}

        if intent == "node_media_viz":
            result = await self._invoke_node(
                "media.viz",
                {"type": params.get("type", "bar"), "title": params.get("title", "Saphira Viz"),
                 "data": params.get("data", [])},
                "media",
            )
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result}

        if intent == "node_media_video":
            result = await self._invoke_node(
                "media.video",
                {"text": params.get("text", "Saphira"), "duration_sec": params.get("duration_sec", 5),
                 "style": params.get("style", "gradient_fade")},
                "media",
            )
            return {"status": result.get("status", "ok"), "agent": "agent_zero", "role": self.role.value,
                    "intent": intent, "node_result": result}

        # --- Matter / HA ---
        if intent in (
            "turn_on", "turn_off", "toggle", "set_brightness", "set_color",
            "set_temperature", "set_hvac_mode", "lock", "unlock",
            "set_cover", "open_cover", "close_cover",
            "media_play", "media_pause", "media_stop", "media_volume",
            "fan_percentage", "fan_preset", "activate_scene", "matter",
        ):
            result = self.matter.execute_intent(intent, params)
            return {
                "status": result.get("status", "unknown"),
                "agent": "agent_zero",
                "role": self.role.value,
                "intent": intent,
                "result": result,
            }

        return {
            "status": "accepted",
            "agent": "agent_zero",
            "role": self.role.value,
            "message": f"Execution request received: {intent}",
            "params": params,
        }


# ---------------------------------------------------------------------------
# 3. Agent Two — Auditor / Security
# ---------------------------------------------------------------------------
class AgentTwo(SelfHealingAgent):
    name = "agent_two"
    role = AgentRole.AUDITOR
    SENSITIVE = {"unlock", "lock", "node_pr", "system.sms"}

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "")
        confirmed = payload.get("confirmed", False)
        if intent in self.SENSITIVE and not confirmed:
            return {
                "status": "blocked",
                "agent": "agent_two",
                "role": self.role.value,
                "message": f"Auditor: '{intent}' requires explicit confirmation.",
                "requires_confirmation": True,
            }
        return {
            "status": "cleared",
            "agent": "agent_two",
            "role": self.role.value,
            "intent": intent,
            "message": "Auditor: security check passed.",
        }


# ---------------------------------------------------------------------------
# 4. Aura — Perception
# ---------------------------------------------------------------------------
class Aura(SelfHealingAgent):
    name = "aura"
    role = AgentRole.PERCEPTION

    ROOM_ENTITIES = {
        "living": ["light.living_room", "media_player.living_room", "cover.living_blinds"],
        "kitchen": ["light.kitchen", "switch.kitchen_fan"],
        "bedroom": ["light.bedroom", "cover.bedroom_blinds"],
        "front": ["lock.front_door", "light.porch"],
        "office": ["light.office", "switch.office_fan"],
    }

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context", {})
        text = (payload.get("text") or payload.get("raw") or "").lower()
        room = context.get("room") or self._detect_room(text)
        vision = payload.get("vision") or context.get("vision")

        return {
            "status": "success",
            "agent": "aura",
            "role": self.role.value,
            "room": room,
            "vision_summary": vision or "No visual input.",
            "suggested_entities": self._suggest_entities(room, text),
            "perception_note": perception_pipeline_note(),
            "message": "Perception complete.",
        }

    def _detect_room(self, text: str) -> Optional[str]:
        for room in self.ROOM_ENTITIES:
            if room in text:
                return room
        return None

    def _suggest_entities(self, room: Optional[str], text: str) -> List[str]:
        if room and room in self.ROOM_ENTITIES:
            return self.ROOM_ENTITIES[room]
        for room, entities in self.ROOM_ENTITIES.items():
            if room in text:
                return entities
        return []


# ---------------------------------------------------------------------------
# 5. Nova Reign — Governance
# ---------------------------------------------------------------------------
class NovaReign(SelfHealingAgent):
    name = "nova_reign"
    role = AgentRole.GOVERNANCE
    ALLOWED = {
        "turn_on", "turn_off", "toggle", "set_brightness", "set_color",
        "set_temperature", "set_hvac_mode", "lock", "unlock",
        "set_cover", "open_cover", "close_cover",
        "media_play", "media_pause", "media_stop", "media_volume",
        "fan_percentage", "fan_preset", "activate_scene", "general", "matter",
        # Node intents
        "node_snap", "node_dashboard", "node_test", "node_pr", "node_env",
        "node_media_viz", "node_media_video", "node_code", "node_exec",
        "node_canvas", "node_camera", "node_notify",
    }

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "general")
        if intent not in self.ALLOWED:
            return {
                "status": "rejected",
                "agent": "nova_reign",
                "role": self.role.value,
                "message": f"Governance: intent '{intent}' not allowed.",
            }
        return {
            "status": "approved",
            "agent": "nova_reign",
            "role": self.role.value,
            "intent": intent,
            "message": "Governance: policy check passed.",
        }


# ---------------------------------------------------------------------------
# 6. NovaAethrea — Memory
# ---------------------------------------------------------------------------
class NovaAethrea(SelfHealingAgent):
    name = "nova_aethrea"
    role = AgentRole.MEMORY

    DEFAULT_SCENES = {
        "evening": [
            {"intent": "set_brightness", "params": {"entity_id": "light.living_room", "brightness_pct": 30}},
            {"intent": "set_temperature", "params": {"entity_id": "climate.main", "temperature": 71}},
        ],
        "good_night": [
            {"intent": "turn_off", "params": {"entity_id": "light.living_room"}},
            {"intent": "turn_off", "params": {"entity_id": "light.kitchen"}},
            {"intent": "lock", "params": {"entity_id": "lock.front_door"}},
            {"intent": "set_temperature", "params": {"entity_id": "climate.main", "temperature": 68}},
        ],
        "movie": [
            {"intent": "set_brightness", "params": {"entity_id": "light.living_room", "brightness_pct": 10}},
            {"intent": "set_cover", "params": {"entity_id": "cover.living_blinds", "position": 0}},
        ],
        "im_home": [
            {"intent": "turn_on", "params": {"entity_id": "light.living_room"}},
            {"intent": "set_brightness", "params": {"entity_id": "light.living_room", "brightness_pct": 70}},
            {"intent": "set_temperature", "params": {"entity_id": "climate.main", "temperature": 72}},
        ],
    }

    def __init__(self, router=None):
        self.router = router
        self.store = persistent_memory
        for name, steps in self.DEFAULT_SCENES.items():
            if not self.store.get_scene(name):
                self.store.save_scene(name, steps)

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if payload.get("memory_key") and payload.get("memory_value") is not None:
            self.store.set_fact(payload["memory_key"], payload["memory_value"])
            return {"status": "stored", "agent": "nova_aethrea", "role": self.role.value, "key": payload["memory_key"]}

        if payload.get("memory_key"):
            return {
                "status": "retrieved",
                "agent": "nova_aethrea",
                "role": self.role.value,
                "key": payload["memory_key"],
                "value": self.store.get_fact(payload["memory_key"]),
            }

        intent = payload.get("intent", "")
        scene_hint = (payload.get("scene") or payload.get("matched") or payload.get("raw") or "").lower()

        scene_name = None
        if intent == "activate_scene" or any(s in scene_hint for s in self.DEFAULT_SCENES):
            if "evening" in scene_hint:
                scene_name = "evening"
            elif "night" in scene_hint:
                scene_name = "good_night"
            elif "movie" in scene_hint:
                scene_name = "movie"
            elif "home" in scene_hint:
                scene_name = "im_home"

        if scene_name:
            steps = self.store.get_scene(scene_name) or self.DEFAULT_SCENES.get(scene_name, [])
            self.store.append_history({"type": "scene", "name": scene_name})
            return {
                "status": "scene_ready",
                "agent": "nova_aethrea",
                "role": self.role.value,
                "scene": scene_name,
                "steps": steps,
                "message": f"Memory: scene '{scene_name}' ready ({len(steps)} steps).",
            }

        return {
            "status": "ok",
            "agent": "nova_aethrea",
            "role": self.role.value,
            "available_scenes": list(self.DEFAULT_SCENES.keys()),
            "recent_history": self.store.get_history(5),
            "message": "Long-term memory online.",
        }


CORE_AGENTS = {
    "saphira": SaphiraCore,
    "agent_zero": AgentZero,
    "agent_two": AgentTwo,
    "aura": Aura,
    "nova_reign": NovaReign,
    "nova_aethrea": NovaAethrea,
}


def all_agent_identities() -> Dict[str, Any]:
    return {name: describe_agent(name) for name in CORE_AGENTS}
