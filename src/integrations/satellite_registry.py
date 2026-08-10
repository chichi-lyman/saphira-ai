"""Registry of first-party satellite repositories connected to Saphira.

Saphira remains the canonical runtime. Satellite repositories are integrated by
capability and are not blindly copied into the core repository. This keeps
experiments, large runtimes, and provider-specific applications isolated while
letting the executive runtime discover approved capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntegrationMode(str, Enum):
    MODULE = "module"
    ADAPTER = "adapter"
    UI = "ui"
    RUNTIME = "runtime"
    REFERENCE = "reference"


@dataclass(frozen=True)
class Satellite:
    repository: str
    capability: str
    mode: IntegrationMode
    priority: str
    rationale: str
    status: str = "connected-by-contract"


CONNECTED_SATELLITES: tuple[Satellite, ...] = (
    Satellite("chichi-lyman/saphira-asi-core", "cognitive reasoning + vector memory", IntegrationMode.MODULE, "P0", "Primary Saphira reasoning/memory architecture."),
    Satellite("chichi-lyman/saphira-os", "assistant operating-system layer", IntegrationMode.RUNTIME, "P0", "OS/runtime abstraction for the Saphira product."),
    Satellite("chichi-lyman/saphira-ai-platform", "platform services", IntegrationMode.RUNTIME, "P0", "Platform-level Saphira services and deployment surface."),
    Satellite("chichi-lyman/saphira-sales-swarm", "B2B sales automation", IntegrationMode.ADAPTER, "P0", "Scout, enrichment, strategy, outreach, CRM and close workflows."),
    Satellite("chichi-lyman/saphira-sentinel-suite", "security + monitoring", IntegrationMode.ADAPTER, "P0", "Sentinel/security control surface."),
    Satellite("chichi-lyman/saphira-twin-vault", "identity + protected memory", IntegrationMode.ADAPTER, "P0", "Identity/twin vault boundary for persistent user context."),
    Satellite("chichi-lyman/saphira-liaison-ui", "liaison interface", IntegrationMode.UI, "P1", "Dedicated Saphira liaison experience."),
    Satellite("chichi-lyman/v0-saphira-ai", "Saphira web UI", IntegrationMode.UI, "P1", "Existing Saphira UI implementation to reuse where compatible."),
    Satellite("chichi-lyman/v0-ai-assistant-dashboard", "control plane UI", IntegrationMode.UI, "P1", "Operator dashboard foundation."),
    Satellite("chichi-lyman/vercel-ai-chatbot", "web chat surface", IntegrationMode.UI, "P1", "Conversational web implementation."),
    Satellite("chichi-lyman/vercel-ai-chatbot-with-supabase", "persistent chat/data patterns", IntegrationMode.ADAPTER, "P1", "Supabase-backed chat persistence patterns."),
    Satellite("chichi-lyman/saphira-asi-core", "forensic intelligence contracts", IntegrationMode.MODULE, "P0", "Forensic filter, directive routing and decision architecture."),
    Satellite("chichi-lyman/agent-zero", "isolated execution + browser/desktop/tools", IntegrationMode.RUNTIME, "P0", "Use as a sandboxed execution worker; do not duplicate its full application in Saphira core."),
    Satellite("chichi-lyman/agent-gpt", "agent execution", IntegrationMode.ADAPTER, "P1", "Candidate agent worker behind the capability contract."),
    Satellite("chichi-lyman/agent-2", "specialized agent", IntegrationMode.ADAPTER, "P1", "Candidate specialized worker."),
    Satellite("chichi-lyman/aura-agent", "specialized intelligence", IntegrationMode.ADAPTER, "P1", "Candidate specialized worker."),
    Satellite("chichi-lyman/novaaethrea-agent", "NovaAethrea intelligence", IntegrationMode.ADAPTER, "P1", "NovaAethrea worker behind Saphira orchestration."),
    Satellite("chichi-lyman/novareign-agent", "NovaReign intelligence", IntegrationMode.ADAPTER, "P1", "NovaReign worker behind Saphira orchestration."),
    Satellite("chichi-lyman/NovaReign_AI", "NovaReign intelligence platform", IntegrationMode.MODULE, "P1", "First-party NovaReign intelligence capability."),
    Satellite("chichi-lyman/NovaReign-Sovereign-Intelligence", "NovaReign sovereignty layer", IntegrationMode.REFERENCE, "P1", "Strategic intelligence and governance reference."),
    Satellite("chichi-lyman/Nova_Umbrella", "Nova Umbrella ecosystem", IntegrationMode.REFERENCE, "P1", "Strategic umbrella architecture."),
    Satellite("chichi-lyman/nova-umbrella-core", "Nova core", IntegrationMode.MODULE, "P1", "Core Nova Umbrella capability."),
    Satellite("chichi-lyman/nova-umbrella-orchestration", "Nova orchestration", IntegrationMode.ADAPTER, "P1", "Orchestration capability for integration into Saphira."),
    Satellite("chichi-lyman/nova-umbrella-ecosystem", "Nova ecosystem", IntegrationMode.REFERENCE, "P1", "Ecosystem-level architecture and manifests."),
    Satellite("chichi-lyman/Nova-Umbrella-Swarm", "Nova multi-agent swarm", IntegrationMode.ADAPTER, "P1", "Candidate swarm capability."),
    Satellite("chichi-lyman/NexusAgent", "agent networking/orchestration", IntegrationMode.ADAPTER, "P1", "Candidate agent-network layer."),
    Satellite("chichi-lyman/agent-skills", "agent skill library", IntegrationMode.ADAPTER, "P1", "Skill discovery and reusable procedures."),
    Satellite("chichi-lyman/geoserver-mcp", "geospatial MCP", IntegrationMode.ADAPTER, "P2", "Specialized geospatial tool server."),
    Satellite("chichi-lyman/ScriptRunner_for_Termux", "Android/Termux execution", IntegrationMode.ADAPTER, "P1", "Permissioned device execution bridge."),
    Satellite("chichi-lyman/antigravity-sdk-python", "Python SDK integration", IntegrationMode.ADAPTER, "P2", "Reusable SDK integration boundary."),
    Satellite("chichi-lyman/vercel-plugin", "deployment integration", IntegrationMode.ADAPTER, "P2", "Deployment capability boundary."),
    Satellite("chichi-lyman/Chelsea-sales", "sales frontend", IntegrationMode.UI, "P1", "Commercial acquisition surface that can feed Saphira LeadOS."),
    Satellite("chichi-lyman/chelsea-ai-mastermind", "strategy/AI workspace", IntegrationMode.REFERENCE, "P2", "First-party strategy and product reference."),
    Satellite("chichi-lyman/AI-Assistant-1.1", "assistant legacy implementation", IntegrationMode.REFERENCE, "P2", "Legacy capability source; migrate only useful components."),
    Satellite("chichi-lyman/Jarvis-Mark-X", "device/assistant concepts", IntegrationMode.REFERENCE, "P2", "Reference implementation for device-assistant concepts."),
)


def satellites_for_capability(capability: str) -> list[Satellite]:
    needle = capability.lower()
    return [item for item in CONNECTED_SATELLITES if needle in item.capability.lower()]


def connected_repository_names() -> tuple[str, ...]:
    return tuple(item.repository for item in CONNECTED_SATELLITES)
