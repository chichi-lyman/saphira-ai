# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Dual prompt & security engine — splits user intent toward persona vs execution

from typing import Dict, Any, Optional

from src.core.agent_classification import requires_human_confirmation, action_autonomy
from src.core.equilibrium import final_action_score


def analyze_request(user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Lightweight gate before orchestration.
    Full intent parsing still happens in SaphiraCore; this flags L1 and equilibrium.
    """
    context = context or {}
    text = (user_input or "").lower()

    intent = context.get("intent") or "general"
    for key in ("unlock", "lock", "payment", "send_email", "deploy", "migrate"):
        if key.replace("_", " ") in text or key in text:
            intent = key if key != "deploy" else "deploy_prod"
            break

    proposal = {
        "intent": intent,
        "user_requested": True,
        "confirmed": bool(context.get("confirmed")),
        "confidence": context.get("confidence", 0.7),
        "text": user_input,
    }
    eq = final_action_score(proposal)
    needs_confirm = requires_human_confirmation(intent, confirmed=proposal["confirmed"])

    return {
        "intent": intent,
        "autonomy_required": action_autonomy(intent),
        "needs_confirmation": needs_confirm,
        "equilibrium": eq,
        "route": "execution" if eq.get("proceed") and not needs_confirm else "persona_and_gate",
        "owner": "Chelsea Megan Woods",
    }
