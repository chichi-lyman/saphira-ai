# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Canonical Saphira autonomy levels + industry scale reference metadata

from enum import Enum
from typing import Dict, Any, List


class SaphiraAutonomy(str, Enum):
    L1_CONFIRM_FIRST = "L1_copilot"
    L2_SUPERVISED = "L2_gated"
    L3_BACKGROUND = "L3_autonomous"


SAPHIRA_LEVEL_INFO: Dict[str, Dict[str, Any]] = {
    SaphiraAutonomy.L1_CONFIRM_FIRST.value: {
        "label": "Confirm First / Hard Gate",
        "execution_autonomy": "none",
        "human_required": True,
        "examples": ["unlock", "payment", "send_email", "deploy_prod", "cold_outreach"],
    },
    SaphiraAutonomy.L2_SUPERVISED.value: {
        "label": "Supervised / Bounded",
        "execution_autonomy": "within_rules_or_sandbox",
        "human_required": False,
        "alert_on_change": True,
        "examples": ["sandbox_code", "ui_draft", "smart_home_adjust", "lyra_local_render"],
    },
    SaphiraAutonomy.L3_BACKGROUND.value: {
        "label": "Silent Background",
        "execution_autonomy": "full_within_policy",
        "human_required": False,
        "notify_on": ["completion", "critical_exception"],
        "examples": ["vector_ingest", "telemetry_index", "context_synthesis", "equilibrium_score"],
    },
}


INDUSTRY_SCALES: Dict[str, Dict[str, Any]] = {
    "sae_j3016": {
        "name": "SAE J3016 Autonomous Driving",
        "levels": 6,
        "range": "0–5",
        "focus": "Vehicle and road automation",
    },
    "openai_agent_style": {
        "name": "OpenAI-style agent scale (conceptual)",
        "levels": 5,
        "range": "L1–L5",
        "focus": "Conversational → reasoners → multi-step agents → innovators → organizations",
    },
    "bessemer_style": {
        "name": "Bessemer-style AI scale (conceptual)",
        "levels": 7,
        "range": "L0–L6",
        "focus": "Prompt chains → agents managing teams of agents",
    },
    "saphira": {
        "name": "Saphira multi-agent safety model",
        "levels": 3,
        "range": "L1–L3",
        "focus": "Operational safety and human-in-the-loop gating",
    },
}


def describe_saphira_levels() -> List[Dict[str, Any]]:
    return [
        {"id": k, **v}
        for k, v in SAPHIRA_LEVEL_INFO.items()
    ]


def industry_reference() -> Dict[str, Any]:
    return {
        "saphira_levels": 3,
        "scales": INDUSTRY_SCALES,
        "owner": "Chelsea Megan Woods",
        "studio": "Woods AI Studio / Lyman Legacies",
    }
