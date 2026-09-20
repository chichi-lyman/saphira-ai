# Copyright © 2026 Chelsea Megan Woods
"""FastAPI router exposing typed policy evaluation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.orchestration.policy_models import PolicyAction, PolicyDecision, HandoffPayload

router = APIRouter(prefix="/policy", tags=["policy"])


@router.post("/evaluate", response_model=PolicyDecision)
async def evaluate_policy(payload: HandoffPayload) -> PolicyDecision:
    """Evaluate a handoff against commercial / security policy.

    Real implementation consults CommercialAuthorityPolicy and Agent Two.
    This endpoint enforces the typed contract surface.
    """
    if payload.policy == PolicyAction.DENY:
        return PolicyDecision(
            action=PolicyAction.DENY,
            reason="Explicit DENY on envelope",
            agent=payload.from_agent,
            requires_human=False,
        )
    if payload.policy == PolicyAction.REQUIRE_APPROVAL:
        return PolicyDecision(
            action=PolicyAction.REQUIRE_APPROVAL,
            reason="Envelope requires human approval",
            agent=payload.from_agent,
            requires_human=True,
        )
    return PolicyDecision(
        action=PolicyAction.ALLOW,
        reason="Envelope ALLOW",
        agent=payload.from_agent,
        requires_human=False,
    )


@router.get("/actions")
async def list_actions() -> dict:
    return {"actions": [a.value for a in PolicyAction]}
