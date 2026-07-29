# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Saphira multimodal capability registry — what the orchestrator may route to

from enum import Enum
from typing import Dict, Any, List


class MultimodalDomain(str, Enum):
    REALTIME_VOICE = "realtime_voice"
    AIR_GESTURES = "air_gestures"
    BIOMETRIC_AUTH = "biometric_auth"
    PARAMETRIC_CAD = "parametric_cad"
    WIRELESS_PRINT = "wireless_print"
    WEB_AUTOMATION = "web_automation"
    SMART_ENVIRONMENT = "smart_environment"
    CONTEXT_MEMORY = "context_memory"


CAPABILITY_MATRIX: Dict[str, Dict[str, Any]] = {
    MultimodalDomain.REALTIME_VOICE.value: {
        "executes": "Dual-pipeline conversational speech, interrupt support, Samantha cadence",
        "stack": ["gemini_native_audio", "elevenlabs_chelsea_voice"],
        "default_autonomy": "L2_gated",
        "delegate": ["saphira", "saphira_translator"],
    },
    MultimodalDomain.AIR_GESTURES.value: {
        "executes": "Spatial UI drag/click/release on floating overlays",
        "stack": ["mediapipe_hands"],
        "default_autonomy": "L2_gated",
        "delegate": ["aura", "ada_bridge"],
    },
    MultimodalDomain.BIOMETRIC_AUTH.value: {
        "executes": "Face landmarker for layer unlock / action auth",
        "stack": ["mediapipe_face"],
        "default_autonomy": "L1_copilot",
        "delegate": ["agent_two", "aura"],
    },
    MultimodalDomain.PARAMETRIC_CAD.value: {
        "executes": "Voice to parametric solid geometry, STL export",
        "stack": ["build123d"],
        "default_autonomy": "L2_gated",
        "delegate": ["agent_zero", "ada_bridge"],
    },
    MultimodalDomain.WIRELESS_PRINT.value: {
        "executes": "Discover printers, slice, send job over Wi-Fi",
        "stack": ["orcaslicer", "moonraker", "prusalink", "klipper"],
        "default_autonomy": "L2_gated",
        "delegate": ["agent_zero"],
    },
    MultimodalDomain.WEB_AUTOMATION.value: {
        "executes": "Navigate, fill forms, extract data",
        "stack": ["playwright", "chromium"],
        "default_autonomy": "L2_gated",
        "delegate": ["agent_zero"],
        "note": "Credentialed submit upgrades to L1",
    },
    MultimodalDomain.SMART_ENVIRONMENT.value: {
        "executes": "Lights, color, power, scenes",
        "stack": ["home_assistant", "matter", "python_kasa"],
        "default_autonomy": "L2_gated",
        "delegate": ["agent_zero", "aura", "nova_aethrea"],
    },
    MultimodalDomain.CONTEXT_MEMORY.value: {
        "executes": "Long-term state, schedules, sandbox, vectors",
        "stack": ["nova_aethrea", "aura", "supabase_vector_optional"],
        "default_autonomy": "L3_autonomous",
        "delegate": ["nova_aethrea", "aura"],
    },
}


def list_capabilities() -> List[Dict[str, Any]]:
    return [
        {"domain": k, **v}
        for k, v in CAPABILITY_MATRIX.items()
    ]


def route_domain(domain: str) -> Dict[str, Any]:
    d = CAPABILITY_MATRIX.get(domain) or CAPABILITY_MATRIX.get(
        domain.lower().replace(" ", "_")
    )
    if not d:
        return {"status": "unknown_domain", "domain": domain}
    return {"status": "ok", "domain": domain, **d, "owner": "Chelsea Megan Woods"}
