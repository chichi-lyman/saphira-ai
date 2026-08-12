"""Typed client surface for policy dry-run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.platform.policy import AutonomyPolicy, CounterfactualPreview

@dataclass
class SaphiraClientConfig:
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    tenant_id: str = "default"

class SaphiraClient:
    def __init__(self, config: Optional[SaphiraClientConfig] = None):
        self.config = config or SaphiraClientConfig()
        self.policy = AutonomyPolicy(tenant_id=self.config.tenant_id)
    def dry_run_capability(self, capability: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        decision = self.policy.decide(capability, context)
        preview = None
        if decision.requires_confirmation:
            preview = CounterfactualPreview.build(intent=str((context or {}).get("intent", capability)), capability=capability, tools=(context or {}).get("tools", []), side_effects=(context or {}).get("side_effects", []), rollback=(context or {}).get("rollback"))
        return {"allowed": decision.allowed, "level": decision.level.value, "requires_confirmation": decision.requires_confirmation, "reason": decision.reason, "preview": preview}
    def health_path(self) -> str:
        return f"{self.config.base_url.rstrip('/')}/health"
