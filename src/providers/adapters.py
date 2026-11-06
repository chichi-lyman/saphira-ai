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
    """
    Dual-mode Gemini provider:
    - Vertex AI (preferred when GOOGLE_CLOUD_PROJECT is set): production GCP path
    - Gemini Developer API (GEMINI_API_KEY): AI Studio / rapid prototyping

    Uses the unified google-genai SDK (Client with vertexai=True or api_key=...).
    """

    name = ProviderName.GEMINI

    def __init__(self, settings: Settings):
        self._settings = settings
        self._api_key = (settings.gemini_api_key or "").strip()
        self._project = (settings.google_cloud_project or "").strip()
        self._location = (settings.vertex_location or "us-central1").strip()

    def configured(self) -> bool:
        return self._settings.vertex_configured() or self._settings.gemini_developer_configured()

    def enabled(self) -> bool:
        return bool(self._settings.gemini_enabled) and self.configured()

    def _backend(self) -> str:
        if self._settings.vertex_configured():
            return "vertex"
        if self._settings.gemini_developer_configured():
            return "developer"
        return "none"

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "provider": self.name.value,
            "configured": self.configured(),
            "enabled": self.enabled(),
            "backend": self._backend(),
            "default_model": self._settings.gemini_model,
            "project": self._project or None,
            "location": self._location if self._backend() == "vertex" else None,
        }

    def _build_client(self):
        from google import genai

        if self._settings.vertex_configured():
            # Vertex AI / Gemini on Google Cloud (IAM / ADC / service account)
            return genai.Client(
                vertexai=True,
                project=self._project,
                location=self._location,
            )
        # Gemini Developer API (AI Studio key)
        return genai.Client(api_key=self._api_key)

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
                message="Gemini not enabled — set GOOGLE_CLOUD_PROJECT (Vertex) or GEMINI_API_KEY",
            )

        model = req.model or self._settings.gemini_model
        backend = self._backend()
        t0 = time.perf_counter()
        try:
            client = self._build_client()
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
                raw={"backend": backend},
            )
        except Exception as e:
            latency = (time.perf_counter() - t0) * 1000
            return GenerateResult(
                status="error",
                provider=self.name.value,
                model=model,
                message=f"[{backend}] {e}",
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
            messages = []
            if req.system:
                messages.append({"role": "system", "content": req.system})
            messages.append({"role": "user", "content": req.prompt})
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
            )
            latency = (time.perf_counter() - t0) * 1000
            text = ""
            if resp.choices:
                text = (resp.choices[0].message.content or "").strip()
            usage = None
            if getattr(resp, "usage", None):
                usage = {
                    "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                }
            return GenerateResult(
                status="success",
                text=text,
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

            client = AsyncOpenAI(
                api_key=self._api_key,
                base_url="https://api.x.ai/v1",
            )
            messages = []
            if req.system:
                messages.append({"role": "system", "content": req.system})
            messages.append({"role": "user", "content": req.prompt})
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
            )
            latency = (time.perf_counter() - t0) * 1000
            text = ""
            if resp.choices:
                text = (resp.choices[0].message.content or "").strip()
            usage = None
            if getattr(resp, "usage", None):
                usage = {
                    "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                }
            return GenerateResult(
                status="success",
                text=text,
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


class AnthropicAdapter:
    name = ProviderName.ANTHROPIC

    def __init__(self, settings: Settings):
        self._settings = settings
        self._api_key = (settings.anthropic_api_key or "").strip()

    def configured(self) -> bool:
        return bool(self._api_key)

    def enabled(self) -> bool:
        return bool(self._settings.anthropic_enabled) and self.configured()

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "provider": self.name.value,
            "configured": self.configured(),
            "enabled": self.enabled(),
            "default_model": getattr(self._settings, "anthropic_model", "claude-sonnet-4-5-20250929"),
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
                message="Anthropic not enabled or missing key",
            )

        model = req.model or getattr(self._settings, "anthropic_model", "claude-sonnet-4-5-20250929")
        t0 = time.perf_counter()
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=self._api_key)
            kwargs: dict[str, Any] = {
                "model": model,
                "max_tokens": req.max_tokens or 4096,
                "temperature": req.temperature,
                "messages": [{"role": "user", "content": req.prompt}],
            }
            if req.system:
                kwargs["system"] = req.system

            resp = await client.messages.create(**kwargs)
            latency = (time.perf_counter() - t0) * 1000
            text = ""
            if resp.content:
                for block in resp.content:
                    if getattr(block, "type", None) == "text":
                        text += getattr(block, "text", "") or ""
            usage = None
            if getattr(resp, "usage", None):
                usage = {
                    "prompt_tokens": getattr(resp.usage, "input_tokens", None),
                    "completion_tokens": getattr(resp.usage, "output_tokens", None),
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
