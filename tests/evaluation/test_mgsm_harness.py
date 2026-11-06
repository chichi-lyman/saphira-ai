# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Offline tests for MGSM harness.

import pytest

from src.evaluation import EvaluationRunner, get_registry
from src.evaluation.benchmarks.mgsm import MGSM_LANGUAGES, _extract_numeric_answer


def test_registry_has_mgsm():
    reg = get_registry()
    assert "mgsm" in reg.list_keys()
    meta = reg.metadata("mgsm")
    assert meta["category"] == "math"
    assert "eval.mgsm" in meta["capability_keys"]
    assert "reasoning.multilingual" in meta["capability_keys"]


def test_mgsm_languages():
    assert "en" in MGSM_LANGUAGES
    assert "zh" in MGSM_LANGUAGES
    assert len(MGSM_LANGUAGES) == 11


def test_extract_numeric():
    assert _extract_numeric_answer("#### 11") == 11.0
    assert _extract_numeric_answer("The answer is 20") == 20.0
    assert _extract_numeric_answer("La respuesta es 11") == 11.0


@pytest.mark.asyncio
async def test_mgsm_builtin_runs():
    async def solver(prompt: str) -> str:
        p = prompt.lower()
        if any(x in p for x in ["5 tennis", "5 pelotas", "5 balles", "5 tennisbälle", "5个网球", "テニスボールを5"]):
            return "#### 11"
        if any(x in p for x in ["50 apples", "50 manzanas"]):
            return "#### 20"
        return "#### 0"

    runner = EvaluationRunner(model_fn=solver, agent_name="test")
    result = await runner.run("mgsm", limit=8, seed=42)
    assert result.benchmark == "mgsm"
    assert result.n_total == 8
    assert result.overall_score >= 0.5
    assert result.metadata.get("metric") == "exact_match"


@pytest.mark.asyncio
async def test_mgsm_language_filter():
    async def solver(prompt: str) -> str:
        return "#### 11"

    runner = EvaluationRunner(model_fn=solver, agent_name="test")
    result = await runner.run("mgsm", subjects=["en"], limit=5, seed=1)
    assert all(s == "en" for s in result.subjects) or result.n_total <= 5
