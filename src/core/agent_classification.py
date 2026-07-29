# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Three-dimensional agent classification for Saphira core:
# vertical domain | classic architecture | autonomy level

from enum import Enum
from typing import Dict, Any, List, Set


class VerticalDomain(str, Enum):
    EXECUTIVE_ADMIN = "executive_admin"
    FINANCE = "finance"
    HEALTH_WELLNESS = "health_wellness"
    CREATIVE_MEDIA = "creative_media"
    SOCIAL_GROWTH = "social_growth"
    SMART_HOME_IOT = "smart_home_iot"
    SECURITY_PRIVACY = "security_privacy"
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
    L1_COPILOT = "L1_copilot"          # human prompt + approval every step
    L2_GATED = "L2_gated"              # multi-step OK; pause at checkpoints
    L3_AUTONOMOUS = "L3_autonomous"  # background; notify on done/critical


# Core roster classification
CORE_CLASSIFICATION: Dict[str, Dict[str, Any]] = {
    "saphira": {
        "vertical": VerticalDomain.GENERAL,
        "architectures": [
            ArchitectureType.GOAL_BASED,
            ArchitectureType.MULTI_AGENT,
            ArchitectureType.UTILITY_BASED,
        ],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
    "agent_zero": {
        "vertical": VerticalDomain.SMART_HOME_IOT,
        "architectures": [
            ArchitectureType.SIMPLE_REFLEX,
            ArchitectureType.GOAL_BASED,
            ArchitectureType.EMBODIED,
        ],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
    },
    "agent_two": {
        "vertical": VerticalDomain.SECURITY_PRIVACY,
        "architectures": [
            ArchitectureType.SIMPLE_REFLEX,
            ArchitectureType.MODEL_BASED,
        ],
        "default_autonomy": AutonomyLevel.L1_COPILOT,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
    "aura": {
        "vertical": VerticalDomain.SMART_HOME_IOT,
        "architectures": [
            ArchitectureType.MODEL_BASED,
            ArchitectureType.EMBODIED,
        ],
        "default_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
    },
    "nova_reign": {
        "vertical": VerticalDomain.SECURITY_PRIVACY,
        "architectures": [
            ArchitectureType.SIMPLE_REFLEX,
            ArchitectureType.GOAL_BASED,
        ],
        "default_autonomy": AutonomyLevel.L2_GATED,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
    "nova_aethrea": {
        "vertical": VerticalDomain.GENERAL,
        "architectures": [
            ArchitectureType.MODEL_BASED,
            ArchitectureType.LEARNING,
        ],
        "default_autonomy": AutonomyLevel.L3_AUTONOMOUS,
        "max_autonomy": AutonomyLevel.L3_AUTONOMOUS,
    },
}

# Domain specialists (existing / planned)
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
    "boundary_coach": {
        "vertical": VerticalDomain.HEALTH_WELLNESS,
        "architectures": [ArchitectureType.GOAL_BASED],
        "default_autonomy": AutonomyLevel.L1_COPILOT,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
    "relationship_agent": {
        "vertical": VerticalDomain.GENERAL,
        "architectures": [ArchitectureType.MODEL_BASED, ArchitectureType.GOAL_BASED],
        "default_autonomy": AutonomyLevel.L1_COPILOT,
        "max_autonomy": AutonomyLevel.L2_GATED,
    },
}

# Intent → minimum autonomy required (higher = more human control needed at gate)
# L1 = must confirm; L2 = gated OK; L3 = may run proactive
INTENT_AUTONOMY: Dict[str, AutonomyLevel] = {
    "unlock": AutonomyLevel.L1_COPILOT,
    "lock": AutonomyLevel.L1_COPILOT,
    "turn_on": AutonomyLevel.L2_GATED,
    "turn_off": AutonomyLevel.L2_GATED,
    "set_brightness": AutonomyLevel.L2_GATED,
    "set_temperature": AutonomyLevel.L2_GATED,
    "activate_scene": AutonomyLevel.L2_GATED,
    "general": AutonomyLevel.L1_COPILOT,
    "send_email": AutonomyLevel.L1_COPILOT,
    "payment": AutonomyLevel.L1_COPILOT,
}


def classify_core_agent(name: str) -> Dict[str, Any]:
    name = (name or "").lower()
    if name in CORE_CLASSIFICATION:
        data = dict(CORE_CLASSIFICATION[name])
    elif name in SPECIALIST_CLASSIFICATION:
        data = dict(SPECIALIST_CLASSIFICATION[name])
    else:
        data = {
            "vertical": VerticalDomain.GENERAL,
            "architectures": [ArchitectureType.SIMPLE_REFLEX],
            "default_autonomy": AutonomyLevel.L1_COPILOT,
            "max_autonomy": AutonomyLevel.L1_COPILOT,
        }
    data["name"] = name
    data["vertical"] = data["vertical"].value if isinstance(data["vertical"], Enum) else data["vertical"]
    data["architectures"] = [
        a.value if isinstance(a, Enum) else a for a in data["architectures"]
    ]
    data["default_autonomy"] = (
        data["default_autonomy"].value
        if isinstance(data["default_autonomy"], Enum)
        else data["default_autonomy"]
    )
    data["max_autonomy"] = (
        data["max_autonomy"].value
        if isinstance(data["max_autonomy"], Enum)
        else data["max_autonomy"]
    )
    return data


def action_autonomy(intent: str) -> str:
    intent = (intent or "general").lower().strip()
    level = INTENT_AUTONOMY.get(intent, AutonomyLevel.L1_COPILOT)
    return level.value if isinstance(level, Enum) else level


def requires_human_confirmation(intent: str, confirmed: bool = False) -> bool:
    """True if this intent may not proceed without confirmed=True."""
    level = INTENT_AUTONOMY.get((intent or "").lower(), AutonomyLevel.L1_COPILOT)
    if level == AutonomyLevel.L1_COPILOT and not confirmed:
        return True
    if intent in ("unlock", "lock", "send_email", "payment") and not confirmed:
        return True
    return False


def all_verticals() -> List[str]:
    return [v.value for v in VerticalDomain]


def all_architectures() -> List[str]:
    return [a.value for a in ArchitectureType]
