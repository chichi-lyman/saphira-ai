# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Basic unit tests for evolution engine, wake-word sensitivity bounds,
# and interruption RMS debouncing.

import pytest
from src.core.evolution_engine import SaphiraEvolutionCore


def test_evolution_core_initial_state():
    core = SaphiraEvolutionCore()
    state = core.query_runtime_state()
    assert state["engine_status"] == "STOPPED"
    assert state["metrics"]["exceptions_mitigated"] == 0
    assert "safe_params" in state


def test_param_store_bounds():
    core = SaphiraEvolutionCore()
    assert 0.1 <= core.get_param("wake_sensitivity") <= 1.0
    assert core.get_param("memory_top_k") >= 1


@pytest.mark.asyncio
async def test_fault_reporting_increments_counter():
    core = SaphiraEvolutionCore()
    await core.report_fault("test_subsystem", RuntimeError("simulated"))
    assert core.telemetry.exceptions_mitigated == 1
