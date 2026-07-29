# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# NovaReign (Yang) + NovaAethrea (Yin) equilibrium mediator

from typing import Dict, Any, Optional


def score_reign_proposal(proposal: Dict[str, Any]) -> float:
    """
    Expansion / optimization score (0–1).
    Higher = stronger push toward action / creativity / velocity.
    """
    base = 0.5
    if proposal.get("priority") == "high":
        base += 0.2
    if proposal.get("user_requested"):
        base += 0.15
    if proposal.get("creative"):
        base += 0.1
    if proposal.get("confidence"):
        try:
            base += 0.15 * float(proposal["confidence"])
        except (TypeError, ValueError):
            pass
    return max(0.0, min(1.0, base))


def score_aethrea_constraint(proposal: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> float:
    """
    Constraint / safety score contribution (typically negative or damping).
    More risk → lower (more negative) contribution.
    """
    damp = 0.0
    intent = (proposal.get("intent") or proposal.get("action") or "").lower()
    sensitive = {"unlock", "lock", "payment", "send_email", "migrate", "deploy_prod"}
    if intent in sensitive:
        damp -= 0.45
    if proposal.get("requires_confirmation") and not proposal.get("confirmed"):
        damp -= 0.5
    if policy and intent in (policy.get("deny_list") or []):
        damp -= 1.0
    if proposal.get("anomaly"):
        damp -= 0.3
    return damp


def final_action_score(
    proposal: Dict[str, Any],
    policy: Optional[Dict[str, Any]] = None,
    threshold: float = 0.35,
) -> Dict[str, Any]:
    """
    Final_Action_Score ≈ NovaReign_Score + NovaAethrea_Constraint
    Proceed only if score >= threshold and not hard-blocked.
    """
    reign = score_reign_proposal(proposal)
    aethrea = score_aethrea_constraint(proposal, policy)
    total = reign + aethrea

    hard_block = False
    intent = (proposal.get("intent") or "").lower()
    if intent in ("unlock", "payment", "send_email", "migrate", "deploy_prod") and not proposal.get("confirmed"):
        hard_block = True
    if policy and intent in (policy.get("deny_list") or []):
        hard_block = True

    proceed = (not hard_block) and (total >= threshold)

    return {
        "nova_reign_score": round(reign, 3),
        "nova_aethrea_constraint": round(aethrea, 3),
        "final_action_score": round(total, 3),
        "threshold": threshold,
        "hard_block": hard_block,
        "proceed": proceed,
        "mediator": "nova_equilibrium",
        "owner": "Chelsea Megan Woods",
    }
