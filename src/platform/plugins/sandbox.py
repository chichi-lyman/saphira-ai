"""Plugin sandbox registry with risk tiers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set

@dataclass
class PluginSpec:
    name: str
    version: str
    risk_tier: str
    network_allowlist: Set[str] = field(default_factory=set)
    max_cpu_ms: int = 5_000
    max_memory_mb: int = 256
    handler: Optional[Callable[..., Any]] = None

class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, PluginSpec] = {}
    def register(self, spec: PluginSpec) -> None:
        self._plugins[spec.name] = spec
    def get(self, name: str) -> Optional[PluginSpec]:
        return self._plugins.get(name)
    def list(self) -> Dict[str, PluginSpec]:
        return dict(self._plugins)
    def invoke(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        spec = self._plugins.get(name)
        if not spec:
            return {"status": "error", "message": f"Plugin not found: {name}"}
        if spec.risk_tier == "high" and not payload.get("confirmed"):
            return {"status": "needs_confirmation", "plugin": name, "risk_tier": "high"}
        if spec.handler is None:
            return {"status": "ok", "plugin": name, "echo": payload, "sandboxed": True}
        try:
            return {"status": "ok", "plugin": name, "result": spec.handler(payload)}
        except Exception as e:
            return {"status": "error", "plugin": name, "error": str(e)}

plugin_registry = PluginRegistry()
