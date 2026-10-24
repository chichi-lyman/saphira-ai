# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""Telemetry snapshot checks + smoke coverage for SaphiraModelRegistry endpoints."""

from __future__ import annotations

from src.core.model_registry import SaphiraModelRegistry
from src.core.operational_telemetry import OperationalTelemetry


def test_local_endpoints_registered():
    local = SaphiraModelRegistry.list_local_endpoints()
    assert "vllm_local" in local
    assert "ollama_local" in local
    assert all(e.is_local for e in local.values())


def test_cloud_endpoint_registered():
    ep = SaphiraModelRegistry.get_endpoint("gemini_primary")
    assert ep is not None
    assert ep.is_local is False
    assert ep.provider == "google"


def test_telemetry_reports_latency_cost_and_verification():
    telemetry = OperationalTelemetry()
    telemetry.record(
        operation_id="op-1",
        provider="provider-a",
        model_id="mock",
        task_id="task-1",
        started_at=100.0,
        latency_ms=100,
        success=True,
        verified=True,
        estimated_cost_usd=0.01,
    )
    telemetry.record(
        operation_id="op-2",
        provider="provider-a",
        model_id="mock",
        task_id="task-2",
        started_at=101.0,
        latency_ms=300,
        success=False,
        verified=False,
        estimated_cost_usd=0.03,
        error_category="timeout",
    )
    snapshot = telemetry.snapshot()
    assert snapshot["operations"] == 2
    assert snapshot["success_rate"] == 0.5
    assert snapshot["latency_ms_avg"] == 200
    assert snapshot["estimated_cost_usd_total"] == 0.04
    assert snapshot["verification_pass_rate"] == 0.5
