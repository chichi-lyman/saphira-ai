# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

from typing import Any, Dict, Optional
from pydantic import BaseModel


class ModelEndpointConfig(BaseModel):
    provider: str
    model_name: str
    endpoint_url: str
    is_local: bool = False
    max_context_tokens: int = 8192
    notes: str = ""


class SaphiraModelRegistry:
    """
    Central Provider-Neutral Model Registry for Saphira AI.

    Registers cloud backends (Gemini, Claude/Anthropic, OpenAI-compatible)
    and local offline vLLM / Ollama endpoints. Used by the inference router
    so the product can switch providers without rewriting business logic.
    """

    PROVIDERS: Dict[str, ModelEndpointConfig] = {
        # Primary cloud path (Google)
        "gemini_flash": ModelEndpointConfig(
            provider="google",
            model_name="gemini-2.5-flash",
            endpoint_url="https://generativelanguage.googleapis.com/v1beta",
            is_local=False,
            max_context_tokens=1048576,
            notes="Fast, high-context. Primary for most interactive work.",
        ),
        "gemini_pro": ModelEndpointConfig(
            provider="google",
            model_name="gemini-2.5-pro",
            endpoint_url="https://generativelanguage.googleapis.com/v1beta",
            is_local=False,
            max_context_tokens=1048576,
            notes="Heavier reasoning when quality > latency.",
        ),
        # Anthropic path (fallback / specialized)
        "claude_sonnet": ModelEndpointConfig(
            provider="anthropic",
            model_name="claude-sonnet-4-5-20250929",
            endpoint_url="https://api.anthropic.com/v1/messages",
            is_local=False,
            max_context_tokens=200000,
            notes="Strong coding & long-document analysis fallback.",
        ),
        "claude_haiku": ModelEndpointConfig(
            provider="anthropic",
            model_name="claude-haiku-4-5-20251001",
            endpoint_url="https://api.anthropic.com/v1/messages",
            is_local=False,
            max_context_tokens=200000,
            notes="Fast, cost-efficient Anthropic option.",
        ),
        # Local / self-hosted (force-local, offline, cost control)
        "vllm_local": ModelEndpointConfig(
            provider="vllm",
            model_name="qwen2.5-coder-7b-instruct",
            endpoint_url="http://localhost:8000/v1/chat/completions",
            is_local=True,
            max_context_tokens=32768,
            notes="Local OpenAI-compatible endpoint (vLLM).",
        ),
        "ollama_local": ModelEndpointConfig(
            provider="ollama",
            model_name="llama3.1:8b",
            endpoint_url="http://localhost:11434/v1/chat/completions",
            is_local=True,
            max_context_tokens=8192,
            notes="Local Ollama for fully offline or privacy-sensitive runs.",
        ),
    }

    @classmethod
    def get_endpoint(cls, key: str = "gemini_flash") -> Optional[ModelEndpointConfig]:
        return cls.PROVIDERS.get(key)

    @classmethod
    def list_local_endpoints(cls) -> Dict[str, ModelEndpointConfig]:
        return {k: v for k, v in cls.PROVIDERS.items() if v.is_local}

    @classmethod
    def list_cloud_endpoints(cls) -> Dict[str, ModelEndpointConfig]:
        return {k: v for k, v in cls.PROVIDERS.items() if not v.is_local}

    @classmethod
    def preferred_order(cls) -> list[str]:
        """Default routing preference: fast Gemini → quality Claude → local."""
        return ["gemini_flash", "claude_sonnet", "claude_haiku", "vllm_local", "ollama_local"]
