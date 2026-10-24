# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Unit tests for configuration-driven ProviderRegistry.

External calls stay disabled; these tests never hit live APIs.
"""

from __future__ import annotations

import pytest

from src.config.settings import Settings
from src.providers.registry import ProviderRegistry
from src.providers.types import GenerateRequest


def _settings(**kwargs) -> Settings:
    """Build settings without reading real env (extra ignore + explicit values)."""
    base = {
        "providers_enabled": False,
        "openai_api_key": None,
        "gemini_api_key": None,
        "xai_api_key": None,
        "anthropic_api_key": None,
        "openai_enabled": True,
        "gemini_enabled": True,
        "xai_enabled": True,
        "anthropic_enabled": True,
        "llm_preference": "gemini,openai,xai",
        "openai_model": "gpt-4o-mini",
        "gemini_model": "gemini-2.0-flash",
        "xai_model": "grok-2-latest",
        "anthropic_model": "claude-sonnet-4-5-20250929",
        "environment": "test",
    }
    base.update(kwargs)
    return Settings.model_validate(base)


@pytest.mark.asyncio
async def test_providers_disabled_by_default():
    reg = ProviderRegistry(_settings(providers_enabled=False))
    result = await reg.generate(GenerateRequest(prompt="hello"))
    assert result.status == "disabled"
    assert "false" in (result.message or "").lower() or "enabled" in (result.message or "").lower()


@pytest.mark.asyncio
async def test_not_configured_when_no_keys():
    reg = ProviderRegistry(
        _settings(
            providers_enabled=True,
            openai_api_key="",
            gemini_api_key="",
            xai_api_key="",
            anthropic_api_key="",
        )
    )
    result = await reg.generate(GenerateRequest(prompt="hello"))
    assert result.status in ("error", "not_configured", "disabled")
    assert result.status != "success"


@pytest.mark.asyncio
async def test_health_snapshot_read_only():
    reg = ProviderRegistry(_settings(providers_enabled=False, gemini_api_key="fake-key"))
    health = reg.health()
    assert health["providers_enabled"] is False
    assert "gemini" in health["providers"]
    assert health["providers"]["gemini"]["configured"] is True
    assert health["providers"]["gemini"]["enabled"] is True
    assert health["providers"]["openai"]["configured"] is False


@pytest.mark.asyncio
async def test_telemetry_recorded_on_disabled():
    reg = ProviderRegistry(_settings(providers_enabled=False))
    await reg.generate(GenerateRequest(prompt="ping", metadata={"test": True}))
    records = reg.recent_telemetry(limit=5)
    assert len(records) >= 1
    assert records[-1].status == "disabled"


@pytest.mark.asyncio
async def test_preference_order_exposed():
    reg = ProviderRegistry(_settings(llm_preference="openai,xai,gemini"))
    health = reg.health()
    assert health["preference"] == ["openai", "xai", "gemini"]


@pytest.mark.asyncio
async def test_generate_natural_reply_disabled():
    reg = ProviderRegistry(_settings(providers_enabled=False))
    result = await reg.generate_natural_reply("Hi Saphira")
    assert result.status == "disabled"
