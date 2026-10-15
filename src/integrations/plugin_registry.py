"""Provider-neutral plugin registry for Saphira integrations.

Plugins are capabilities exposed to the executive runtime. Credentials and
provider SDKs stay outside the registry; adapters implement the actual calls.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
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
        # --- Existing core integrations ---
        PluginManifest(
            "github",
            "1.0",
            "Repository, issue, and pull-request automation",
            ("development", "repository"),
            ("repo",),
        ),
        PluginManifest(
            "shopify",
            "1.0",
            "Commerce catalog, order, customer, and storefront automation",
            ("commerce",),
            ("read", "write"),
            True,
            True,
        ),
        PluginManifest(
            "stripe",
            "1.0",
            "Subscription billing, checkout links, and financial micro-transactions",
            ("billing", "payments"),
            ("billing",),
            True,
            True,
            metadata={"gateway": "stripe", "category": "commerce"},
        ),
        PluginManifest(
            "crm",
            "1.0",
            "Lead, account, pipeline, and customer operations",
            ("sales", "crm"),
            ("read", "write"),
            True,
            True,
        ),
        PluginManifest(
            "calendar",
            "1.0",
            "Scheduling and calendar operations",
            ("calendar",),
            ("read", "write"),
            True,
            True,
        ),
        PluginManifest(
            "communications",
            "1.0",
            "Approved email and messaging workflows",
            ("communications", "outreach"),
            ("send",),
            True,
            True,
        ),
        PluginManifest(
            "web_research",
            "1.1",
            "Live web browsing, scraping, fact verification (Firecrawl/Tavily/Browserbase)",
            ("research", "grounding", "web_search"),
            ("search",),
            metadata={"category": "core_utility", "providers": ("firecrawl", "tavily", "browserbase")},
        ),
        PluginManifest(
            "memory",
            "1.0",
            "Persistent memory and event retrieval",
            ("memory",),
            ("read", "write"),
        ),
        PluginManifest(
            "device",
            "1.0",
            "Permissioned Android and smart-environment actions",
            ("device", "smart_environment"),
            ("control",),
            True,
            True,
        ),
        PluginManifest(
            "analytics",
            "1.0",
            "Business and system telemetry",
            ("analytics", "business_intelligence"),
            ("read",),
        ),
        # --- Core Utility Plugins ---
        PluginManifest(
            "google_workspace",
            "1.0",
            "Google Workspace connector: schedules appointments, drafts emails, reads Drive files",
            ("workspace", "calendar", "email", "drive", "productivity"),
            ("read", "write"),
            True,
            True,
            metadata={"providers": ("gmail", "google_calendar", "google_drive"), "category": "core_utility"},
        ),
        PluginManifest(
            "microsoft_365",
            "1.0",
            "Microsoft 365 connector: Outlook, Teams, OneDrive, and productivity automation",
            ("workspace", "calendar", "email", "drive", "productivity"),
            ("read", "write"),
            True,
            True,
            metadata={"providers": ("outlook", "teams", "onedrive"), "category": "core_utility"},
        ),
        PluginManifest(
            "document_intelligence",
            "1.0",
            "Native parsing and summarization of PDFs, spreadsheets, and text documents",
            ("document", "pdf", "spreadsheet", "summarization"),
            ("read",),
            metadata={"category": "core_utility"},
        ),
        PluginManifest(
            "code_interpreter",
            "1.0",
            "Live Python sandbox for data analysis, math models, charts, and downloadable assets",
            ("code", "sandbox", "python", "analysis"),
            ("execute",),
            True,
            False,
            metadata={"category": "core_utility"},
        ),
        PluginManifest(
            "image_generation",
            "1.0",
            "Visual creation bridge (DALL·E / Midjourney-class) for rapid asset generation",
            ("media", "image", "generation"),
            ("generate",),
            True,
            True,
            metadata={"category": "core_utility"},
        ),
        # --- Extended Workflow ---
        PluginManifest(
            "zapier",
            "1.0",
            "Zapier / Make.com action bridge to 5,000+ third-party apps for background workflows",
            ("automation", "workflow", "integration"),
            ("trigger", "action"),
            True,
            True,
            metadata={"aliases": ("make.com", "integromat"), "category": "extended_workflow"},
        ),
        PluginManifest(
            "twilio",
            "1.0",
            "Voice-to-text calls, SMS alerts, and multi-channel messaging gateway",
            ("communications", "sms", "voice", "messaging"),
            ("send", "call"),
            True,
            True,
            metadata={"category": "extended_workflow"},
        ),
        PluginManifest(
            "social_content",
            "1.0",
            "Media parsing: ingest video/links, extract transcripts, generate social captions and summaries",
            ("social", "content", "transcript", "caption"),
            ("read", "generate"),
            True,
            True,
            metadata={"category": "extended_workflow"},
        ),
        # --- Competitive excellence pillars (all agents may invoke) ---
        PluginManifest(
            "latency",
            "1.0",
            "Low-latency TTS/STT/TTFT path (local ONNX/Piper + streaming); target 180–350ms",
            ("low_latency_audio", "tts", "stt", "ttft"),
            ("audio",),
            metadata={
                "category": "excellence",
                "target": "180ms-350ms",
                "agents": ("saphira", "aura", "agent_zero"),
            },
        ),
        PluginManifest(
            "memory_hybrid",
            "1.0",
            "Hybrid memory retention/recall (pgvector + operational store); design target 98.2%",
            ("hybrid_memory_recall", "memory", "vector_search"),
            ("read", "write"),
            metadata={
                "category": "excellence",
                "target": "98.2%",
                "agents": ("saphira", "scholar", "novaaethrea"),
            },
        ),
        PluginManifest(
            "tool_automation",
            "1.0",
            "High-reliability tool execution (FastAPI fabric, Android a11y, web connectors); target 94.5%",
            ("tool_automation", "automation", "device_action"),
            ("execute",),
            True,
            True,
            metadata={
                "category": "excellence",
                "target": "94.5%",
                "agents": ("agent_two", "novareign", "aura"),
            },
        ),
        PluginManifest(
            "edge_offline",
            "1.0",
            "Edge/offline native path (Android, Termux, WebGPU, optional vLLM)",
            ("edge_offline", "offline", "on_device"),
            ("local",),
            metadata={
                "category": "excellence",
                "target": "100% native path",
                "agents": ("agent_zero", "aura", "cipher"),
            },
        ),
        PluginManifest(
            "reasoning",
            "1.0",
            "Deep/zero-shot reasoning via Scholar + orchestrator multi-step plans",
            ("deep_reasoning", "reasoning", "analysis"),
            ("think",),
            metadata={
                "category": "excellence",
                "target": "84.5/100+",
                "agents": ("scholar", "novaaethrea", "saphira", "orchestrator"),
            },
        ),
        PluginManifest(
            "privacy_ledger",
            "1.0",
            "Self-hosted privacy & ownership: append-only execution ledger, tenant isolation",
            ("privacy_ledger", "privacy", "audit"),
            ("audit",),
            metadata={
                "category": "excellence",
                "target": "10/10",
                "agents": ("cipher", "agent_two", "novareign", "saphira"),
            },
        ),
        PluginManifest(
            "excellence_overview",
            "1.0",
            "Composite excellence posture (Tier S): latency, memory, automation, edge, privacy, reasoning",
            ("excellence_overview", "benchmark"),
            ("read",),
            metadata={"category": "excellence", "tier": "S", "rank_target": 4},
        ),
    )
