"""Provider-neutral plugin registry for Saphira integrations.

Plugins are capabilities exposed to the executive runtime. Credentials and
provider SDKs stay outside the registry; adapters implement the actual calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    capabilities: tuple[str, ...]
    scopes: tuple[str, ...] = ()
    requires_approval: bool = False
    side_effects: bool = False
    enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class PluginAdapter(Protocol):
    async def health(self) -> dict[str, Any]: ...

    async def invoke(self, capability: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


class PluginRegistry:
    """In-process registry used by the executive runtime and control plane."""

    def __init__(self) -> None:
        self._manifests: dict[str, PluginManifest] = {}
        self._adapters: dict[str, PluginAdapter] = {}

    def register(self, manifest: PluginManifest, adapter: PluginAdapter | None = None) -> None:
        self._manifests[manifest.name] = manifest
        if adapter is not None:
            self._adapters[manifest.name] = adapter

    def get(self, name: str) -> PluginManifest:
        return self._manifests[name]

    def list(self, *, enabled_only: bool = False) -> list[PluginManifest]:
        values = list(self._manifests.values())
        if enabled_only:
            values = [manifest for manifest in values if manifest.enabled]
        return sorted(values, key=lambda item: item.name)

    def resolve_capability(self, capability: str) -> list[PluginManifest]:
        return [
            manifest
            for manifest in self._manifests.values()
            if capability in manifest.capabilities and manifest.enabled
        ]

    async def health(self, name: str) -> dict[str, Any]:
        adapter = self._adapters[name]
        return await adapter.health()

    async def invoke(
        self,
        name: str,
        capability: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        manifest = self.get(name)
        if not manifest.enabled:
            raise RuntimeError(f"Plugin '{name}' is disabled")
        if capability not in manifest.capabilities:
            raise ValueError(f"Capability '{capability}' is not exposed by '{name}'")
        adapter = self._adapters[name]
        return await adapter.invoke(capability, arguments or {})


def default_plugin_manifests() -> tuple[PluginManifest, ...]:
    """Catalog of integrations Saphira is designed to support.

    These manifests define integration boundaries, not claims that credentials
    or external services are already connected in every deployment.
    """
    return (
        PluginManifest("github", "1.0", "Repository, issue, and pull-request automation", ("development", "repository"), ("repo",)),
        PluginManifest("shopify", "1.0", "Commerce catalog, order, customer, and storefront automation", ("commerce",), ("read", "write"), True, True),
        PluginManifest("stripe", "1.0", "Subscription and billing automation", ("billing",), ("billing",), True, True),
        PluginManifest("crm", "1.0", "Lead, account, pipeline, and customer operations", ("sales", "crm"), ("read", "write"), True, True),
        PluginManifest("calendar", "1.0", "Scheduling and calendar operations", ("calendar",), ("read", "write"), True, True),
        PluginManifest("communications", "1.0", "Approved email and messaging workflows", ("communications", "outreach"), ("send",), True, True),
        PluginManifest("web_research", "1.0", "Web grounding and research workflows", ("research", "grounding"), ("search",)),
        PluginManifest("memory", "1.0", "Persistent memory and event retrieval", ("memory",), ("read", "write")),
        PluginManifest("device", "1.0", "Permissioned Android and smart-environment actions", ("device", "smart_environment"), ("control",), True, True),
        PluginManifest("analytics", "1.0", "Business and system telemetry", ("analytics", "business_intelligence"), ("read",)),
    )
