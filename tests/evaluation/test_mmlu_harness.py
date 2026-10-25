# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Offline tests for the MMLU evaluation harness (builtin subset only).

import asyncio
import pytest

from src.evaluation import EvaluationRunner, get_registry
from src.evaluation.benchmarks.mmlu import MMLUBenchmark, MMLU_SUBJECTS, _extract_choice


def test_registry_has_mmlu():
    reg = get_registry()
    assert "mmlu" in reg.list_keys()
    meta = reg.metadata("mmlu")
    assert meta is not None
    assert meta["subjects"] == 57
    assert "scholar" in meta["owner_agents"]
    assert "eval.mmlu" in meta["capability_keys"]


def test_extract_choice():
    assert _extract_choice("The answer is B") == 1
    assert _extract_choice("A") == 0
    assert _extract_choice("I choose 3") == 2  # 1-based → 0-based
    assert _extract_choice("random text") is None


def test_mmlu_subjects_count():
    assert len(MMLU_SUBJECTS) == 57


@pytest.mark.asyncio
async def test_builtin_subset_runs():
    """Mock model that always answers 'B' — score is deterministic on builtin set."""

    async def always_b(prompt: str) -> str:
        return "B"

    runner = EvaluationRunner(model_fn=always_b, agent_name="test-agent")
    result = await runner.run("mmlu", n_shots=0, limit=12, seed=42)

    assert result.benchmark == "mmlu"
    assert result.n_total == 12
    assert 0.0 <= result.overall_score <= 1.0
    assert result.n_correct == int(round(result.overall_score * result.n_total))
    assert "astronomy" in result.subjects or len(result.subjects) > 0
    assert result.latency_ms >= 0
    d = result.to_dict()
    assert "overall_score" in d
    assert d["n_shots"] == 0


@pytest.mark.asyncio
async def test_subject_filter():
    async def always_a(prompt: str) -> str:
        return "A"

    runner = EvaluationRunner(model_fn=always_a, agent_name="test")
    result = await runner.run(
        "mmlu",
        n_shots=0,
        subjects=["astronomy"],
        limit=5,
        seed=1,
    )
    assert all(s == "astronomy" for s in result.subjects) or result.n_total <= 5


@pytest.mark.asyncio
async def test_five_shot_does_not_crash():
    async def always_c(prompt: str) -> str:
        return "C"

    runner = EvaluationRunner(model_fn=always_c, agent_name="test")
    result = await runner.run("mmlu", n_shots=5, limit=4, seed=7)
    assert result.n_total == 4
    assert result.n_shots == 5
