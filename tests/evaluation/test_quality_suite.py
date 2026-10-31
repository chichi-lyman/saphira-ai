import pytest

from src.evaluation.quality_suite import QUALITY_CASES, run_quality_suite


@pytest.mark.asyncio
async def test_quality_suite_runs_all_dimensions_and_aggregates():
    async def model_fn(prompt: str) -> str:
        return "I will answer carefully and state uncertainty when needed."

    def grader_fn(case, response):
        return {"score": 1.0, "passed": True, "notes": case.evaluation_focus}

    report = await run_quality_suite(model_fn, grader_fn)
    assert report["case_count"] == len(QUALITY_CASES)
    assert report["pass_count"] == len(QUALITY_CASES)
    assert report["grading_mode"] == "external_grader_required"
    assert "adversarial_robustness" in report["category_summary"]


@pytest.mark.asyncio
async def test_quality_suite_rejects_invalid_grader_scores():
    async def model_fn(prompt: str) -> str:
        return "response"

    def grader_fn(case, response):
        return {"score": 1.5, "passed": True}

    with pytest.raises(ValueError):
        await run_quality_suite(model_fn, grader_fn)
