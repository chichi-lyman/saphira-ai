# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
"""
Stress tests for every ProviderRegistry component.

Covers:
- Settings defaults & preference parsing
- Each adapter (Gemini, OpenAI, xAI) disabled / not_configured / error paths
- Registry routing, fallback, preferred provider, concurrent load
- Telemetry bounds & integrity
- Health snapshot immutability under load
- Rapid repeated calls
- Empty / huge prompts
- Metadata propagation

No live external API calls are made.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config.settings import Settings
from src.providers.adapters import GeminiAdapter, OpenAIAdapter, XAIAdapter
from src.providers.registry import ProviderRegistry
from src.providers.types import GenerateRequest, GenerateResult, InvocationRecord, ProviderName


def make_settings(**kwargs: Any) -> Settings:
    base = {
        "providers_enabled": False,
        "openai_api_key": None,
        "gemini_api_key": None,
        "xai_api_key": None,
        "openai_enabled": True,
        "gemini_enabled": True,
        "xai_enabled": True,
        "llm_preference": "gemini,openai,xai",
        "openai_model": "gpt-4o-mini",
        "gemini_model": "gemini-2.0-flash",
        "xai_model": "grok-2-latest",
        "environment": "test",
    }
    base.update(kwargs)
    return Settings(**base)


def success_result(provider: str = "openai", model: str = "gpt-4o-mini") -> GenerateResult:
    return GenerateResult(
        status="success",
        text="ok",
        provider=provider,
        model=model,
        latency_ms=12.5,
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    )


class TestSettingsStress:
    def test_providers_enabled_defaults_false(self):
        s = make_settings()
        assert s.providers_enabled is False

    def test_preference_list_parsing_variants(self):
        cases = [
            ("gemini,openai,xai", ["gemini", "openai", "xai"]),
            ("  openai , xai  ", ["openai", "xai"]),
            ("GEMINI,OpenAI", ["gemini", "openai"]),
            ("", []),
            ("single", ["single"]),
        ]
        for raw, expected in cases:
            s = make_settings(llm_preference=raw)
            assert s.llm_preference_list() == expected

    def test_has_any_llm_provider(self):
        assert make_settings().has_any_llm_provider() is False
        assert make_settings(openai_api_key="sk-x").has_any_llm_provider() is True
        assert make_settings(gemini_api_key="g").has_any_llm_provider() is True
        assert make_settings(xai_api_key="x").has_any_llm_provider() is True

    def test_validation_report_includes_providers_enabled(self):
        report = make_settings(providers_enabled=True).validation_report()
        assert report["providers_enabled"] is True
        assert "llm_provider_configured" in report

    def test_model_defaults_present(self):
        s = make_settings()
        assert s.openai_model
        assert s.gemini_model
        assert s.xai_model


class TestGeminiAdapterStress:
    @pytest.mark.asyncio
    async def test_disabled_master_switch(self):
        a = GeminiAdapter(make_settings(providers_enabled=False, gemini_api_key="k"))
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "disabled"
        assert r.provider == "gemini"

    @pytest.mark.asyncio
    async def test_not_configured_no_key(self):
        a = GeminiAdapter(make_settings(providers_enabled=True, gemini_api_key=""))
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "not_configured"

    @pytest.mark.asyncio
    async def test_not_configured_provider_disabled(self):
        a = GeminiAdapter(
            make_settings(providers_enabled=True, gemini_api_key="k", gemini_enabled=False)
        )
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "not_configured"

    @pytest.mark.asyncio
    async def test_import_error_surfaces_as_error(self):
        a = GeminiAdapter(make_settings(providers_enabled=True, gemini_api_key="k"))
        with patch("builtins.__import__", side_effect=ImportError("no google")):
            r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "error"
        assert r.latency_ms is not None and r.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_health_snapshot_fields(self):
        a = GeminiAdapter(make_settings(gemini_api_key="k"))
        h = a.health_snapshot()
        assert h["provider"] == "gemini"
        assert h["configured"] is True
        assert "default_model" in h

    def test_name_enum(self):
        assert GeminiAdapter.name == ProviderName.GEMINI


def _install_fake_openai(mock_client: Any) -> None:
    import sys
    import types

    mod = types.ModuleType("openai")
    mod.AsyncOpenAI = MagicMock(return_value=mock_client)  # type: ignore[attr-defined]
    sys.modules["openai"] = mod


class TestOpenAIAdapterStress:
    @pytest.mark.asyncio
    async def test_disabled_master_switch(self):
        a = OpenAIAdapter(make_settings(providers_enabled=False, openai_api_key="k"))
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "disabled"

    @pytest.mark.asyncio
    async def test_not_configured_no_key(self):
        a = OpenAIAdapter(make_settings(providers_enabled=True, openai_api_key=None))
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "not_configured"

    @pytest.mark.asyncio
    async def test_mocked_success_path(self):
        a = OpenAIAdapter(make_settings(providers_enabled=True, openai_api_key="sk-test"))
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="  hello world  "))]
        mock_resp.usage = MagicMock(prompt_tokens=3, completion_tokens=2, total_tokens=5)
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(return_value=mock_resp)
        _install_fake_openai(client)
        r = await a.generate(GenerateRequest(prompt="hi", system="sys"))
        assert r.status == "success"
        assert r.text == "hello world"
        assert r.usage["total_tokens"] == 5
        assert r.latency_ms is not None

    @pytest.mark.asyncio
    async def test_mocked_api_exception(self):
        a = OpenAIAdapter(make_settings(providers_enabled=True, openai_api_key="sk-test"))
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(side_effect=RuntimeError("rate limit"))
        _install_fake_openai(client)
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "error"
        assert "rate limit" in (r.message or "")

    @pytest.mark.asyncio
    async def test_empty_prompt_still_calls(self):
        a = OpenAIAdapter(make_settings(providers_enabled=True, openai_api_key="sk-test"))
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=""))]
        mock_resp.usage = None
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(return_value=mock_resp)
        _install_fake_openai(client)
        r = await a.generate(GenerateRequest(prompt=""))
        assert r.status == "success"
        assert r.text == ""


class TestXAIAdapterStress:
    @pytest.mark.asyncio
    async def test_disabled_and_not_configured(self):
        a = XAIAdapter(make_settings(providers_enabled=False, xai_api_key="k"))
        assert (await a.generate(GenerateRequest(prompt="x"))).status == "disabled"
        a2 = XAIAdapter(make_settings(providers_enabled=True, xai_api_key=""))
        assert (await a2.generate(GenerateRequest(prompt="x"))).status == "not_configured"

    @pytest.mark.asyncio
    async def test_mocked_success(self):
        a = XAIAdapter(make_settings(providers_enabled=True, xai_api_key="xai-k"))
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="grok reply"))]
        mock_resp.usage = MagicMock(prompt_tokens=1, completion_tokens=1, total_tokens=2)
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(return_value=mock_resp)
        _install_fake_openai(client)
        r = await a.generate(GenerateRequest(prompt="hi"))
        assert r.status == "success"
        assert r.text == "grok reply"
        assert r.provider == "xai"

    def test_health(self):
        h = XAIAdapter(make_settings(xai_api_key="k")).health_snapshot()
        assert h["provider"] == "xai"
        assert h["configured"] is True


class TestRegistryRoutingStress:
    @pytest.mark.asyncio
    async def test_master_off_short_circuits(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False, openai_api_key="k"))
        r = await reg.generate(GenerateRequest(prompt="hi"))
        assert r.status == "disabled"

    @pytest.mark.asyncio
    async def test_fallback_skips_disabled_providers(self):
        reg = ProviderRegistry(
            make_settings(
                providers_enabled=True,
                openai_api_key="",
                gemini_api_key="",
                xai_api_key="",
            )
        )
        r = await reg.generate(GenerateRequest(prompt="hi"))
        assert r.status != "success"

    @pytest.mark.asyncio
    async def test_preferred_provider_honored(self):
        reg = ProviderRegistry(
            make_settings(providers_enabled=True, openai_api_key="sk", gemini_api_key="gk")
        )

        async def fake_generate(self, req):
            return success_result(provider=self.name.value, model="m")

        with patch.object(OpenAIAdapter, "generate", fake_generate), patch.object(
            GeminiAdapter, "generate", fake_generate
        ), patch.object(XAIAdapter, "generate", fake_generate):
            r = await reg.generate(GenerateRequest(prompt="hi"), preferred="openai")
        assert r.status == "success"
        assert r.provider == "openai"

    @pytest.mark.asyncio
    async def test_no_fallback_stops_after_first_failure(self):
        reg = ProviderRegistry(
            make_settings(
                providers_enabled=True,
                llm_preference="openai,gemini",
                openai_api_key="sk",
                gemini_api_key="gk",
            )
        )

        async def openai_fail(self, req):
            return GenerateResult(status="error", provider="openai", message="boom")

        async def gemini_ok(self, req):
            return success_result(provider="gemini")

        with patch.object(OpenAIAdapter, "generate", openai_fail), patch.object(
            GeminiAdapter, "generate", gemini_ok
        ):
            r = await reg.generate(GenerateRequest(prompt="hi"), fallback=False)
        assert r.status == "error"
        assert r.provider == "openai"

    @pytest.mark.asyncio
    async def test_fallback_reaches_second_provider(self):
        reg = ProviderRegistry(
            make_settings(
                providers_enabled=True,
                llm_preference="openai,gemini",
                openai_api_key="sk",
                gemini_api_key="gk",
            )
        )

        async def openai_fail(self, req):
            return GenerateResult(status="error", provider="openai", message="boom")

        async def gemini_ok(self, req):
            return success_result(provider="gemini")

        with patch.object(OpenAIAdapter, "generate", openai_fail), patch.object(
            GeminiAdapter, "generate", gemini_ok
        ):
            r = await reg.generate(GenerateRequest(prompt="hi"), fallback=True)
        assert r.status == "success"
        assert r.provider == "gemini"


class TestTelemetryStress:
    @pytest.mark.asyncio
    async def test_records_accumulate(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        for i in range(50):
            await reg.generate(GenerateRequest(prompt=f"p{i}", metadata={"i": i}))
        records = reg.recent_telemetry(limit=100)
        assert len(records) == 50
        assert all(isinstance(r, InvocationRecord) for r in records)
        assert all(r.status == "disabled" for r in records)

    @pytest.mark.asyncio
    async def test_telemetry_window_bounded(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        for i in range(600):
            await reg.generate(GenerateRequest(prompt="x"))
        assert len(reg._telemetry) <= 500
        assert len(reg.recent_telemetry(limit=1000)) <= 500

    @pytest.mark.asyncio
    async def test_metadata_propagated(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        await reg.generate(GenerateRequest(prompt="x", metadata={"surface": "stress"}))
        rec = reg.recent_telemetry(1)[0]
        assert rec.metadata.get("surface") == "stress"


class TestConcurrencyStress:
    @pytest.mark.asyncio
    async def test_100_concurrent_disabled_calls(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))

        async def one(i: int):
            return await reg.generate(GenerateRequest(prompt=f"c{i}"))

        t0 = time.perf_counter()
        results = await asyncio.gather(*[one(i) for i in range(100)])
        elapsed = time.perf_counter() - t0
        assert all(r.status == "disabled" for r in results)
        assert elapsed < 5.0
        assert len(reg.recent_telemetry(limit=200)) >= 100

    @pytest.mark.asyncio
    async def test_health_stable_under_concurrent_reads(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False, gemini_api_key="k"))

        async def read_health(_):
            return reg.health()

        snapshots = await asyncio.gather(*[read_health(i) for i in range(50)])
        for s in snapshots:
            assert s["providers_enabled"] is False
            assert s["providers"]["gemini"]["configured"] is True

    @pytest.mark.asyncio
    async def test_interleaved_generate_and_health(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))

        async def mix(i: int):
            if i % 2 == 0:
                return await reg.generate(GenerateRequest(prompt=str(i)))
            return reg.health()

        outcomes = await asyncio.gather(*[mix(i) for i in range(40)])
        assert len(outcomes) == 40


class TestPromptEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_prompt(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        r = await reg.generate(GenerateRequest(prompt=""))
        assert r.status == "disabled"

    @pytest.mark.asyncio
    async def test_very_large_prompt(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        huge = "x" * 500_000
        r = await reg.generate(GenerateRequest(prompt=huge, metadata={"size": len(huge)}))
        assert r.status == "disabled"
        assert reg.recent_telemetry(1)[0].metadata["size"] == 500_000

    @pytest.mark.asyncio
    async def test_unicode_and_control_chars(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        prompt = "你好 🚀 \x00\n\t" + "é" * 100
        r = await reg.generate(GenerateRequest(prompt=prompt))
        assert r.status == "disabled"

    @pytest.mark.asyncio
    async def test_generate_natural_reply_wrapper(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        r = await reg.generate_natural_reply("Hello Saphira", system="persona")
        assert r.status == "disabled"


class TestHealthImmutability:
    def test_health_does_not_mutate_settings(self):
        s = make_settings(providers_enabled=False, gemini_api_key="k")
        reg = ProviderRegistry(s)
        before = s.providers_enabled
        h1 = reg.health()
        h2 = reg.health()
        assert before is False
        assert h1 == h2
        h1["providers_enabled"] = True
        assert reg.health()["providers_enabled"] is False

    def test_all_three_providers_in_health(self):
        reg = ProviderRegistry(make_settings())
        h = reg.health()
        assert set(h["providers"].keys()) == {"gemini", "openai", "xai"}


class TestBurstStress:
    @pytest.mark.asyncio
    async def test_1000_sequential_disabled(self):
        reg = ProviderRegistry(make_settings(providers_enabled=False))
        t0 = time.perf_counter()
        for i in range(1000):
            r = await reg.generate(GenerateRequest(prompt=f"b{i}"))
            assert r.status == "disabled"
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0
        assert len(reg._telemetry) <= 500
