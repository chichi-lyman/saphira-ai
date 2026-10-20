"""Provider-neutral model registry for Saphira / Nova Umbrella.

Registers Microsoft (Azure OpenAI), Amazon (Bedrock), Google (Gemini),
OpenAI, xAI, and optional local endpoints. Secrets stay in env — never committed.

Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProviderEndpoint:
    key: str
    provider: str
    model_name: str
    endpoint_url: str
    is_local: bool = False
    max_context_tokens: int = 8192
    api_key_env: str = ""
    enabled: bool = True
    priority: int = 100
    capabilities: tuple[str, ...] = ("chat",)


def _env_enabled(name: str, default: bool = True) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


class ProviderRegistry:
    def __init__(self) -> None:
        self._endpoints: Dict[str, ProviderEndpoint] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults = [
            ProviderEndpoint(
                key="openai_primary",
                provider="openai",
                model_name=os.environ.get("OPENAI_MODEL", "gpt-4o"),
                endpoint_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                api_key_env="OPENAI_API_KEY",
                priority=10,
                max_context_tokens=128000,
                capabilities=("chat", "tools", "vision"),
                enabled=_env_enabled("OPENAI_ENABLED", True),
            ),
            ProviderEndpoint(
                key="azure_openai",
                provider="azure",
                model_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
                endpoint_url=os.environ.get(
                    "AZURE_OPENAI_ENDPOINT", "https://YOUR_RESOURCE.openai.azure.com"
                ),
                api_key_env="AZURE_OPENAI_API_KEY",
                priority=15,
                max_context_tokens=128000,
                capabilities=("chat", "tools", "vision"),
                enabled=_env_enabled("AZURE_OPENAI_ENABLED", False),
            ),
            ProviderEndpoint(
                key="bedrock_primary",
                provider="bedrock",
                model_name=os.environ.get(
                    "BEDROCK_MODEL", "anthropic.claude-3-5-sonnet-20241022-v2:0"
                ),
                endpoint_url=os.environ.get(
                    "BEDROCK_ENDPOINT", "https://bedrock-runtime.us-east-1.amazonaws.com"
                ),
                api_key_env="AWS_ACCESS_KEY_ID",
                priority=20,
                max_context_tokens=200000,
                capabilities=("chat", "tools"),
                enabled=_env_enabled("BEDROCK_ENABLED", False),
            ),
            ProviderEndpoint(
                key="gemini_primary",
                provider="google",
                model_name=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                endpoint_url=os.environ.get(
                    "GEMINI_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta"
                ),
                api_key_env="GEMINI_API_KEY",
                priority=12,
                max_context_tokens=1048576,
                capabilities=("chat", "tools", "vision", "long_context"),
                enabled=_env_enabled("GEMINI_ENABLED", True),
            ),
            ProviderEndpoint(
                key="xai_primary",
                provider="xai",
                model_name=os.environ.get("XAI_MODEL", "grok-2"),
                endpoint_url=os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1"),
                api_key_env="XAI_API_KEY",
                priority=15,
                max_context_tokens=131072,
                capabilities=("chat", "tools"),
                enabled=_env_enabled("XAI_ENABLED", True),
            ),
            ProviderEndpoint(
                key="vllm_local",
                provider="vllm",
                model_name=os.environ.get("VLLM_MODEL", "qwen2.5-coder-7b-instruct"),
                endpoint_url=os.environ.get(
                    "VLLM_ENDPOINT", "http://localhost:8000/v1/chat/completions"
                ),
                is_local=True,
                priority=50,
                max_context_tokens=32768,
                capabilities=("chat",),
                enabled=_env_enabled("VLLM_ENABLED", False),
            ),
            ProviderEndpoint(
                key="ollama_local",
                provider="ollama",
                model_name=os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
                endpoint_url=os.environ.get(
                    "OLLAMA_ENDPOINT", "http://localhost:11434/v1/chat/completions"
                ),
                is_local=True,
                priority=60,
                max_context_tokens=8192,
                capabilities=("chat",),
                enabled=_env_enabled("OLLAMA_ENABLED", False),
            ),
        ]
        for ep in defaults:
            self._endpoints[ep.key] = ep

    def get(self, key: str) -> Optional[ProviderEndpoint]:
        return self._endpoints.get(key)

    def list_enabled(self) -> List[ProviderEndpoint]:
        return sorted(
            [e for e in self._endpoints.values() if e.enabled],
            key=lambda e: e.priority,
        )

    def list_by_provider(self, provider: str) -> List[ProviderEndpoint]:
        return [e for e in self._endpoints.values() if e.provider == provider]

    def has_credentials(self, key: str) -> bool:
        ep = self.get(key)
        if not ep or not ep.enabled:
            return False
        if ep.is_local:
            return True
        if not ep.api_key_env:
            return False
        if ep.provider == "bedrock":
            return bool(
                os.environ.get("AWS_ACCESS_KEY_ID")
                or os.environ.get("AWS_ROLE_ARN")
                or os.environ.get("AWS_WEB_IDENTITY_TOKEN_FILE")
            )
        return bool(os.environ.get(ep.api_key_env))

    def route(
        self,
        *,
        prefer: str | None = None,
        require_capability: str | None = None,
        local_ok: bool = True,
    ) -> Optional[ProviderEndpoint]:
        candidates = self.list_enabled()
        if prefer:
            preferred = self.get(prefer)
            if preferred and preferred.enabled and self.has_credentials(prefer):
                if require_capability is None or require_capability in preferred.capabilities:
                    return preferred
        for ep in candidates:
            if not local_ok and ep.is_local:
                continue
            if require_capability and require_capability not in ep.capabilities:
                continue
            if self.has_credentials(ep.key):
                return ep
        return None

    def status_snapshot(self) -> Dict[str, Any]:
        return {
            ep.key: {
                "provider": ep.provider,
                "model": ep.model_name,
                "enabled": ep.enabled,
                "has_credentials": self.has_credentials(ep.key),
                "is_local": ep.is_local,
                "priority": ep.priority,
            }
            for ep in sorted(self._endpoints.values(), key=lambda e: e.priority)
        }


provider_registry = ProviderRegistry()
