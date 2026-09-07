"""Deterministic execution guard for Saphira actions.

The model may propose an action, but this module—not the model—decides whether
an action can execute. It provides three properties needed by autonomous
systems: explicit authority, idempotency, and bounded execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from typing import FrozenSet, Mapping


class ActionClass(str, Enum):
    READ = "read"
    WRITE = "write"
    EXTERNAL = "external"
    FINANCIAL = "financial"
    DESTRUCTIVE = "destructive"


class Decision(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True)
class Action:
    name: str
    action_class: ActionClass
    tenant_id: str
    actor_id: str
    idempotency_key: str
    requested_at: float = field(default_factory=time.time)
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionEnvelope:
    execution_id: str
    action: Action
    decision: Decision
    expires_at: float
    reason: str


class HardeningKernel:
    """Fail-closed policy boundary for model-proposed actions."""

    def __init__(
        self,
        *,
        approval_required: FrozenSet[ActionClass] | None = None,
        denied_actions: FrozenSet[str] | None = None,
        max_execution_seconds: int = 300,
    ) -> None:
        self.approval_required = approval_required or frozenset(
            {
                ActionClass.EXTERNAL,
                ActionClass.FINANCIAL,
                ActionClass.DESTRUCTIVE,
            }
        )
        self.denied_actions = denied_actions or frozenset()
        self.max_execution_seconds = max(1, max_execution_seconds)
        self._seen: set[str] = set()

    @staticmethod
    def execution_id(action: Action) -> str:
        material = "|".join(
            (
                action.tenant_id,
                action.actor_id,
                action.name,
                action.idempotency_key,
            )
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def evaluate(self, action: Action) -> ExecutionEnvelope:
        """Evaluate an action. Missing authority always fails closed."""
        if not action.tenant_id or not action.actor_id or not action.idempotency_key:
            return self._envelope(action, Decision.DENY, "missing_execution_identity")

        if action.name in self.denied_actions:
            return self._envelope(action, Decision.DENY, "action_denied_by_policy")

        execution_id = self.execution_id(action)
        if execution_id in self._seen:
            return self._envelope(action, Decision.DENY, "duplicate_execution")

        if action.action_class in self.approval_required:
            return self._envelope(action, Decision.REQUIRE_APPROVAL, "approval_required")

        self._seen.add(execution_id)
        return self._envelope(action, Decision.ALLOW, "policy_allow")

    def record_approved(self, envelope: ExecutionEnvelope) -> ExecutionEnvelope:
        """Commit an approved execution to the idempotency ledger."""
        if envelope.decision is not Decision.REQUIRE_APPROVAL:
            raise ValueError("only approval-gated executions can be approved")
        execution_id = envelope.execution_id
        if execution_id in self._seen:
            raise ValueError("duplicate_execution")
        self._seen.add(execution_id)
        return self._envelope(envelope.action, Decision.ALLOW, "human_approval")

    def _envelope(
        self, action: Action, decision: Decision, reason: str
    ) -> ExecutionEnvelope:
        return ExecutionEnvelope(
            execution_id=self.execution_id(action),
            action=action,
            decision=decision,
            expires_at=time.time() + self.max_execution_seconds,
            reason=reason,
        )
