"""Local-first task routing heuristic for Saphira.

Light tasks → prefer local SLM (vLLM/Ollama) when enabled.
Heavy tasks → cloud providers via ProviderModelRouter.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.core.provider_router import ProviderModelRouter, RouteDecision, provider_model_router

LIGHT_KEYWORDS = (
    "format", "classify", "label", "summarize short", "rewrite", "typo",
    "json only", "extract fields", "route intent",
)
HEAVY_KEYWORDS = (
    "deep research", "multi-hop", "architecture", "prove", "long document",
    "codebase", "strategy", "legal", "medical",
)


@dataclass
class TaskClass:
    complexity: str
    prefer_local: bool
    reason: str


def classify_task(prompt: str) -> TaskClass:
    p = (prompt or "").lower()
    if any(k in p for k in HEAVY_KEYWORDS):
        return TaskClass("heavy", False, "Heavy keywords → cloud reasoning preferred")
    if any(k in p for k in LIGHT_KEYWORDS) or len(p) < 120:
        return TaskClass("light", True, "Light/short task → local SLM preferred when available")
    return TaskClass("unknown", False, "Default to cloud-capable route")


def route_with_fallback(
    prompt: str,
    *,
    router: ProviderModelRouter | None = None,
    local_keys: Iterable[str] = ("vllm_local", "ollama_local"),
) -> RouteDecision:
    r = router or provider_model_router
    tc = classify_task(prompt)
    if tc.prefer_local:
        for key in local_keys:
            decision = r.choose(prefer=key, require_capability="chat", local_ok=True)
            if decision.endpoint is not None and decision.endpoint.is_local:
                decision.reason = f"{tc.reason}; {decision.reason}"
                return decision
    decision = r.choose(require_capability="chat", local_ok=True)
    decision.reason = f"{tc.reason}; {decision.reason}"
    return decision
