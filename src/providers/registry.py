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
from src.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError
from src.resilience.degradation import GracefulDegradation, DegradationLevel

logger = logging.getLogger("Saphira.ProviderRegistry")


class ProviderRegistry:
    """
    Configuration-driven LLM provider registry with circuit breakers,
    graceful degradation, and partial-failure recovery.

    External calls are off unless Settings.providers_enabled is True.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()
        self._providers: dict[str, LLMProvider] = {
            ProviderName.GEMINI.value: GeminiAdapter(self._settings),
            ProviderName.ANTHROPIC.value: AnthropicAdapter(self._settings),
            ProviderName.OPENAI.value: OpenAIAdapter(self._settings),
            ProviderName.XAI.value: XAIAdapter(self._settings),
        }
        self._breakers: dict[str, CircuitBreaker] = {
            name: CircuitBreaker(
                name=name,
                failure_threshold=5,
                recovery_timeout=30.0,
                success_threshold=2,
            )
            for name in self._providers
        }
        self._degradation = GracefulDegradation()
        self._telemetry: list[InvocationRecord] = []

    def health(self) -> dict[str, Any]:
        """Read-only snapshot including circuit state."""
        providers = {}
        for name, p in self._providers.items():
            snap = p.health_snapshot()
            snap["circuit"] = self._breakers[name].snapshot()
            providers[name] = snap
        self._degradation.update_from_provider_health({"providers": providers})
        return {
            "providers_enabled": self._settings.providers_enabled,
            "preference": self._settings.llm_preference_list(),
            "providers": providers,
            "degradation": self._degradation.snapshot(),
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
        Route a generation request with circuit-breaker protection and
        graceful degradation.

        - preferred: force a specific provider name
        - fallback: try preference order until one succeeds (partial failure recovery)
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
        attempted = 0

        for name in order:
            provider = self._providers.get(name)
            if not provider or not provider.enabled():
                continue

            breaker = self._breakers[name]
            if not breaker.allow():
                logger.debug("skip %s (circuit open, retry_after=%.1fs)", name, breaker.retry_after())
                continue

            attempted += 1
            result = await provider.generate(req)
            self._record(result, metadata=req.metadata)

            if result.status == "success":
                breaker.record_success()
                return result

            # Treat non-success as failure for the breaker
            breaker.record_failure(result.message)
            last = result
            if not fallback:
                return result

        # All paths failed or circuits open → degrade
        health = self.health()
        level = self._degradation.level
        if level >= DegradationLevel.STANDBY or attempted == 0:
            msg = self._degradation.standby_message(last.message if last else None)
            standby = GenerateResult(
                status="standby",
                text=msg,
                message=msg,
                provider="standby",
            )
            self._record(standby, metadata=req.metadata)
            return standby

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

    def reset_circuits(self) -> None:
        """Admin / test helper."""
        for b in self._breakers.values():
            b.reset()


_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry
