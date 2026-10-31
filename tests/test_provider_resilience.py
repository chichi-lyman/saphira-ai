import asyncio
from unittest.mock import patch

import pytest

from src.config.settings import Settings
from src.providers.adapters import GeminiAdapter, OpenAIAdapter
from src.providers.registry import ProviderRegistry
from src.providers.types import GenerateRequest, GenerateResult

def make_registry():
    settings = Settings(providers_enabled=True, openai_api_key="test-openai", gemini_api_key="test-gemini", xai_api_key="", llm_preference="openai,gemini", environment="test")
    return ProviderRegistry(settings)

def success(provider):
    return GenerateResult(status="success", provider=provider, model="test-model", text="recovered")

@pytest.mark.asyncio
async def test_unexpected_provider_exception_fails_over_to_next_provider():
    registry = make_registry()
    async def explode(self, req): raise RuntimeError("adapter bug")
    async def recover(self, req): return success("gemini")
    with patch.object(OpenAIAdapter, "generate", explode), patch.object(GeminiAdapter, "generate", recover):
        result = await registry.generate(GenerateRequest(prompt="hello"))
    assert result.status == "success"
    assert result.provider == "gemini"

@pytest.mark.asyncio
async def test_policy_rejection_is_not_bypassed_by_provider_fallback():
    registry = make_registry()
    async def reject(self, req): return GenerateResult(status="policy_rejected", provider="openai", message="blocked by policy")
    async def should_not_run(self, req): return success("gemini")
    with patch.object(OpenAIAdapter, "generate", reject), patch.object(GeminiAdapter, "generate", should_not_run) as fallback:
        result = await registry.generate(GenerateRequest(prompt="unsafe"))
    assert result.status == "policy_rejected"
    fallback.assert_not_awaited()

@pytest.mark.asyncio
async def test_provider_timeout_isolated_and_fallback_continues():
    registry = make_registry()
    registry._provider_timeout_seconds = 0.001
    async def slow(self, req): await asyncio.sleep(0.02); return success("openai")
    async def recover(self, req): return success("gemini")
    with patch.object(OpenAIAdapter, "generate", slow), patch.object(GeminiAdapter, "generate", recover):
        result = await registry.generate(GenerateRequest(prompt="hello"))
    assert result.status == "success"
    assert result.provider == "gemini"
    assert registry.recent_telemetry(2)[0].metadata["failure_category"] == "timeout"
