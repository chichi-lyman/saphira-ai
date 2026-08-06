# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Public catalog of Saphira core features and implementation status.

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter

from src.core.features import CORE_FEATURES, feature_summary, features_by_layer
from src.core.model_router import model_router
from src.core.tool_registry import tool_registry
from src.core.memory_layers import session_memory, persistent_memory
from src.core.tone_engine import ToneMode, TONE_DIRECTIVES

router = APIRouter(prefix="/features", tags=["features"])


@router.get("")
async def list_features(layer: Optional[str] = None) -> Dict[str, Any]:
    if layer:
        return {
            "layer": layer,
            "features": features_by_layer().get(layer, []),
            "summary": feature_summary(),
        }
    return {
        "summary": feature_summary(),
        "features": CORE_FEATURES,
        "by_layer": features_by_layer(),
        "owner": "Chelsea Megan Woods",
    }


@router.get("/status")
async def runtime_status() -> Dict[str, Any]:
    return {
        "summary": feature_summary(),
        "model_router": model_router.status(),
        "tools": tool_registry.list_tools(),
        "memory": {
            "session": "active",
            "persistent": persistent_memory.snapshot(),
        },
        "tone_modes": list(TONE_DIRECTIVES.keys()),
        "owner": "Chelsea Megan Woods",
    }
