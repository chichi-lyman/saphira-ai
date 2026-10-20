"""Deterministic tests for Saphira core safety and routing policies.

All providers are fakes; tests never call local or cloud model endpoints.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core.local_fallback import classify_task, route_with_fallback
from src.core.logic_validator import validate_specialist_output
from src.core.provider_router import RouteDecision
from src.core.worker_timeouts import WorkerTimeoutPolicy, should_abort_loop


class FakeRouter:
    def __init__(self, decisions: dict[str | None, RouteDecision]) -> None:
        self.decisions = decisions
        self.calls: list[dict[str, object]] = []

    def choose(
        self,
        *,
        prefer: str | None = None,
        require_capability: str = "chat",
        local_ok: bool = True,
    ) -> RouteDecision:
        self.calls.append(
            {
                "prefer": prefer,
                "require_capability": require_capability,
                "local_ok": local_ok,
            }
        )
        return self.decisions.get(
            prefer,
            RouteDecision(
                endpoint=None,
                reason="no configured endpoint",
                fallback_keys=[],
            ),
        )


def decision(*, key: str, is_local: bool) -> RouteDecision:
    endpoint = SimpleNamespace(key=key, is_local=is_local)
    return RouteDecision(endpoint=endpoint, reason=f"selected {key}", fallback_keys=[])


class TestTaskClassification:
    @pytest.mark.parametrize(
        ("prompt", "expected"),
        [
            ("Format this name", "light"),
            ("Please classify this request", "light"),
            ("Can you do deep research on this?", "heavy"),
            ("Review the codebase architecture", "heavy"),
            ("A" * 300, "unknown"),
        ],
    )
    def test_classifies_task_without_external_calls(self, prompt: str, expected: str) -> None:
        assert classify_task(prompt).complexity == expected


class TestLocalFallbackRouting:
    def test_light_task_prefers_configured_local_endpoint(self) -> None:
        router = FakeRouter(
            {
                "vllm_local": decision(key="vllm_local", is_local=True),
            }
        )

        result = route_with_fallback("Format this sentence", router=router)

        assert result.endpoint is not None
        assert result.endpoint.key == "vllm_local"
        assert "local slm preferred" in result.reason.lower()
        assert router.calls[0]["prefer"] == "vllm_local"

    def test_heavy_task_skips_local_preference(self) -> None:
        cloud = decision(key="openai", is_local=False)
        router = FakeRouter({None: cloud})

        result = route_with_fallback("Perform deep research on this topic", router=router)

        assert result.endpoint is not None
        assert result.endpoint.key == "openai"
        assert len(router.calls) == 1
        assert router.calls[0]["prefer"] is None

    def test_light_task_uses_general_route_when_no_local_endpoint_exists(self) -> None:
        cloud = decision(key="cloud", is_local=False)
        router = FakeRouter({None: cloud})

        result = route_with_fallback("Fix this typo", router=router)

        assert result.endpoint is not None
        assert result.endpoint.key == "cloud"
        assert router.calls[-1]["prefer"] is None


class TestWorkerTimeoutPolicy:
    def test_hop_limit_allows_steps_below_limit(self) -> None:
        policy = WorkerTimeoutPolicy(max_specialist_hops=10)

        assert should_abort_loop(0, policy) is False
        assert should_abort_loop(9, policy) is False

    def test_hop_limit_aborts_at_and_above_limit(self) -> None:
        policy = WorkerTimeoutPolicy(max_specialist_hops=10)

        assert should_abort_loop(10, policy) is True
        assert should_abort_loop(11, policy) is True

    def test_custom_hop_limit_is_respected(self) -> None:
        policy = WorkerTimeoutPolicy(max_specialist_hops=3)

        assert should_abort_loop(2, policy) is False
        assert should_abort_loop(3, policy) is True


class TestLogicValidator:
    def test_rejects_empty_output(self) -> None:
        verdict = validate_specialist_output(
            user_instruction="Answer the question",
            specialist_output="   ",
        )

        assert verdict.ok is False
        assert any("Empty output" in reason for reason in verdict.reasons)

    def test_rejects_too_short_output(self) -> None:
        verdict = validate_specialist_output(
            user_instruction="Answer the question",
            specialist_output="OK",
        )

        assert verdict.ok is False
        assert any("too short" in reason.lower() for reason in verdict.reasons)

    def test_flags_obvious_completion_contradiction(self) -> None:
        verdict = validate_specialist_output(
            user_instruction="Explain the result",
            specialist_output="This cannot be done, but it was successfully completed.",
        )

        assert verdict.ok is False
        assert any("contradiction" in reason.lower() for reason in verdict.reasons)

    def test_flags_missing_list_structure(self) -> None:
        verdict = validate_specialist_output(
            user_instruction="Please list the three required steps in detail",
            specialist_output="First do this, then do that, then finish.",
        )

        assert verdict.ok is False
        assert any("list markers" in reason.lower() for reason in verdict.reasons)

    def test_flags_high_loop_count_metadata(self) -> None:
        verdict = validate_specialist_output(
            user_instruction="Answer clearly",
            specialist_output="A sufficiently long and readable answer.",
            metadata={"loop_count": 10},
        )

        assert verdict.ok is False
        assert any("loop count" in reason.lower() for reason in verdict.reasons)

    def test_accepts_clean_structured_output(self) -> None:
        verdict = validate_specialist_output(
            user_instruction="List the required steps",
            specialist_output="1. Inspect the inputs.\n2. Validate the result.\n3. Record the outcome.",
        )

        assert verdict.ok is True
        assert verdict.reasons == []
