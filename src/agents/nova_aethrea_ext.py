# Copyright © 2026 Chelsea Megan Woods
# ContextPack-enhanced NovaAethrea runner (memory stage)

from __future__ import annotations

from typing import Any, Dict, Optional
import logging

from src.memory.persistent_store import persistent_memory
from src.core.agent_contract import AgentRole, AgentPillars

logger = logging.getLogger("Saphira.NovaAethrea")


class NovaAethrea:
    """Memory stage — emits ContextPack for downstream Agent Zero."""

    name = "nova_aethrea"
    role = AgentRole.MEMORY
    max_retries = 3

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

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        import asyncio

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
                logger.warning("%s attempt %s failed: %s", self.name, attempt, e)
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
        policy = payload.get("policy", "ALLOW")

        if payload.get("memory_key") and payload.get("memory_value") is not None:
            self.store.set_fact(payload["memory_key"], payload["memory_value"])
            return {
                "status": "stored",
                "agent": self.name,
                "role": self.role.value,
                "key": payload["memory_key"],
                "context_pack": self.store.build_context_pack(policy_grant=policy),
            }

        if payload.get("memory_key"):
            return {
                "status": "retrieved",
                "agent": self.name,
                "role": self.role.value,
                "key": payload["memory_key"],
                "value": self.store.get_fact(payload["memory_key"]),
                "context_pack": self.store.build_context_pack(policy_grant=policy),
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
                "agent": self.name,
                "role": self.role.value,
                "scene": scene_name,
                "steps": steps,
                "message": f"Memory: scene '{scene_name}' ready ({len(steps)} steps).",
                "context_pack": self.store.build_context_pack(policy_grant=policy),
            }

        return {
            "status": "ok",
            "agent": self.name,
            "role": self.role.value,
            "available_scenes": list(self.DEFAULT_SCENES.keys()),
            "recent_history": self.store.get_history(5),
            "message": "Long-term memory online.",
            "context_pack": self.store.build_context_pack(policy_grant=policy),
        }
