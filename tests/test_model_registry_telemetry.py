from src.core.model_registry import (
    Modality,
    ModelRegistry,
    ModelSpec,
    NoEligibleModelError,
    RoutingRequest,
)
from src.core.operational_telemetry import OperationalTelemetry


def test_registry_routes_to_lowest_cost_eligible_model():
    registry = ModelRegistry()
    registry.register(ModelSpec("provider-a", "expensive", enabled=True, cost_per_1k_input_tokens=0.02))
    registry.register(ModelSpec("provider-b", "cheap", enabled=True, cost_per_1k_input_tokens=0.001))
    decision = registry.route(RoutingRequest())
    assert decision.selected.key == "provider-b:cheap"
    assert len(decision.candidates) == 2


def test_registry_respects_provider_preference():
    registry = ModelRegistry()
    registry.register(ModelSpec("provider-a", "a", enabled=True, cost_per_1k_input_tokens=0.001))
    registry.register(ModelSpec("provider-b", "b", enabled=True, cost_per_1k_input_tokens=0.02))
    decision = registry.route(RoutingRequest(preferred_providers=("provider-b",)))
    assert decision.selected.provider == "provider-b"


def test_registry_filters_disabled_and_wrong_modality():
    registry = ModelRegistry()
    registry.register(ModelSpec("provider-a", "disabled", enabled=False))
    registry.register(
        ModelSpec("provider-b", "text-only", enabled=True, modalities=frozenset({Modality.TEXT}))
    )
    try:
        registry.route(RoutingRequest(required_modalities=frozenset({Modality.IMAGE})))
    except NoEligibleModelError:
        pass
    else:
        raise AssertionError("Expected no eligible model")


def test_registry_invokes_registered_adapter():
    registry = ModelRegistry()
    registry.register(ModelSpec("provider-a", "mock", enabled=True), invoker=lambda prompt: prompt.upper())
    decision = registry.route(RoutingRequest())
    assert registry.invoke(decision, prompt="hello") == "HELLO"


def test_telemetry_reports_latency_cost_and_verification():
    telemetry = OperationalTelemetry()
    telemetry.record(
        operation_id="op-1", provider="provider-a", model_id="mock", task_id="task-1",
        started_at=100.0, latency_ms=100, success=True, verified=True, estimated_cost_usd=0.01,
    )
    telemetry.record(
        operation_id="op-2", provider="provider-a", model_id="mock", task_id="task-2",
        started_at=101.0, latency_ms=300, success=False, verified=False, estimated_cost_usd=0.03,
        error_category="timeout",
    )
    snapshot = telemetry.snapshot()
    assert snapshot["operations"] == 2
    assert snapshot["success_rate"] == 0.5
    assert snapshot["latency_ms_avg"] == 200
    assert snapshot["estimated_cost_usd_total"] == 0.04
    assert snapshot["verification_pass_rate"] == 0.5
