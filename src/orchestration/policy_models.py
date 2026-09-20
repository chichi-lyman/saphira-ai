# Copyright © 2026 Chelsea Megan Woods
"""Strict Pydantic v2 contracts for policy gating (ALLOW / REQUIRE_APPROVAL / DENY)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


class PolicyDecision(BaseModel):
    """Outcome of CommercialAuthorityPolicy / Agent Two / NovaReign gates."""

    action: PolicyAction = Field(..., description="Gate decision")
    reason: str = Field(default="", description="Human-readable rationale")
    agent: str = Field(default="", description="Internal agent that decided")
    requires_human: bool = Field(default=False)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class HandoffPayload(BaseModel):
    """Typed JSON contract for inter-agent handoffs."""

    trace_id: str
    from_agent: str
    to_agent: str
    task_id: str
    objective: str
    policy: PolicyAction = PolicyAction.ALLOW
    constraints: list[str] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    context_pack: Optional[dict[str, Any]] = None
    deadline_ms: Optional[int] = None

    model_config = {"extra": "forbid"}
