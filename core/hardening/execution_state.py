"""Deterministic execution state machine for Saphira side effects.

The LLM never owns these transitions. Callers must present the current state,
and only explicit transitions are accepted. Unknown external outcomes enter
RECONCILIATION_REQUIRED instead of being blindly retried.
"""
from __future__ import annotations

from enum import Enum


class ExecutionState(str, Enum):
    PROPOSED = "proposed"
    VALIDATED = "validated"
    AUTHORIZED = "authorized"
    RESERVED = "reserved"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMMITTED = "committed"
    VALIDATION_FAILED = "validation_failed"
    AUTHORIZATION_DENIED = "authorization_denied"
    RESERVATION_FAILED = "reservation_failed"
    EXECUTION_FAILED = "execution_failed"
    VERIFICATION_FAILED = "verification_failed"
    ROLLED_BACK = "rolled_back"
    RECONCILIATION_REQUIRED = "reconciliation_required"


_ALLOWED: dict[ExecutionState, frozenset[ExecutionState]] = {
    ExecutionState.PROPOSED: frozenset({ExecutionState.VALIDATED, ExecutionState.VALIDATION_FAILED}),
    ExecutionState.VALIDATED: frozenset({ExecutionState.AUTHORIZED, ExecutionState.AUTHORIZATION_DENIED}),
    ExecutionState.AUTHORIZED: frozenset({ExecutionState.RESERVED}),
    ExecutionState.RESERVED: frozenset({ExecutionState.EXECUTING, ExecutionState.RESERVATION_FAILED}),
    ExecutionState.EXECUTING: frozenset({ExecutionState.VERIFYING, ExecutionState.EXECUTION_FAILED, ExecutionState.RECONCILIATION_REQUIRED}),
    ExecutionState.VERIFYING: frozenset({ExecutionState.COMMITTED, ExecutionState.VERIFICATION_FAILED, ExecutionState.RECONCILIATION_REQUIRED}),
    ExecutionState.VALIDATION_FAILED: frozenset({ExecutionState.ROLLED_BACK}),
    ExecutionState.AUTHORIZATION_DENIED: frozenset({ExecutionState.ROLLED_BACK}),
    ExecutionState.RESERVATION_FAILED: frozenset({ExecutionState.ROLLED_BACK}),
    ExecutionState.EXECUTION_FAILED: frozenset({ExecutionState.ROLLED_BACK}),
    ExecutionState.VERIFICATION_FAILED: frozenset({ExecutionState.ROLLED_BACK}),
    ExecutionState.RECONCILIATION_REQUIRED: frozenset({ExecutionState.VERIFYING, ExecutionState.ROLLED_BACK}),
    ExecutionState.COMMITTED: frozenset(),
    ExecutionState.ROLLED_BACK: frozenset(),
}


def transition(current: ExecutionState, target: ExecutionState) -> ExecutionState:
    """Return target only when the transition is explicitly permitted."""
    if target not in _ALLOWED[current]:
        raise ValueError(f"invalid_execution_transition:{current.value}->{target.value}")
    return target
