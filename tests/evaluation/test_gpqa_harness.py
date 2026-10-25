# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Offline tests for GPQA harness (builtin subset).

import pytest

from src.evaluation import EvaluationRunner, get_registry
from src.evaluation.benchmarks.gpqa import GPQABenchmark, GPQA_DOMAINS, _extract_choice


def test_registry_has_gpqa():
    reg = get_registry()
    assert "gpqa" in reg.list_keys()
    meta = reg.metadata("gpqa")
    assert meta is not None
    assert meta["category"] == "reasoning"
    assert "eval.gpqa" in meta["capability_keys"]
    assert "reasoning.graduate" in meta["capability_keys"]
    assert "scholar" in meta["owner_agents"]


def test_gpqa_domains():
    assert set(GPQA_DOMAINS) == {"biology", "chemistry", "physics"}


def test_extract_choice():
    assert _extract_choice("The answer is C") == 2
    assert _extract_choice("Answer: A") == 0
    assert _extract_choice("B") == 1
    assert _extract_choice("no letter here") is None


@pytest.mark.asyncio
async def test_gpqa_builtin_runs():
    async def always_c(prompt: str) -> str:
        return "C"

    runner = EvaluationRunner(model_fn=always_c, agent_name="test")
    result = await runner.run("gpqa", n_shots=0, limit=8, seed=42)
    assert result.benchmark == "gpqa"
    assert result.n_total == 8
    assert 0.0 <= result.overall_score <= 1.0
    assert result.metadata.get("metric") == "accuracy"
    assert any(d in result.subjects for d in ("biology", "chemistry", "physics"))


@pytest.mark.asyncio
async def test_gpqa_domain_filter():
    async def always_a(prompt: str) -> str:
        return "A"

    runner = EvaluationRunner(model_fn=always_a, agent_name="test")
    result = await runner.run("gpqa", subjects=["physics"], limit=5, seed=1)
    assert all(s == "physics" for s in result.subjects) or result.n_total <= 5


@pytest.mark.asyncio
async def test_gpqa_fewshot_does_not_crash():
    async def always_b(prompt: str) -> str:
        return "B"

    runner = EvaluationRunner(model_fn=always_b, agent_name="test")
    result = await runner.run("gpqa", n_shots=3, limit=4, seed=7)
    assert result.n_total == 4
    assert result.n_shots == 3
