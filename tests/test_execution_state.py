import pytest

from core.hardening.execution_state import ExecutionState, transition


def test_happy_path_is_explicit():
    state = ExecutionState.PROPOSED
    for target in (
        ExecutionState.VALIDATED,
        ExecutionState.AUTHORIZED,
        ExecutionState.RESERVED,
        ExecutionState.EXECUTING,
        ExecutionState.VERIFYING,
        ExecutionState.COMMITTED,
    ):
        state = transition(state, target)
    assert state is ExecutionState.COMMITTED


def test_unknown_outcome_requires_reconciliation():
    assert transition(
        ExecutionState.EXECUTING,
        ExecutionState.RECONCILIATION_REQUIRED,
    ) is ExecutionState.RECONCILIATION_REQUIRED


def test_cannot_skip_authorization():
    with pytest.raises(ValueError):
        transition(ExecutionState.VALIDATED, ExecutionState.EXECUTING)


def test_committed_is_terminal():
    with pytest.raises(ValueError):
        transition(ExecutionState.COMMITTED, ExecutionState.EXECUTING)


def test_failed_validation_can_only_roll_back():
    with pytest.raises(ValueError):
        transition(ExecutionState.VALIDATION_FAILED, ExecutionState.EXECUTING)
    assert transition(
        ExecutionState.VALIDATION_FAILED,
        ExecutionState.ROLLED_BACK,
    ) is ExecutionState.ROLLED_BACK
