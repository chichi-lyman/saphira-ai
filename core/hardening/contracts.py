"""Typed contracts separating model proposals from executable side effects."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ToolExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=1)
    deadline_ms: int = Field(default=30_000, ge=1, le=300_000)


class ModelActionProposal(BaseModel):
    """Untrusted model output. It is never an executable command."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    intent: str = Field(min_length=1)
    tool: str | None = None
    operation: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str | None = None
