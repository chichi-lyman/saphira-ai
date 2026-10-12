# Copyright © 2026 Chelsea Megan Woods
# Saphira AI — Persistent Goal Ledger
#
# Durable goals stored in PostgreSQL (or file-backed for local).
# Authoritative even if a worker crashes or a queue message is redelivered.
# Use with Celery/Redis for background work and idempotency keys.

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("saphira.goal_ledger")

DEFAULT_PATH = Path(os.getenv("SAPHIRA_GOAL_LEDGER_PATH", "data/goal_ledger.json"))


class GoalStatus(str, Enum):
    PROPOSED = "proposed"
    QUEUED = "queued"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ApprovalState(str, Enum):
    REQUIRED = "required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"


class GoalStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    depends_on: List[str] = Field(default_factory=list)
    status: GoalStatus = GoalStatus.PROPOSED
    result: Optional[Dict[str, Any]] = None


class Goal(BaseModel):
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    objective: str
    steps: List[GoalStep] = Field(default_factory=list)
    status: GoalStatus = GoalStatus.PROPOSED
    approval_state: ApprovalState = ApprovalState.NOT_REQUIRED
    next_run_at: Optional[datetime] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GoalLedger:
    """File-backed goal ledger. Swap for asyncpg + PostgreSQL in production."""

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._goals: Dict[str, Goal] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                for item in data.get("goals", []):
                    g = Goal.model_validate(item)
                    self._goals[g.goal_id] = g
            except Exception as exc:
                logger.warning("Failed to load goal ledger: %s", exc)

    def _save(self) -> None:
        payload = {
            "goals": [g.model_dump(mode="json") for g in self._goals.values()],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def create(self, user_id: str, objective: str, **kwargs: Any) -> Goal:
        goal = Goal(user_id=user_id, objective=objective, **kwargs)
        self._goals[goal.goal_id] = goal
        self._save()
        logger.info("Created goal %s for user %s", goal.goal_id, user_id)
        return goal

    def get(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def list_for_user(self, user_id: str) -> List[Goal]:
        return [g for g in self._goals.values() if g.user_id == user_id]

    def update_status(
        self,
        goal_id: str,
        status: GoalStatus,
        *,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Goal:
        goal = self._goals.get(goal_id)
        if not goal:
            raise KeyError(f"Goal {goal_id} not found")
        goal.status = status
        goal.updated_at = datetime.now(timezone.utc)
        if evidence:
            goal.evidence.append(evidence)
        self._save()
        return goal

    def set_approval(self, goal_id: str, state: ApprovalState) -> Goal:
        goal = self._goals.get(goal_id)
        if not goal:
            raise KeyError(f"Goal {goal_id} not found")
        goal.approval_state = state
        goal.updated_at = datetime.now(timezone.utc)
        self._save()
        return goal
