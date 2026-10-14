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


class SaphiraModelRegistry:
    """
    Central Provider-Neutral Model Registry for Saphira AI.
    Registers cloud backends and local offline vLLM/Ollama endpoints.
    """

    PROVIDERS: Dict[str, ModelEndpointConfig] = {
        "gemini_primary": ModelEndpointConfig(
            provider="google",
            model_name="gemini-2.5-flash",
            endpoint_url="https://generativelanguage.googleapis.com/v1beta",
            is_local=False,
            max_context_tokens=1048576,
        ),
        "vllm_local": ModelEndpointConfig(
            provider="vllm",
            model_name="qwen2.5-coder-7b-instruct",
            endpoint_url="http://localhost:8000/v1/chat/completions",
            is_local=True,
            max_context_tokens=32768,
        ),
        "ollama_local": ModelEndpointConfig(
            provider="ollama",
            model_name="llama3.1:8b",
            endpoint_url="http://localhost:11434/v1/chat/completions",
            is_local=True,
            max_context_tokens=8192,
        ),
    }

    @classmethod
    def get_endpoint(cls, key: str = "vllm_local") -> Optional[ModelEndpointConfig]:
        return cls.PROVIDERS.get(key)

    @classmethod
    def list_local_endpoints(cls) -> Dict[str, ModelEndpointConfig]:
        return {k: v for k, v in cls.PROVIDERS.items() if v.is_local}
