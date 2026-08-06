# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Multi-model routing: local / fast / heavy with fallback.

from __future__ import annotations

import os
from enum import Enum
from typing import Any, Dict, List, Optional


class ModelTier(str, Enum):
    LOCAL = "local"      # on-device / WebGPU / small local LLM
    FAST = "fast"        # Flash-class cloud APIs
    HEAVY = "heavy"      # deep reasoning / long context


# Default preference order per task class
TASK_ROUTING: Dict[str, List[str]] = {
    "device_command": [ModelTier.LOCAL.value, ModelTier.FAST.value],
    "chitchat": [ModelTier.FAST.value, ModelTier.LOCAL.value],
    "lookup": [ModelTier.FAST.value, ModelTier.HEAVY.value],
    "research": [ModelTier.HEAVY.value, ModelTier.FAST.value],
    "code": [ModelTier.HEAVY.value, ModelTier.FAST.value],
    "planning": [ModelTier.HEAVY.value, ModelTier.FAST.value],
    "voice_reply": [ModelTier.FAST.value, ModelTier.LOCAL.value],
    "default": [ModelTier.FAST.value, ModelTier.HEAVY.value, ModelTier.LOCAL.value],
}


class ModelRouter:
    """
    Selects provider/model by task tier and available API keys.
    Does not call providers itself — returns a routing decision for callers.
    """

    def __init__(self):
        self.providers = {
            ModelTier.LOCAL.value: {
                "id": os.getenv("SAPHIRA_LOCAL_MODEL", "local-webgpu"),
                "enabled": os.getenv("ENABLE_LOCAL_MODEL", "true").lower() == "true",
                "cost": "low",
                "latency": "lowest",
            },
            ModelTier.FAST.value: {
                "id": os.getenv("SAPHIRA_FAST_MODEL", "gemini-flash"),
                "enabled": bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")),
                "cost": "medium",
                "latency": "low",
            },
            ModelTier.HEAVY.value: {
                "id": os.getenv("SAPHIRA_HEAVY_MODEL", "gemini-pro"),
                "enabled": bool(
                    os.getenv("GEMINI_API_KEY")
                    or os.getenv("OPENAI_API_KEY")
                    or os.getenv("XAI_API_KEY")
                    or os.getenv("GROK_API_KEY")
                ),
                "cost": "high",
                "latency": "higher",
            },
        }

    def route(self, task: str = "default", prefer: Optional[str] = None) -> Dict[str, Any]:
        order = list(TASK_ROUTING.get(task, TASK_ROUTING["default"]))
        if prefer and prefer in order:
            order.remove(prefer)
            order.insert(0, prefer)

        chosen = None
        fallbacks: List[str] = []
        for tier in order:
            info = self.providers.get(tier, {})
            if info.get("enabled"):
                if chosen is None:
                    chosen = {"tier": tier, **info}
                else:
                    fallbacks.append(tier)

        if chosen is None:
            # Always allow local stub so the system degrades instead of dying
            chosen = {
                "tier": ModelTier.LOCAL.value,
                "id": "local-stub",
                "enabled": True,
                "cost": "low",
                "latency": "lowest",
                "degraded": True,
            }

        return {
            "task": task,
            "primary": chosen,
            "fallbacks": fallbacks,
            "policy": "prefer_fast_for_voice_and_devices_heavy_for_research",
            "owner": "Chelsea Megan Woods",
        }

    def status(self) -> Dict[str, Any]:
        return {"providers": self.providers, "tasks": list(TASK_ROUTING.keys())}


model_router = ModelRouter()
