"""Benchmark excellence pillar definitions for Saphira.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExcellencePillar:
    id: str
    title: str
    saphira_target: str
    design_score: str
    capability: str
    plugin: str
    notes: str
    metadata: dict[str, Any]


EXCELLENCE_PILLARS: tuple[ExcellencePillar, ...] = (
    ExcellencePillar(
        id="latency",
        title="System Latency (TTS/STT/TTFT)",
        saphira_target="180ms–350ms",
        design_score="Tier S — local ONNX/Piper path",
        capability="low_latency_audio",
        plugin="latency",
        notes="Prefer local wake/STT/TTS; stream first tokens; keep cloud path as fallback.",
        metadata={
            "stack": ("onnxruntime-android", "piper", "websocket_audio"),
            "endpoints": ("/api/device/audio", "/api/chat"),
        },
    ),
    ExcellencePillar(
        id="memory",
        title="Memory Retention & Recall Rate",
        saphira_target="98.2%",
        design_score="pgvector + hybrid operational store",
        capability="hybrid_memory_recall",
        plugin="memory_hybrid",
        notes="Durable facts via policy-gated writes; hybrid vector + structured recall.",
        metadata={"stack": ("postgres", "pgvector", "src.memory")},
    ),
    ExcellencePillar(
        id="automation",
        title="Task Automation & Tool Execution",
        saphira_target="94.5%",
        design_score="FastAPI tools + Android a11y + web connectors",
        capability="tool_automation",
        plugin="tool_automation",
        notes="Side effects require Nova Reign / Agent Two approval gates.",
        metadata={"stack": ("fastapi", "plugin_registry", "android_a11y", "firecrawl", "tavily")},
    ),
    ExcellencePillar(
        id="edge",
        title="Edge Hardware / Offline Capability",
        saphira_target="100% native path",
        design_score="Android native + optional Termux/WebGPU/vLLM",
        capability="edge_offline",
        plugin="edge_offline",
        notes="Cloud models optional; device path must function for core companion UX.",
        metadata={"stack": ("android", "termux", "webgpu", "vllm")},
    ),
    ExcellencePillar(
        id="reasoning",
        title="Zero-Shot Reasoning Score",
        saphira_target="84.5 / 100 (continuous improvement)",
        design_score="Scholar + orchestrator multi-step",
        capability="deep_reasoning",
        plugin="reasoning",
        notes="Hard problems route to Scholar; surface answer remains Saphira-only.",
        metadata={"stack": ("scholar", "orchestrator", "tool_grounding")},
    ),
    ExcellencePillar(
        id="privacy",
        title="Data Privacy & Local Ownership",
        saphira_target="10/10",
        design_score="Self-hosted execution ledger + tenant isolation",
        capability="privacy_ledger",
        plugin="privacy_ledger",
        notes="Append-only ledger; credentials never in APK; user owns durable memory.",
        metadata={"stack": ("core.hardening.ledger", "plugin_registry_secrets", "self_host")},
    ),
    ExcellencePillar(
        id="overall",
        title="Overall Rank & Tier",
        saphira_target="Rank 4 (Tier S)",
        design_score="Win on privacy, edge, memory, latency; close reasoning gap",
        capability="excellence_overview",
        plugin="excellence_overview",
        notes="Composite posture — not a single model score.",
        metadata={"tier": "S", "rank_target": 4},
    ),
)


def get_pillar(pillar_id: str) -> ExcellencePillar:
    for pillar in EXCELLENCE_PILLARS:
        if pillar.id == pillar_id:
            return pillar
    raise KeyError(f"Unknown excellence pillar: {pillar_id}")
