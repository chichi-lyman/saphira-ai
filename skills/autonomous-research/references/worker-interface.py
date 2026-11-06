# Copyright © 2026 Chelsea Megan Woods
# Nova Umbrella / Saphira AI – Autonomous Research Worker interface

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class WorkerStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BUDGET_EXCEEDED = "budget_exceeded"
    POLICY_DENIED = "policy_denied"


class ResearchStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str  # navigate | extract | search | evaluate | stop
    url: Optional[str] = None
    args: dict[str, Any] = Field(default_factory=dict)
    result_summary: Optional[str] = None
    evidence_refs: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cost_usd: float = 0.0


class ResearchEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_url: str
    extracted_at: datetime
    record: dict[str, Any]  # must validate against contract.output_schema
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: dict[str, Any] = Field(default_factory=dict)


class WorkerResult(BaseModel):
    contract_id: str
    status: WorkerStatus
    steps: list[ResearchStep]
    evidence: list[ResearchEvidence]
    final_summary: Optional[str] = None
    total_cost_usd: float = 0.0
    started_at: datetime
    finished_at: Optional[datetime] = None
    error: Optional[str] = None


class AutonomousResearchWorker(ABC):
    """
    Bound execution surface owned by Agent Two.
    Nova Reign creates the contract; this worker never invents new goals.
    """

    @abstractmethod
    async def start(self, contract: dict) -> str:
        """Validate contract, enforce allow-list & budget, return run_id."""
        ...

    @abstractmethod
    async def run(self, run_id: str) -> AsyncIterator[ResearchStep]:
        """
        Yield steps as they complete.
        Must stop on budget, policy violation, or success_criteria met.
        """
        ...

    @abstractmethod
    async def cancel(self, run_id: str) -> None:
        """Immediate soft kill – no further network calls."""
        ...

    @abstractmethod
    async def get_result(self, run_id: str) -> WorkerResult:
        """Final aggregated result + evidence trail for NovaAethrea."""
        ...

    @abstractmethod
    async def dry_run(self, contract: dict) -> list[ResearchStep]:
        """Simulate without network side-effects (used for user preview)."""
        ...
