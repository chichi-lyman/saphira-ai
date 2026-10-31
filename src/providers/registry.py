# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

from __future__ import annotations

import asyncio
import logging
import time
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
        self._provider_failures: dict[str, int] = {}
        self._provider_cooldowns: dict[str, float] = {}
        self._failure_threshold = 3
        self._cooldown_seconds = 30.0
        self._provider_timeout_seconds = 45.0

    def health(self) -> dict[str, Any]:
        """Read-only snapshot. Never mutates state."""
        return {
            "providers_enabled": self._settings.providers_enabled,
            "preference": self._settings.llm_preference_list(),
            "providers": {name: {**p.health_snapshot(), "circuit_open": self._provider_cooldowns.get(name, 0.0) > time.monotonic(), "consecutive_failures": self._provider_failures.get(name, 0)} for name, p in self._providers.items()},
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

    @staticmethod
    def _failure_category(message: Optional[str]) -> str:
        text = (message or "").lower()
        if "timeout" in text or "timed out" in text: return "timeout"
        if "429" in text or "rate limit" in text or "quota" in text: return "rate_limited"
        if "401" in text or "403" in text or "unauthorized" in text or "forbidden" in text: return "authentication"
        if "connection" in text or "unavailable" in text or "502" in text or "503" in text or "504" in text: return "unavailable"
        return "provider_error"

    async def generate(self, req: GenerateRequest, *, preferred: Optional[str] = None, fallback: bool = True) -> GenerateResult:
        """Isolate provider failures and use bounded, observable failover.
        Explicit safety/policy rejections are returned immediately and never bypassed.
        """
        if not self._settings.providers_enabled:
            result = GenerateResult(status="disabled", message="SAPHIRA_PROVIDERS_ENABLED is false")
            self._record(result, metadata={**req.metadata, "failure_category": "globally_disabled"})
            return result
        order: list[str] = []
        if preferred: order.append(preferred.lower())
        for name in self._settings.llm_preference_list():
            if name not in order: order.append(name)
        attempted = 0
        last = GenerateResult(status="not_configured", message="No configured providers are available")
        for name in order:
            provider = self._providers.get(name)
            if provider is None or not provider.enabled(): continue
            if self._provider_cooldowns.get(name, 0.0) > time.monotonic():
                last = GenerateResult(status="unavailable", provider=name, message="Provider isolated by circuit breaker")
                continue
            self._provider_cooldowns.pop(name, None)
            attempted += 1
            try:
                result = await asyncio.wait_for(provider.generate(req), timeout=self._provider_timeout_seconds)
            except asyncio.TimeoutError:
                result = GenerateResult(status="error", provider=name, message="Provider request timed out")
            except Exception as exc:
                logger.warning("provider_invocation_exception provider=%s exception_type=%s", name, type(exc).__name__)
                result = GenerateResult(status="error", provider=name, message=f"Provider invocation failed ({type(exc).__name__})")
            if result.status == "success":
                self._provider_failures[name] = 0
                self._provider_cooldowns.pop(name, None)
                self._record(result, metadata={**req.metadata, "failure_category": None})
                return result
            category = self._failure_category(result.message)
            self._record(result, metadata={**req.metadata, "failure_category": category})
            if result.status in {"rejected", "policy_rejected"}: return result
            if result.status in {"error", "unavailable"}:
                failures = self._provider_failures.get(name, 0) + 1
                self._provider_failures[name] = failures
                if failures >= self._failure_threshold:
                    self._provider_cooldowns[name] = time.monotonic() + self._cooldown_seconds
            last = result
            if not fallback: return result
        if attempted == 0:
            self._record(last, metadata={**req.metadata, "failure_category": "no_provider_configured"})
            return last
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
