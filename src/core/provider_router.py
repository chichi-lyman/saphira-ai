"""Model routing via ProviderRegistry (OpenAI, Azure, Bedrock, Gemini, xAI, local).

Selects endpoint by credentials + capability + priority.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.providers.registry import ProviderEndpoint, ProviderRegistry, provider_registry


@dataclass
class RouteDecision:
    endpoint: ProviderEndpoint | None
    reason: str
    fallback_keys: list[str]


class ProviderModelRouter:
    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self.registry = registry or provider_registry

    def choose(
        self,
        *,
        prefer: str | None = None,
        require_capability: str = "chat",
        local_ok: bool = True,
    ) -> RouteDecision:
        ep = self.registry.route(
            prefer=prefer,
            require_capability=require_capability,
            local_ok=local_ok,
        )
        enabled = self.registry.list_enabled()
        fallbacks = [e.key for e in enabled if self.registry.has_credentials(e.key)]
        if ep is None:
            return RouteDecision(
                endpoint=None,
                reason="No enabled provider with credentials and required capability",
                fallback_keys=fallbacks,
            )
        return RouteDecision(
            endpoint=ep,
            reason=f"Selected {ep.key} ({ep.provider}/{ep.model_name})",
            fallback_keys=[k for k in fallbacks if k != ep.key],
        )

    def status(self) -> dict[str, Any]:
        return self.registry.status_snapshot()


provider_model_router = ProviderModelRouter()
