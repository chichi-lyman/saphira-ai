# Copyright © 2026 Chelsea Megan Woods
# ContextPack-enhanced NovaAethrea runner (memory stage)
# Extended with consented face memory.

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from src.memory.persistent_store import persistent_memory
from src.core.agent_contract import AgentRole, AgentPillars

logger = logging.getLogger("Saphira.NovaAethrea")


class NovaAethrea:
    """Memory stage — emits ContextPack for downstream Agent Zero + face ledger."""

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
        intent = payload.get("intent", "")

        # ---- Face memory intents ----
        if intent == "face_list":
            faces = self.store.list_faces()
            safe = [{"label": f.get("label"), "metadata": f.get("metadata", {})} for f in faces]
            return {
                "status": "ok",
                "agent": self.name,
                "faces": safe,
                "message": f"{len(safe)} face(s) in memory.",
                "context_pack": self.store.build_context_pack(policy_grant=policy) if hasattr(self.store, "build_context_pack") else {},
            }

        if intent == "face_forget":
            label = (payload.get("params") or {}).get("label") or payload.get("label")
            if not label:
                return {
                    "status": "error",
                    "agent": self.name,
                    "message": "No label provided to forget.",
                }
            removed = self.store.delete_face(label)
            return {
                "status": "ok" if removed else "not_found",
                "agent": self.name,
                "label": label,
                "message": f"Forgot face '{label}'." if removed else f"No face named '{label}'.",
            }

        if intent == "face_enroll":
            params = payload.get("params") or {}
            label = params.get("label") or payload.get("label")
            embedding = params.get("embedding") or payload.get("embedding")
            consent_token = params.get("consent_token") or payload.get("consent_token")
            if not consent_token:
                return {
                    "status": "consent_required",
                    "agent": self.name,
                    "message": "Explicit consent required before storing a face.",
                }
            if not label or not embedding:
                return {
                    "status": "error",
                    "agent": self.name,
                    "message": "label and embedding are required for enrollment.",
                }
            self.store.set_face(
                label,
                {
                    "label": label,
                    "embedding": embedding,
                    "consent_token": consent_token,
                    "metadata": params.get("metadata") or {},
                },
            )
            return {
                "status": "stored",
                "agent": self.name,
                "label": label,
                "message": f"Stored face as '{label}'.",
            }

        # ---- Generic memory write / read ----
        if payload.get("memory_key") and payload.get("memory_value") is not None:
            self.store.set_fact(payload["memory_key"], payload["memory_value"])
            return {
                "status": "stored",
                "agent": self.name,
                "role": self.role.value,
                "key": payload["memory_key"],
                "context_pack": self.store.build_context_pack(policy_grant=policy) if hasattr(self.store, "build_context_pack") else {},
            }

        if payload.get("memory_key"):
            return {
                "status": "retrieved",
                "agent": self.name,
                "role": self.role.value,
                "key": payload["memory_key"],
                "value": self.store.get_fact(payload["memory_key"]),
                "context_pack": self.store.build_context_pack(policy_grant=policy) if hasattr(self.store, "build_context_pack") else {},
            }

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
                "context_pack": self.store.build_context_pack(policy_grant=policy) if hasattr(self.store, "build_context_pack") else {},
            }

        return {
            "status": "ok",
            "agent": self.name,
            "role": self.role.value,
            "available_scenes": list(self.DEFAULT_SCENES.keys()),
            "recent_history": self.store.get_history(5),
            "known_faces": [f.get("label") for f in self.store.list_faces()],
            "message": "Long-term memory online.",
            "context_pack": self.store.build_context_pack(policy_grant=policy) if hasattr(self.store, "build_context_pack") else {},
        }

    def get_known_faces_for_perception(self) -> List[Dict[str, Any]]:
        return [
            {"label": f["label"], "embedding": f["embedding"]}
            for f in self.store.list_faces()
            if "embedding" in f
        ]
