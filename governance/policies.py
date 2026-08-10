from __future__ import annotations

import logging
from typing import Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("saphira.capability_policy")

DEFAULT_RESTRICTED_ACTIONS = [
    "drop_database",
    "export_pii_unencrypted",
    "modify_billing_account",
    "system_shell_exec",
]


class CapabilityManifest(BaseModel):
    agent_did: str
    allowed_domains: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    max_cost_per_execution_usd: float = 5.0
    restricted_actions: list[str] = Field(default_factory=lambda: list(DEFAULT_RESTRICTED_ACTIONS))


class CapabilityPolicyEngine:
    def __init__(self, manifests: Optional[Dict[str, CapabilityManifest]] = None):
        self.manifests = manifests or {}

    def register_manifest(self, manifest: CapabilityManifest) -> None:
        self.manifests[manifest.agent_did] = manifest

    def authorize_execution(
        self,
        agent_did: str,
        action: str,
        tool_name: str,
        estimated_cost_usd: float = 0.0,
    ) -> bool:
        manifest = self.manifests.get(agent_did)
        if not manifest:
            raise PermissionError(f"Agent '{agent_did}' lacks a capability manifest.")
        if action in manifest.restricted_actions or tool_name in manifest.restricted_actions:
            raise PermissionError(f"Action '{action}' is forbidden by governance policy.")
        if "*" not in manifest.allowed_tools and tool_name not in manifest.allowed_tools:
            raise PermissionError(f"Agent '{agent_did}' is not authorized to use '{tool_name}'.")
        if estimated_cost_usd > manifest.max_cost_per_execution_usd:
            raise PermissionError("Execution cost exceeds the agent's maximum limit.")
        return True
