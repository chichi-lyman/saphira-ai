# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Six Core Agents — Expanded, Self-Healing, Highest-State Version
# Saphira | Agent Zero | Agent Two | Aura | Nova Reign | NovaAethrea

from typing import Dict, Any, List, Optional
import logging
import traceback
import asyncio
from src.connectors.matter_home_assistant import matter_ha

logger = logging.getLogger("SaphiraCoreAgents")


# ---------------------------------------------------------------------------
# Shared self-healing base
# ---------------------------------------------------------------------------
class SelfHealingAgent:
    """Base that retries, logs failures, and returns a recoverable state."""

    name = "base"
    max_retries = 3

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self.run(payload)
            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} attempt {attempt} failed: {e}")
                await asyncio.sleep(0.15 * (2 ** (attempt - 1)))
        return {
            "status": "recovered_from_failure",
            "agent": self.name,
            "error": str(last_error),
            "traceback": traceback.format_exc(),
            "message": f"{self.name} exhausted retries but returned safe state.",
        }

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 1. Saphira — Command Core
# ---------------------------------------------------------------------------
class SaphiraCore(SelfHealingAgent):
    name = "saphira"

    # Tight voice → intent mapping for smart-home and core actions
    VOICE_INTENT_MAP = {
        # lights
        "turn on": "turn_on",
        "turn off": "turn_off",
        "lights on": "turn_on",
        "lights off": "turn_off",
        "dim": "set_brightness",
        "brightness": "set_brightness",
        "set brightness": "set_brightness",
        # climate
        "set temperature": "set_temperature",
        "set the thermostat": "set_temperature",
        "make it warmer": "set_temperature",
        "make it cooler": "set_temperature",
        # locks
        "lock the door": "lock",
        "unlock the door": "unlock",
        "lock front door": "lock",
        "unlock front door": "unlock",
        # covers
        "close the blinds": "set_cover",
        "open the blinds": "set_cover",
        "close shades": "set_cover",
        # scenes
        "evening scene": "activate_scene",
        "good night": "activate_scene",
        "movie mode": "activate_scene",
        "i'm home": "activate_scene",
    }

    def __init__(self, router=None):
        self.router = router

    def parse_voice_intent(self, text: str) -> Dict[str, Any]:
        text_l = text.lower().strip()
        for phrase, intent in self.VOICE_INTENT_MAP.items():
            if phrase in text_l:
                return {"intent": intent, "raw": text, "matched_phrase": phrase}
        return {"intent": "general", "raw": text, "matched_phrase": None}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text") or payload.get("message") or ""
        parsed = self.parse_voice_intent(text) if text else {"intent": payload.get("intent", "general")}

        return {
            "status": "success",
            "agent": "saphira",
            "parsed_intent": parsed,
            "message": "Intent understood and ready for delegation.",
            "next_agents": ["agent_two", "nova_reign", "agent_zero"],
            "payload": {**payload, **parsed},
        }


# ---------------------------------------------------------------------------
# 2. Agent Zero — Execution Engine
# ---------------------------------------------------------------------------
class AgentZero(SelfHealingAgent):
    name = "agent_zero"

    def __init__(self, router=None):
        self.router = router
        self.matter = matter_ha

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "")
        params = payload.get("params", {})

        # Scene activation is handled by NovaAethrea; Agent Zero only executes device calls
        if intent == "activate_scene":
            return {
                "status": "delegated",
                "agent": "agent_zero",
                "message": "Scene activation belongs to NovaAethrea.",
            }

        if intent in (
            "turn_on", "turn_off", "toggle", "set_brightness",
            "set_temperature", "lock", "unlock", "set_cover", "matter"
        ):
            result = self.matter.execute_intent(intent, params)
            return {
                "status": result.get("status", "unknown"),
                "agent": "agent_zero",
                "intent": intent,
                "result": result,
            }

        return {
            "status": "accepted",
            "agent": "agent_zero",
            "message": f"Execution request received: {intent}",
            "params": params,
        }


# ---------------------------------------------------------------------------
# 3. Agent Two — Security Enforcer
# ---------------------------------------------------------------------------
class AgentTwo(SelfHealingAgent):
    name = "agent_two"

    SENSITIVE = {"unlock", "lock", "set_temperature"}

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "")
        confirmed = payload.get("confirmed", False)

        if intent in self.SENSITIVE and not confirmed:
            return {
                "status": "blocked",
                "agent": "agent_two",
                "message": f"Security gate: '{intent}' requires explicit user confirmation.",
                "requires_confirmation": True,
            }

        return {
            "status": "cleared",
            "agent": "agent_two",
            "message": "Security check passed.",
            "intent": intent,
        }


# ---------------------------------------------------------------------------
# 4. Aura — Multimodal Perception
# ---------------------------------------------------------------------------
class Aura(SelfHealingAgent):
    name = "aura"

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context", {})
        vision = payload.get("vision") or context.get("vision")
        room = context.get("room") or payload.get("room")

        return {
            "status": "success",
            "agent": "aura",
            "message": "Perception layer active.",
            "room": room,
            "vision_summary": vision or "No visual input this turn.",
            "suggested_entities": self._suggest_entities(room),
        }

    def _suggest_entities(self, room: Optional[str]) -> List[str]:
        if not room:
            return []
        room = room.lower()
        mapping = {
            "living": ["light.living_room", "media_player.living_room"],
            "kitchen": ["light.kitchen", "switch.kitchen_fan"],
            "bedroom": ["light.bedroom", "cover.bedroom_blinds"],
            "front": ["lock.front_door", "light.porch"],
        }
        for key, entities in mapping.items():
            if key in room:
                return entities
        return []


# ---------------------------------------------------------------------------
# 5. Nova Reign — Governance
# ---------------------------------------------------------------------------
class NovaReign(SelfHealingAgent):
    name = "nova_reign"

    def __init__(self, router=None):
        self.router = router
        self.allowed_intents = {
            "turn_on", "turn_off", "toggle", "set_brightness",
            "set_temperature", "lock", "unlock", "set_cover",
            "activate_scene", "general", "matter",
        }

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "general")
        if intent not in self.allowed_intents:
            return {
                "status": "rejected",
                "agent": "nova_reign",
                "message": f"Policy violation: intent '{intent}' is not in the approved set.",
            }
        return {
            "status": "approved",
            "agent": "nova_reign",
            "message": "Governance check passed. Action within policy.",
            "intent": intent,
        }


# ---------------------------------------------------------------------------
# 6. NovaAethrea — Persistent Memory + Scene System
# ---------------------------------------------------------------------------
class NovaAethrea(SelfHealingAgent):
    name = "nova_aethrea"

    def __init__(self, router=None):
        self.router = router
        self._memory: Dict[str, Any] = {}
        self._scenes: Dict[str, List[Dict[str, Any]]] = {
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

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Memory write
        key = payload.get("memory_key")
        value = payload.get("memory_value")
        if key and value is not None:
            self._memory[key] = value
            return {"status": "stored", "agent": "nova_aethrea", "key": key}

        # Memory read
        if key:
            return {
                "status": "retrieved",
                "agent": "nova_aethrea",
                "key": key,
                "value": self._memory.get(key),
            }

        # Scene activation
        intent = payload.get("intent", "")
        scene_name = payload.get("scene") or payload.get("matched_phrase") or ""
        scene_name = scene_name.lower().replace(" ", "_").replace("'", "")

        if intent == "activate_scene" or scene_name in self._scenes:
            # normalize common phrases
            if "evening" in scene_name:
                scene_name = "evening"
            elif "night" in scene_name or "good_night" in scene_name:
                scene_name = "good_night"
            elif "movie" in scene_name:
                scene_name = "movie"
            elif "home" in scene_name:
                scene_name = "im_home"

            steps = self._scenes.get(scene_name, [])
            return {
                "status": "scene_ready",
                "agent": "nova_aethrea",
                "scene": scene_name,
                "steps": steps,
                "message": f"Scene '{scene_name}' prepared with {len(steps)} steps.",
            }

        return {
            "status": "ok",
            "agent": "nova_aethrea",
            "memory_size": len(self._memory),
            "available_scenes": list(self._scenes.keys()),
        }

    def add_scene(self, name: str, steps: List[Dict[str, Any]]):
        self._scenes[name.lower()] = steps


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
CORE_AGENTS = {
    "saphira": SaphiraCore,
    "agent_zero": AgentZero,
    "agent_two": AgentTwo,
    "aura": Aura,
    "nova_reign": NovaReign,
    "nova_aethrea": NovaAethrea,
}
