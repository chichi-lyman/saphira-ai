# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Offline tests for MATH + GSM8K harnesses.

import pytest

from src.evaluation import EvaluationRunner, get_registry
from src.evaluation.benchmarks.math_bench import _extract_final_answer, _normalize_answer
from src.evaluation.benchmarks.gsm8k import _extract_gsm8k_answer


def test_registry_has_math_benchmarks():
    reg = get_registry()
    assert "math" in reg.list_keys()
    assert "gsm8k" in reg.list_keys()
    m = reg.metadata("math")
    assert m["category"] == "math"
    assert "eval.math" in m["capability_keys"]
    g = reg.metadata("gsm8k")
    assert g["category"] == "math"
    assert "eval.gsm8k" in g["capability_keys"]


def test_extract_math_answer():
    assert _extract_final_answer("... #### 42") == "42"
    assert _normalize_answer("7.0") == "7"


def test_extract_gsm8k_answer():
    assert _extract_gsm8k_answer("... #### 72") == "72"
    assert _extract_gsm8k_answer("The answer is 10") == "10"


@pytest.mark.asyncio
async def test_math_builtin_runs():
    async def solver(prompt: str) -> str:
        if "2^{3}" in prompt or "2^3" in prompt: return "#### 17"
        if "x + 5 = 12" in prompt: return "#### 7"
        if "divisible by 3" in prompt: return "#### 6"
        if "area of a rectangle" in prompt: return "#### 40"
        if "remainder when 25" in prompt: return "#### 4"
        if "sin 90" in prompt: return "#### 1"
        if "2x - 4 = 10" in prompt: return "#### 7"
        return "#### 0"

    runner = EvaluationRunner(model_fn=solver, agent_name="test")
    result = await runner.run("math", limit=8, seed=42)
    assert result.benchmark == "math"
    assert result.n_total == 8
    assert result.overall_score >= 0.5
    assert result.metadata.get("metric") == "exact_match"


@pytest.mark.asyncio
async def test_gsm8k_builtin_runs():
    async def solver(prompt: str) -> str:
        if "Natalia sold clips" in prompt: return "#### 72"
        if "Weng earns" in prompt: return "#### 10"
        if "Betty is saving" in prompt: return "#### 5"
        if "Julie is reading" in prompt or "120-page" in prompt: return "#### 42"
        if "3-page letter" in prompt: return "#### 624"
        if "rose bushes" in prompt: return "#### 52"
        if "50 apples" in prompt: return "#### 20"
        if "boxes of pencils" in prompt: return "#### 19"
        return "#### 0"

    runner = EvaluationRunner(model_fn=solver, agent_name="test")
    result = await runner.run("gsm8k", limit=8, seed=42)
    assert result.benchmark == "gsm8k"
    assert result.n_total == 8
    assert result.overall_score >= 0.7
    assert result.metadata.get("metric") == "exact_match"


@pytest.mark.asyncio
async def test_math_wrong_answers_score_zero():
    async def bad(prompt: str) -> str:
        return "#### 99999"

    runner = EvaluationRunner(model_fn=bad, agent_name="test")
    result = await runner.run("math", limit=3, seed=0)
    assert result.overall_score == 0.0
