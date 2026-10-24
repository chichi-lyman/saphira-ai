# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

from __future__ import annotations

import logging
from typing import Any, Optional

from src.config.settings import Settings, get_settings
from src.providers.adapters import (
    GeminiAdapter,
    OpenAIAdapter,
    XAIAdapter,
    AnthropicAdapter,
    LLMProvider,
)
from src.providers.types import GenerateRequest, GenerateResult, InvocationRecord, ProviderName

logger = logging.getLogger("Saphira.ProviderRegistry")


class ProviderRegistry:
    """
    Configuration-driven LLM provider registry.
    External calls are off unless Settings.providers_enabled is True.
    Health is observed (read-only); never mutated from call paths.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()
        self._providers: dict[str, LLMProvider] = {
            ProviderName.GEMINI.value: GeminiAdapter(self._settings),
            ProviderName.ANTHROPIC.value: AnthropicAdapter(self._settings),
            ProviderName.OPENAI.value: OpenAIAdapter(self._settings),
            ProviderName.XAI.value: XAIAdapter(self._settings),
        }
        self._telemetry: list[InvocationRecord] = []

    def health(self) -> dict[str, Any]:
        """Read-only snapshot. Never mutates state."""
        return {
            "providers_enabled": self._settings.providers_enabled,
            "preference": self._settings.llm_preference_list(),
            "providers": {name: p.health_snapshot() for name, p in self._providers.items()},
        }

    def _record(self, result: GenerateResult, metadata: Optional[dict] = None) -> None:
        rec = InvocationRecord(
            provider=result.provider or "",
            model=result.model or "",
            status=result.status,
            latency_ms=result.latency_ms or 0.0,
            prompt_tokens=(result.usage or {}).get("prompt_tokens"),
            completion_tokens=(result.usage or {}).get("completion_tokens"),
            estimated_cost_usd=result.estimated_cost_usd,
            error=result.message if result.status != "success" else None,
            metadata=metadata or {},
        )
        self._telemetry.append(rec)
        if len(self._telemetry) > 500:
            self._telemetry = self._telemetry[-250:]
        logger.info(
            "llm_invocation provider=%s model=%s status=%s latency_ms=%.1f",
            rec.provider,
            rec.model,
            rec.status,
            rec.latency_ms,
        )

    def recent_telemetry(self, limit: int = 20) -> list[InvocationRecord]:
        return list(self._telemetry[-limit:])

    async def generate(
        self,
        req: GenerateRequest,
        *,
        preferred: Optional[str] = None,
        fallback: bool = True,
    ) -> GenerateResult:
        """
        Route a generation request.
        - preferred: force a specific provider name
        - fallback: try preference order until one succeeds
        """
        if not self._settings.providers_enabled:
            result = GenerateResult(
                status="disabled",
                message="SAPHIRA_PROVIDERS_ENABLED is false",
            )
            self._record(result, metadata=req.metadata)
            return result

        order: list[str] = []
        if preferred:
            order.append(preferred.lower())
        for name in self._settings.llm_preference_list():
            if name not in order:
                order.append(name)

        last: GenerateResult = GenerateResult(status="error", message="No providers available")
        for name in order:
            provider = self._providers.get(name)
            if not provider or not provider.enabled():
                continue
            result = await provider.generate(req)
            self._record(result, metadata=req.metadata)
            if result.status == "success":
                return result
            last = result
            if not fallback:
                return result

        return last

    async def generate_natural_reply(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> GenerateResult:
        """Convenience used by chat surface (legacy path). Prefer SaphiraBrain."""
        return await self.generate(
            GenerateRequest(
                prompt=prompt,
                system=system,
                metadata=metadata or {"surface": "chat"},
            ),
            fallback=True,
        )


_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry
