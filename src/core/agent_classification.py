# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Nova ecosystem classification — vertical | architecture | autonomy

from enum import Enum
from typing import Dict, Any, List


class VerticalDomain(str, Enum):
    EXECUTIVE_ADMIN = "executive_admin"
    GOVERNANCE = "governance"
    PERCEPTION = "perception"
    DEVELOPER_OPS = "developer_ops"
    SECURITY_BOUNDARY = "security_boundary"
    CREATIVE_MEDIA = "creative_media"
    FINANCE = "finance"
    HEALTH_WELLNESS = "health_wellness"
    SOCIAL_GROWTH = "social_growth"
    SMART_HOME_IOT = "smart_home_iot"
    LEARNING = "learning"
    GENERAL = "general"


class ArchitectureType(str, Enum):
    SIMPLE_REFLEX = "simple_reflex"
    MODEL_BASED = "model_based"
    GOAL_BASED = "goal_based"
    UTILITY_BASED = "utility_based"
    LEARNING = "learning"
    MULTI_AGENT = "multi_agent"
    EMBODIED = "embodied"


class AutonomyLevel(str, Enum):
    L1_COPILOT = "L1_copilot"
    L2_GATED = "L2_gated"
    L3_AUTONOMOUS = "L3_autonomous"


CORE_CLASSIFICATION: Dict[str, Dict[str, Any]] = {
    "saphira": {
        "vertical": VerticalDomain.EXECUTIVE_ADMIN,
        "architectures": [
            ArchitectureType.MULTI_AGENT,
            ArchitectureType.GOAL_BASED,
            ArchitectureType.UTILITY_BASED,
        ],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
        "focus": "Brand face, orchestrator, public interface",
    },
    "nova_reign": {
        "vertical": VerticalDomain.GOVERNANCE,
        "architectures": [
            ArchitectureType.UTILITY_BASED,
            ArchitectureType.LEARNING,
            ArchitectureType.GOAL_BASED,
        ],
        "default_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "focus": "Yang — expansion, momentum, creative proposals",
        "equilibrium": "yang",
    },
    "nova_aethrea": {
        "vertical": VerticalDomain.GOVERNANCE,
        "architectures": [
            ArchitectureType.MODEL_BASED,
            ArchitectureType.LEARNING,
        ],
        "default_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "focus": "Yin — constraint, risk, memory, policy",
        "equilibrium": "yin",
    },
    "aura": {
        "vertical": VerticalDomain.PERCEPTION,
        "architectures": [
            ArchitectureType.LEARNING,
            ArchitectureType.MULTI_AGENT,
            ArchitectureType.SIMPLE_REFLEX,
            ArchitectureType.EMBODIED,
        ],
        "default_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "focus": "Perception, telemetry, context retrieval",
    },
    "agent_zero": {
        "vertical": VerticalDomain.DEVELOPER_OPS,
        "architectures": [
            ArchitectureType.GOAL_BASED,
            ArchitectureType.MODEL_BASED,
            ArchitectureType.LEARNING,
            ArchitectureType.EMBODIED,
        ],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
        "focus": "Code, sandbox, deploy — L1 gate on prod migrations",
    },
    "agent_two": {
        "vertical": VerticalDomain.SECURITY_BOUNDARY,
        "architectures": [
            ArchitectureType.SIMPLE_REFLEX,
            ArchitectureType.MODEL_BASED,
        ],
        "default_autonomy": AutonomyLevel.L1_COPILOT,
        "max_autonomy": AutonomyLevel.L1_COPILOT,
        "focus": "Hard gates, auth, panic lockdown",
    },
    "lyra": {
        "vertical": VerticalDomain.CREATIVE_MEDIA,
        "architectures": [
            ArchitectureType.MODEL_BASED,
            ArchitectureType.GOAL_BASED,
        ],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
        "focus": "Creative direction, UI/UX, social drafts",
    },
}

SPECIALIST_CLASSIFICATION: Dict[str, Dict[str, Any]] = {
    "biometric_stress": {
        "vertical": VerticalDomain.HEALTH_WELLNESS,
        "architectures": [ArchitectureType.MODEL_BASED, ArchitectureType.LEARNING],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
    },
    "lifestyle_orchestrator": {
        "vertical": VerticalDomain.HEALTH_WELLNESS,
        "architectures": [ArchitectureType.GOAL_BASED, ArchitectureType.UTILITY_BASED],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
    "admin_resolver": {
        "vertical": VerticalDomain.EXECUTIVE_ADMIN,
        "architectures": [ArchitectureType.GOAL_BASED, ArchitectureType.MULTI_AGENT],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
}

INTENT_AUTONOMY: Dict[str, AutonomyLevel] = {
    "unlock": AutonomyLevel.L1_COPILOT,
    "lock": AutonomyLevel.L1_COPILOT,
    "payment": AutonomyLevel.L1_COPILOT,
    "send_email": AutonomyLevel.L1_COPILOT,
    "migrate": AutonomyLevel.L1_COPILOT,
    "deploy_prod": AutonomyLevel.L1_COPILOT,
    "turn_on": AutonomyLevel.L2_GATED,
    "turn_off": AutonomyLevel.L2_GATED,
    "set_brightness": AutonomyLevel.L2_GATED,
    "set_temperature": AutonomyLevel.L2_GATED,
    "activate_scene": AutonomyLevel.L2_GATED,
    "social_draft": AutonomyLevel.L1_COPILOT,
    "general": AutonomyLevel.L1_COPILOT,
}


def _serialize(data: Dict[str, Any], name: str) -> Dict[str, Any]:
    out = dict(data)
    out["name"] = name
    for key in ("vertical", "default_autonomy", "max_autonomy"):
        if key in out and isinstance(out[key], Enum):
            out[key] = out[key].value
    if "architectures" in out:
        out["architectures"] = [
            a.value if isinstance(a, Enum) else a for a in out["architectures"]
        ]
    return out


def classify_core_agent(name: str) -> Dict[str, Any]:
    name = (name or "").lower().replace(" ", "_")
    if name in CORE_CLASSIFICATION:
        return _serialize(CORE_CLASSIFICATION[name], name)
    if name in SPECIALIST_CLASSIFICATION:
        return _serialize(SPECIALIST_CLASSIFICATION[name], name)
    return _serialize(
        {
            "vertical": VerticalDomain.GENERAL,
            "architectures": [ArchitectureType.SIMPLE_REFLEX],
            "default_autonomy": AutonomyLevel.L1_COPILOT,
            "max_autonomy": AutonomyLevel.L1_COPILOT,
            "focus": "Unclassified specialist — default L1",
        },
        name,
    )


def action_autonomy(intent: str) -> str:
    level = INTENT_AUTONOMY.get((intent or "general").lower(), AutonomyLevel.L1_COPILOT)
    return level.value if isinstance(level, Enum) else level


def requires_human_confirmation(intent: str, confirmed: bool = False) -> bool:
    level = INTENT_AUTONOMY.get((intent or "").lower(), AutonomyLevel.L1_COPILOT)
    if level == AutonomyLevel.L1_COPILOT and not confirmed:
        return True
    if (intent or "") in ("unlock", "lock", "payment", "send_email", "migrate", "deploy_prod") and not confirmed:
        return True
    return False


def ecosystem_matrix() -> List[Dict[str, Any]]:
    return [classify_core_agent(n) for n in CORE_CLASSIFICATION]
