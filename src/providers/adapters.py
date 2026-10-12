# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional, Protocol

from src.config.settings import Settings
from src.providers.types import GenerateRequest, GenerateResult, ProviderName


class LLMProvider(Protocol):
    name: ProviderName

    def configured(self) -> bool: ...
    def enabled(self) -> bool: ...
    async def generate(self, req: GenerateRequest) -> GenerateResult: ...
    def health_snapshot(self) -> dict[str, Any]: ...


class GeminiAdapter:
    name = ProviderName.GEMINI

    def __init__(self, settings: Settings):
        self._settings = settings
        self._api_key = (settings.gemini_api_key or "").strip()

    def configured(self) -> bool:
        return bool(self._api_key)

    def enabled(self) -> bool:
        return bool(self._settings.gemini_enabled) and self.configured()

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "provider": self.name.value,
            "configured": self.configured(),
            "enabled": self.enabled(),
            "default_model": self._settings.gemini_model,
        }

    async def generate(self, req: GenerateRequest) -> GenerateResult:
        if not self._settings.providers_enabled:
            return GenerateResult(
                status="disabled",
                provider=self.name.value,
                message="providers_enabled=False",
            )
        if not self.enabled():
            return GenerateResult(
                status="not_configured",
                provider=self.name.value,
                message="Gemini not enabled or missing key",
            )

        model = req.model or self._settings.gemini_model
        t0 = time.perf_counter()
        try:
            from google import genai

            client = genai.Client(api_key=self._api_key)
            contents = req.prompt if not req.system else f"{req.system}\n\n{req.prompt}"

            def _call():
                return client.models.generate_content(model=model, contents=contents)

            res = await asyncio.to_thread(_call)
            latency = (time.perf_counter() - t0) * 1000
            text = getattr(res, "text", None) or ""
            return GenerateResult(
                status="success",
                text=text.strip(),
                provider=self.name.value,
                model=model,
                latency_ms=latency,
            )
        except Exception as e:
            latency = (time.perf_counter() - t0) * 1000
            return GenerateResult(
                status="error",
                provider=self.name.value,
                model=model,
                message=str(e),
                latency_ms=latency,
            )


class OpenAIAdapter:
    name = ProviderName.OPENAI

    def __init__(self, settings: Settings):
        self._settings = settings
        self._api_key = (settings.openai_api_key or "").strip()

    def configured(self) -> bool:
        return bool(self._api_key)

    def enabled(self) -> bool:
        return bool(self._settings.openai_enabled) and self.configured()

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "provider": self.name.value,
            "configured": self.configured(),
            "enabled": self.enabled(),
            "default_model": self._settings.openai_model,
        }

    async def generate(self, req: GenerateRequest) -> GenerateResult:
        if not self._settings.providers_enabled:
            return GenerateResult(
                status="disabled",
                provider=self.name.value,
                message="providers_enabled=False",
            )
        if not self.enabled():
            return GenerateResult(
                status="not_configured",
                provider=self.name.value,
                message="OpenAI not enabled or missing key",
            )

        model = req.model or self._settings.openai_model
        t0 = time.perf_counter()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key)
            messages: list[dict[str, str]] = []
            if req.system:
                messages.append({"role": "system", "content": req.system})
            messages.append({"role": "user", "content": req.prompt})

            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": req.temperature,
            }
            if req.max_tokens is not None:
                kwargs["max_tokens"] = req.max_tokens

            resp = await client.chat.completions.create(**kwargs)
            latency = (time.perf_counter() - t0) * 1000
            choice = (resp.choices[0].message.content or "") if resp.choices else ""
            usage = None
            if resp.usage:
                usage = {
                    "prompt_tokens": resp.usage.prompt_tokens,
                    "completion_tokens": resp.usage.completion_tokens,
                    "total_tokens": resp.usage.total_tokens,
                }
            return GenerateResult(
                status="success",
                text=choice.strip(),
                provider=self.name.value,
                model=model,
                latency_ms=latency,
                usage=usage,
            )
        except Exception as e:
            latency = (time.perf_counter() - t0) * 1000
            return GenerateResult(
                status="error",
                provider=self.name.value,
                model=model,
                message=str(e),
                latency_ms=latency,
            )


class XAIAdapter:
    """xAI / Grok via OpenAI-compatible endpoint."""

    name = ProviderName.XAI

    def __init__(self, settings: Settings):
        self._settings = settings
        self._api_key = (settings.xai_api_key or "").strip()

    def configured(self) -> bool:
        return bool(self._api_key)

    def enabled(self) -> bool:
        return bool(self._settings.xai_enabled) and self.configured()

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "provider": self.name.value,
            "configured": self.configured(),
            "enabled": self.enabled(),
            "default_model": self._settings.xai_model,
        }

    async def generate(self, req: GenerateRequest) -> GenerateResult:
        if not self._settings.providers_enabled:
            return GenerateResult(
                status="disabled",
                provider=self.name.value,
                message="providers_enabled=False",
            )
        if not self.enabled():
            return GenerateResult(
                status="not_configured",
                provider=self.name.value,
                message="xAI not enabled or missing key",
            )

        model = req.model or self._settings.xai_model
        t0 = time.perf_counter()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key, base_url="https://api.x.ai/v1")
            messages: list[dict[str, str]] = []
            if req.system:
                messages.append({"role": "system", "content": req.system})
            messages.append({"role": "user", "content": req.prompt})

            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=req.temperature,
            )
            latency = (time.perf_counter() - t0) * 1000
            text = (resp.choices[0].message.content or "") if resp.choices else ""
            usage = None
            if resp.usage:
                usage = {
                    "prompt_tokens": resp.usage.prompt_tokens,
                    "completion_tokens": resp.usage.completion_tokens,
                    "total_tokens": resp.usage.total_tokens,
                }
            return GenerateResult(
                status="success",
                text=text.strip(),
                provider=self.name.value,
                model=model,
                latency_ms=latency,
                usage=usage,
            )
        except Exception as e:
            latency = (time.perf_counter() - t0) * 1000
            return GenerateResult(
                status="error",
                provider=self.name.value,
                model=model,
                message=str(e),
                latency_ms=latency,
            )
