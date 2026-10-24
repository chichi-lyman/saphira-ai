# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""Verification tests for SaphiraModelRegistry local and cloud endpoints."""

from __future__ import annotations

from src.core.model_registry import ModelEndpointConfig, SaphiraModelRegistry


def test_providers_include_cloud_and_local():
    keys = set(SaphiraModelRegistry.PROVIDERS.keys())
    assert "gemini_primary" in keys
    assert "vllm_local" in keys
    assert "ollama_local" in keys


def test_get_endpoint_default_is_vllm_local():
    ep = SaphiraModelRegistry.get_endpoint()
    assert ep is not None
    assert ep.provider == "vllm"
    assert ep.is_local is True
    assert ep.endpoint_url == "http://localhost:8000/v1/chat/completions"
    assert ep.model_name == "qwen2.5-coder-7b-instruct"
    assert ep.max_context_tokens == 32768


def test_get_endpoint_ollama():
    ep = SaphiraModelRegistry.get_endpoint("ollama_local")
    assert ep is not None
    assert ep.provider == "ollama"
    assert ep.is_local is True
    assert "11434" in ep.endpoint_url
    assert ep.model_name == "llama3.1:8b"


def test_get_endpoint_gemini_cloud():
    ep = SaphiraModelRegistry.get_endpoint("gemini_primary")
    assert ep is not None
    assert ep.provider == "google"
    assert ep.is_local is False
    assert ep.max_context_tokens == 1048576


def test_get_endpoint_missing_returns_none():
    assert SaphiraModelRegistry.get_endpoint("does_not_exist") is None


def test_list_local_endpoints():
    local = SaphiraModelRegistry.list_local_endpoints()
    assert set(local.keys()) == {"vllm_local", "ollama_local"}
    for cfg in local.values():
        assert isinstance(cfg, ModelEndpointConfig)
        assert cfg.is_local is True


def test_endpoint_config_defaults():
    cfg = ModelEndpointConfig(
        provider="test",
        model_name="m",
        endpoint_url="http://localhost:9",
    )
    assert cfg.is_local is False
    assert cfg.max_context_tokens == 8192
