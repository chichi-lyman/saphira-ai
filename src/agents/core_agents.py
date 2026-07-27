# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Six Core Agents — Fully Expanded
# Saphira | Agent Zero | Agent Two | Aura | Nova Reign | NovaAethrea

from typing import Dict, Any, List, Optional
import logging
import traceback
import asyncio
import re
from src.connectors.matter_home_assistant import matter_ha
from src.memory.persistent_store import persistent_memory

logger = logging.getLogger("SaphiraCoreAgents")


class SelfHealingAgent:
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
            "message": f"{self.name} recovered after failures.",
        }

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 1. Saphira — NLP + Intent
# ---------------------------------------------------------------------------
class SaphiraCore(SelfHealingAgent):
    name = "saphira"

    VOICE_PATTERNS = [
        (r"\b(turn on|switch on|lights? on)\b", "turn_on"),
        (r"\b(turn off|switch off|lights? off)\b", "turn_off"),
        (r"\b(dim|set brightness|brightness)\b", "set_brightness"),
        (r"\b(set (the )?temperature|thermostat|make it (warmer|cooler))\b", "set_temperature"),
        (r"\b(lock (the )?(front )?door)\b", "lock"),
        (r"\b(unlock (the )?(front )?door)\b", "unlock"),
        (r"\b(close (the )?(blinds|shades)|open (the )?(blinds|shades))\b", "set_cover"),
        (r"\b(good night|evening scene|movie mode|i'?m home|i am home)\b", "activate_scene"),
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
            "parsed_intent": parsed,
            "payload": {**payload, **parsed},
            "message": "Intent parsed.",
        }


# ---------------------------------------------------------------------------
# 2. Agent Zero — Execution
# ---------------------------------------------------------------------------
class AgentZero(SelfHealingAgent):
    name = "agent_zero"

    def __init__(self, router=None):
        self.router = router
        self.matter = matter_ha

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "")
        params = payload.get("params", {})

        if intent == "activate_scene":
            return {"status": "delegated", "agent": "agent_zero", "message": "Scenes handled by NovaAethrea."}

        if intent in ("turn_on", "turn_off", "toggle", "set_brightness",
                      "set_temperature", "lock", "unlock", "set_cover", "matter"):
            result = self.matter.execute_intent(intent, params)
            return {"status": result.get("status", "unknown"), "agent": "agent_zero", "intent": intent, "result": result}

        return {"status": "accepted", "agent": "agent_zero", "message": f"Received: {intent}", "params": params}


# ---------------------------------------------------------------------------
# 3. Agent Two — Security
# ---------------------------------------------------------------------------
class AgentTwo(SelfHealingAgent):
    name = "agent_two"
    SENSITIVE = {"unlock", "lock"}

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "")
        confirmed = payload.get("confirmed", False)
        if intent in self.SENSITIVE and not confirmed:
            return {
                "status": "blocked",
                "agent": "agent_two",
                "message": f"Security: '{intent}' needs explicit confirmation.",
                "requires_confirmation": True,
            }
        return {"status": "cleared", "agent": "agent_two", "intent": intent}


# ---------------------------------------------------------------------------
# 4. Aura — Full Perception (expanded)
# ---------------------------------------------------------------------------
class Aura(SelfHealingAgent):
    name = "aura"

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

        suggested = self._suggest_entities(room, text)

        return {
            "status": "success",
            "agent": "aura",
            "room": room,
            "vision_summary": vision or "No visual input.",
            "suggested_entities": suggested,
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
        # fallback keyword scan
        for room, entities in self.ROOM_ENTITIES.items():
            if room in text:
                return entities
        return []


# ---------------------------------------------------------------------------
# 5. Nova Reign — Governance
# ---------------------------------------------------------------------------
class NovaReign(SelfHealingAgent):
    name = "nova_reign"
    ALLOWED = {
        "turn_on", "turn_off", "toggle", "set_brightness",
        "set_temperature", "lock", "unlock", "set_cover",
        "activate_scene", "general", "matter",
    }

    def __init__(self, router=None):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = payload.get("intent") or payload.get("action", "general")
        if intent not in self.ALLOWED:
            return {
                "status": "rejected",
                "agent": "nova_reign",
                "message": f"Policy: intent '{intent}' not allowed.",
            }
        return {"status": "approved", "agent": "nova_reign", "intent": intent}


# ---------------------------------------------------------------------------
# 6. NovaAethrea — Persistent Memory + Scenes
# ---------------------------------------------------------------------------
class NovaAethrea(SelfHealingAgent):
    name = "nova_aethrea"

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
        # seed default scenes if missing
        for name, steps in self.DEFAULT_SCENES.items():
            if not self.store.get_scene(name):
                self.store.save_scene(name, steps)

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Write fact / preference
        if payload.get("memory_key") and payload.get("memory_value") is not None:
            self.store.set_fact(payload["memory_key"], payload["memory_value"])
            return {"status": "stored", "agent": "nova_aethrea", "key": payload["memory_key"]}

        if payload.get("memory_key"):
            return {
                "status": "retrieved",
                "agent": "nova_aethrea",
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
                "scene": scene_name,
                "steps": steps,
                "message": f"Scene '{scene_name}' ready ({len(steps)} steps).",
            }

        return {
            "status": "ok",
            "agent": "nova_aethrea",
            "available_scenes": list(self.DEFAULT_SCENES.keys()),
            "recent_history": self.store.get_history(5),
        }


CORE_AGENTS = {
    "saphira": SaphiraCore,
    "agent_zero": AgentZero,
    "agent_two": AgentTwo,
    "aura": Aura,
    "nova_reign": NovaReign,
    "nova_aethrea": NovaAethrea,
}
