# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Offline tests for HumanEval + MBPP harnesses (builtin subsets).

import pytest

from src.evaluation import EvaluationRunner, get_registry
from src.evaluation.benchmarks.humaneval import HumanEvalBenchmark
from src.evaluation.benchmarks.mbpp import MBPPBenchmark


def test_registry_has_coding_benchmarks():
    reg = get_registry()
    assert "humaneval" in reg.list_keys()
    assert "mbpp" in reg.list_keys()
    he = reg.metadata("humaneval")
    assert he is not None
    assert he["category"] == "coding"
    assert "eval.humaneval" in he["capability_keys"]
    mb = reg.metadata("mbpp")
    assert mb["category"] == "coding"
    assert "coding.python" in mb["capability_keys"]


@pytest.mark.asyncio
async def test_humaneval_builtin_runs():
    async def canonical(prompt: str) -> str:
        if "has_close_elements" in prompt:
            return "    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n    return False\n"
        if "truncate_number" in prompt:
            return "    return number % 1.0\n"
        if "below_zero" in prompt:
            return "    balance = 0\n    for op in operations:\n        balance += op\n        if balance < 0:\n            return True\n    return False\n"
        if "mean_absolute_deviation" in prompt:
            return "    mean = sum(numbers) / len(numbers)\n    return sum(abs(x - mean) for x in numbers) / len(numbers)\n"
        if "intersperse" in prompt:
            return "    if not numbers:\n        return []\n    result = []\n    for n in numbers[:-1]:\n        result.append(n)\n        result.append(delimiter)\n    result.append(numbers[-1])\n    return result\n"
        return "    pass\n"

    runner = EvaluationRunner(model_fn=canonical, agent_name="test-coder")
    result = await runner.run("humaneval", limit=5, seed=42)
    assert result.benchmark == "humaneval"
    assert result.n_total == 5
    assert result.overall_score >= 0.5
    assert result.metadata.get("metric") == "pass@1"


@pytest.mark.asyncio
async def test_humaneval_bad_code_fails():
    async def bad(prompt: str) -> str:
        return "    raise RuntimeError('nope')\n"

    runner = EvaluationRunner(model_fn=bad, agent_name="test")
    result = await runner.run("humaneval", limit=3, seed=1)
    assert result.overall_score == 0.0


@pytest.mark.asyncio
async def test_mbpp_builtin_runs():
    async def canonical(prompt: str) -> str:
        if "similar elements" in prompt.lower() or "similar_elements" in prompt:
            return "def similar_elements(test_tup1, test_tup2):\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return res\n"
        if "non-prime" in prompt.lower() or "is_not_prime" in prompt:
            return "import math\ndef is_not_prime(n):\n    if n <= 1:\n        return True\n    for i in range(2, int(math.sqrt(n)) + 1):\n        if n % i == 0:\n            return True\n    return False\n"
        if "square" in prompt.lower():
            return "def square_nums(nums):\n    return list(map(lambda x: x ** 2, nums))\n"
        if "differ" in prompt.lower() and "bit" in prompt.lower():
            return "def differ_At_One_Bit_Pos(a, b):\n    x = a ^ b\n    return x and (not (x & (x - 1)))\n"
        if "find_char_long" in prompt or "at least 4 characters" in prompt.lower():
            return "import re\ndef find_char_long(text):\n    return re.findall(r\"\\b\\w{4,}\\b\", text)\n"
        return "def unknown():\n    pass\n"

    runner = EvaluationRunner(model_fn=canonical, agent_name="test-coder")
    result = await runner.run("mbpp", limit=8, seed=42)
    assert result.benchmark == "mbpp"
    assert result.n_total == 8
    assert result.overall_score >= 0.3
    assert result.metadata.get("metric") == "pass@1"


@pytest.mark.asyncio
async def test_mbpp_empty_fails():
    async def empty(prompt: str) -> str:
        return ""

    runner = EvaluationRunner(model_fn=empty, agent_name="test")
    result = await runner.run("mbpp", limit=3, seed=0)
    assert result.overall_score == 0.0
