# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Canonical Saphira core feature catalog — product + architecture map.

from __future__ import annotations

from typing import Any, Dict, List

# Status: shipped | scaffold | planned
CORE_FEATURES: List[Dict[str, Any]] = [
    # ── 1. Core intelligence & persona ───────────────────────────────
    {
        "id": "memory.session",
        "layer": "intelligence",
        "name": "Short-term session memory",
        "status": "scaffold",
        "module": "src.core.memory_layers",
        "description": "Per-session turn buffer and working context.",
    },
    {
        "id": "memory.persistent",
        "layer": "intelligence",
        "name": "Long-term persistent memory",
        "status": "scaffold",
        "module": "src.core.memory_layers",
        "description": "Preferences, projects, and cross-reboot recall (vector + store).",
    },
    {
        "id": "persona.engine",
        "layer": "intelligence",
        "name": "Persona & tone engine",
        "status": "shipped",
        "module": "src.core.saphira_persona",
        "description": "Samantha-warm + Jarvis-efficient spectrum with secret-mask policy.",
    },
    {
        "id": "persona.tone_shift",
        "layer": "intelligence",
        "name": "Dynamic tone calibration",
        "status": "scaffold",
        "module": "src.core.tone_engine",
        "description": "Context-aware empathy, concise voice mode, stress-aware delivery.",
    },
    {
        "id": "routing.multimodel",
        "layer": "intelligence",
        "name": "Multi-model fallback / routing",
        "status": "scaffold",
        "module": "src.core.model_router",
        "description": "Local/fast API for light tasks; heavy models for deep reasoning.",
    },
    # ── 2. Interface & I/O ───────────────────────────────────────────
    {
        "id": "io.wakeword",
        "layer": "interface",
        "name": "Voice activation & wake word",
        "status": "scaffold",
        "module": "src.core.wake_session",
        "description": "OpenWakeWord → POST /presence/wake; custom Saphira model path.",
    },
    {
        "id": "io.widget",
        "layer": "interface",
        "name": "Floating widget / quick access",
        "status": "scaffold",
        "module": "src.api.presence_router",
        "description": "GET /presence/widget for Android/Flutter/web overlay.",
    },
    {
        "id": "io.multimodal",
        "layer": "interface",
        "name": "Multimodal input",
        "status": "scaffold",
        "module": "src.core.multimodal_registry",
        "description": "Images, audio, screen context registration and routing.",
    },
    {
        "id": "io.voice",
        "layer": "interface",
        "name": "TTS / voice identity",
        "status": "shipped",
        "module": "src.core.saphira_voice",
        "description": "Chelsea voice character via ElevenLabs or compatible TTS.",
    },
    # ── 3. Action & execution ────────────────────────────────────────
    {
        "id": "action.tools",
        "layer": "action",
        "name": "Tool use & function calling",
        "status": "scaffold",
        "module": "src.core.tool_registry",
        "description": "Calendar, web, shell (gated), IoT, notifications via secure tools.",
    },
    {
        "id": "action.guardrails",
        "layer": "action",
        "name": "Error handling & guardrails",
        "status": "scaffold",
        "module": "src.core.tool_registry",
        "description": "L1 confirm gates, L2 bounded, L3 silent background.",
    },
    {
        "id": "action.background",
        "layer": "action",
        "name": "Quiet background execution",
        "status": "shipped",
        "module": "src.core.background_worker",
        "description": "Real-world tasks without blocking conversation.",
    },
    {
        "id": "action.iot",
        "layer": "action",
        "name": "Physical device control",
        "status": "shipped",
        "module": "main / saphira.iot",
        "description": "Media, lights, vacuum, smart bed, print, companion.",
    },
    {
        "id": "action.agents",
        "layer": "action",
        "name": "Multi-agent orchestration",
        "status": "shipped",
        "module": "src.core.orchestrator",
        "description": "Saphira → Aura → security → governance → memory → execution.",
    },
    # ── 4. Deployment & DX ───────────────────────────────────────────
    {
        "id": "dx.setup",
        "layer": "deployment",
        "name": "One-step setup script",
        "status": "scaffold",
        "module": "setup.sh",
        "description": "Install deps, copy .env.example, optional Termux path.",
    },
    {
        "id": "dx.env",
        "layer": "deployment",
        "name": "Environment template",
        "status": "shipped",
        "module": ".env.example",
        "description": "API keys, wake word, TTS/STT, memory backend.",
    },
    {
        "id": "dx.architecture",
        "layer": "deployment",
        "name": "Architecture documentation",
        "status": "scaffold",
        "module": "docs/ARCHITECTURE.md",
        "description": "Wake → persona → router → tools → background flow.",
    },
]


def features_by_layer() -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for f in CORE_FEATURES:
        out.setdefault(f["layer"], []).append(f)
    return out


def feature_summary() -> Dict[str, Any]:
    counts = {"shipped": 0, "scaffold": 0, "planned": 0}
    for f in CORE_FEATURES:
        counts[f.get("status", "planned")] = counts.get(f.get("status", "planned"), 0) + 1
    return {
        "total": len(CORE_FEATURES),
        "counts": counts,
        "layers": list(features_by_layer().keys()),
        "owner": "Chelsea Megan Woods",
        "product": "Saphira AI",
    }
