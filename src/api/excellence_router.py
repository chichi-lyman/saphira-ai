"""Excellence execution gateway — POST /v1/router/execute

Standardized agent routing across latency, privacy, dual memory, offline,
and Nova Umbrella internal agents based on task complexity / hardware prefs.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.excellence.router import route_excellence
from src.latency.router import LatencyRouter
from src.privacy.filter import PrivacyFilter
from src.memory.ledger import dual_memory
from src.offline.fallback import OfflineFallback
from src.excellence.agent_map import pillars_for_agent

router = APIRouter(tags=["excellence-router"])

_latency = LatencyRouter()
_privacy = PrivacyFilter()
_offline = OfflineFallback()


class RouterExecuteRequest(BaseModel):
    task: str = Field(..., description="User or system task description")
    target_agent: str = Field(
        default="saphira-core",
        description="Logical target (saphira-core maps to surface Saphira)",
    )
    prefer_gpu: bool = False
    force_offline: bool = False
    messages: Optional[list[dict[str, str]]] = None


class RouterExecuteResponse(BaseModel):
    status: str
    task: str
    target_agent: str
    surface_agent: str = "Saphira"
    latency: dict[str, Any]
    privacy: dict[str, Any]
    memory: dict[str, Any]
    offline: dict[str, Any]
    excellence_routes: list[dict[str, Any]]
    agent_pillars: list[str]
    result: Optional[dict[str, Any]] = None


def _normalize_agent(target: str) -> str:
    t = (target or "saphira-core").lower().replace("-", "_")
    aliases = {
        "saphira_core": "saphira",
        "saphira": "saphira",
        "agent_two": "agent_two",
        "scholar": "scholar",
        "nova_aethrea": "novaaethrea",
        "novaaethrea": "novaaethrea",
        "nova_reign": "novareign",
        "novareign": "novareign",
        "aura": "aura",
        "agent_zero": "agent_zero",
        "cipher": "cipher",
        "orchestrator": "orchestrator",
    }
    return aliases.get(t, "saphira")


@router.post("/v1/router/execute", response_model=RouterExecuteResponse)
async def execute_route(body: RouterExecuteRequest) -> RouterExecuteResponse:
    """Route a task through excellence pillars and return an execution plan/result."""
    agent_key = _normalize_agent(body.target_agent)
    sanitized = _privacy.sanitize_text(body.task)

    offline_plan = _offline.plan(
        force_offline=body.force_offline,
        prefer_gpu=body.prefer_gpu,
    )
    latency = _latency.decide(
        task=sanitized.text,
        prefer_gpu=body.prefer_gpu,
        offline=body.force_offline,
        local_vllm_healthy=body.force_offline or body.prefer_gpu,
    )

    # Dual memory: record task + return memory check
    dual_memory.append_turn("user", sanitized.text, agent=agent_key)
    mem = dual_memory.memory_check()

    excellence = route_excellence(
        sanitized.text,
        prefer=pillars_for_agent(agent_key) or None,
    )

    result: dict[str, Any] | None = None
    if body.force_offline and body.messages:
        try:
            clean_messages = [
                {"role": m.get("role", "user"), "content": _privacy.sanitize_text(m.get("content", "")).text}
                for m in body.messages
            ]
            result = await _offline.execute_chat(
                clean_messages, force_offline=True
            )
        except Exception as exc:
            result = {
                "error": str(exc),
                "hint": "Start Ollama or local vLLM; set SAPHIRA_OLLAMA_URL / SAPHIRA_LOCAL_VLLM_URL",
            }
    elif "memory" in sanitized.text.lower() or "memory check" in sanitized.text.lower():
        result = {"memory_check": mem, "context_pack_preview": dual_memory.context_pack()}

    return RouterExecuteResponse(
        status="ok",
        task=sanitized.text,
        target_agent=body.target_agent,
        surface_agent="Saphira",
        latency={
            "path": latency.path,
            "reason": latency.reason,
            "estimated_ttft_ms": latency.estimated_ttft_ms,
            "prefer_gpu": latency.prefer_gpu,
            "metadata": latency.metadata,
        },
        privacy={
            "redacted": sanitized.redacted,
            "categories": sanitized.categories,
            "zero_egress": sanitized.zero_egress,
        },
        memory=mem,
        offline={
            "backend": offline_plan.backend,
            "endpoint": offline_plan.endpoint,
            "reason": offline_plan.reason,
            "capabilities": list(offline_plan.capabilities),
        },
        excellence_routes=[
            {
                "pillar": r.pillar_id,
                "capability": r.capability,
                "plugin": r.plugin,
                "owners": list(r.internal_owners),
            }
            for r in excellence
        ],
        agent_pillars=list(pillars_for_agent(agent_key)),
        result=result,
    )


@router.get("/v1/router/health")
async def router_health() -> dict[str, Any]:
    probes = await _offline.health_probe()
    return {
        "status": "healthy",
        "memory": dual_memory.memory_check(),
        "local_backends": probes,
        "excellence": "enabled",
    }
