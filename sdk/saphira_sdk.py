from __future__ import annotations

import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("saphira.sdk")


class AgentManifest:
    def __init__(self, name: str, version: str, description: str, capabilities: list[str], pricing_model: str = "USAGE_BASED", price_per_execution_usd: float = 0.01):
        self.name = name
        self.version = version
        self.description = description
        self.capabilities = capabilities
        self.pricing_model = pricing_model
        self.price_per_execution_usd = price_per_execution_usd


class SaphiraAgent:
    def __init__(self, manifest: AgentManifest):
        self.manifest = manifest
        self.tools: dict[str, Callable[..., Any]] = {}

    def register_tool(self, name: str, description: str = ""):
        def decorator(func: Callable[..., Any]):
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any):
                logger.info("SDK tool execution: %s -> %s", self.manifest.name, name)
                return func(*args, **kwargs)
            self.tools[name] = wrapper
            return wrapper
        return decorator

    def export_package(self) -> dict[str, Any]:
        return {
            "name": self.manifest.name,
            "version": self.manifest.version,
            "description": self.manifest.description,
            "capabilities": self.manifest.capabilities,
            "pricing": {"model": self.manifest.pricing_model, "price_usd": self.manifest.price_per_execution_usd},
            "registered_tools": list(self.tools),
        }
