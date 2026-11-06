# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""HumanEval — Python code generation benchmark (OpenAI, 2021).

164 handwritten problems: function signature + docstring + unit tests.
Primary metric: pass@1 (functional correctness under execution).

Offline-first: ships a curated micro-subset for CI. Full set loads from
HuggingFace `openai_humaneval` or a local JSONL cache when available.

Owner agents: Scholar (synthesis) + Evaluator (execution / scoring)
Governed by: Nova Reign | Memory: NovaAethrea | Execution: Agent Zero
"""

from __future__ import annotations

import ast
import json
import logging
import random
import re
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

logger = logging.getLogger("Saphira.Evaluation.HumanEval")

_BUILTIN: List[Dict[str, Any]] = [
    {"task_id": "HumanEval/0", "prompt": "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    \"\"\"\n", "canonical_solution": "    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n    return False\n", "test": "def check(candidate):\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False\n    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True\n    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 1.0) == True\n    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 0.5) == False\n\n", "entry_point": "has_close_elements"},
    {"task_id": "HumanEval/2", "prompt": "def truncate_number(number: float) -> float:\n    \"\"\" Given a positive floating point number, it can be decomposed into\n    an integer part (largest integer smaller than given number) and decimals\n    (leftover part always smaller than 1).\n    Return the decimal part of the number.\n    >>> truncate_number(3.5)\n    0.5\n    \"\"\"\n", "canonical_solution": "    return number % 1.0\n", "test": "def check(candidate):\n    assert candidate(3.5) == 0.5\n    assert abs(candidate(1.33) - 0.33) < 1e-6\n    assert abs(candidate(123.456) - 0.456) < 1e-6\n\n", "entry_point": "truncate_number"},
    {"task_id": "HumanEval/3", "prompt": "from typing import List\n\ndef below_zero(operations: List[int]) -> bool:\n    \"\"\" You're given a list of deposit and withdrawal operations on a bank account that starts with\n    zero balance. Your task is to detect if at any point the balance of account falls below zero, and\n    at that point function should return True. Otherwise it should return False.\n    >>> below_zero([1, 2, 3])\n    False\n    >>> below_zero([1, 2, -4, 5])\n    True\n    \"\"\"\n", "canonical_solution": "    balance = 0\n    for op in operations:\n        balance += op\n        if balance < 0:\n            return True\n    return False\n", "test": "def check(candidate):\n    assert candidate([]) == False\n    assert candidate([1, 2, -3, 1, 2, -3]) == False\n    assert candidate([1, 2, -4, 5]) == True\n    assert candidate([1, -1, 2, -2, 5, -5, 4, -4]) == False\n    assert candidate([1, -1, 2, -2, 5, -5, 4, -5]) == True\n    assert candidate([1, -2, 2, -2, 5, -5, 4, -4]) == True\n\n", "entry_point": "below_zero"},
    {"task_id": "HumanEval/4", "prompt": "from typing import List\n\ndef mean_absolute_deviation(numbers: List[float]) -> float:\n    \"\"\" For a given list of input numbers, calculate Mean Absolute Deviation\n    around the mean of this dataset.\n    Mean Absolute Deviation is the average absolute difference between each\n    element and a centerpoint (mean in this case):\n    MAD = average | x - x_mean |\n    >>> mean_absolute_deviation([1.0, 2.0, 3.0, 4.0])\n    1.0\n    \"\"\"\n", "canonical_solution": "    mean = sum(numbers) / len(numbers)\n    return sum(abs(x - mean) for x in numbers) / len(numbers)\n", "test": "def check(candidate):\n    assert abs(candidate([1.0, 2.0, 3.0]) - 2.0/3.0) < 1e-6\n    assert abs(candidate([1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-6\n    assert abs(candidate([1.0, 2.0, 3.0, 4.0, 5.0]) - 6.0/5.0) < 1e-6\n\n", "entry_point": "mean_absolute_deviation"},
    {"task_id": "HumanEval/5", "prompt": "from typing import List\n\ndef intersperse(numbers: List[int], delimiter: int) -> List[int]:\n    \"\"\" Insert a number 'delimiter' between every two consecutive elements of input list `numbers'\n    >>> intersperse([], 4)\n    []\n    >>> intersperse([1, 2, 3], 4)\n    [1, 4, 2, 4, 3]\n    \"\"\"\n", "canonical_solution": "    if not numbers:\n        return []\n    result = []\n    for n in numbers[:-1]:\n        result.append(n)\n        result.append(delimiter)\n    result.append(numbers[-1])\n    return result\n", "test": "def check(candidate):\n    assert candidate([], 7) == []\n    assert candidate([5, 6, 3, 2], 8) == [5, 8, 6, 8, 3, 8, 2]\n    assert candidate([2, 2, 2], 2) == [2, 2, 2, 2, 2]\n\n", "entry_point": "intersperse"},
]


@dataclass
class HumanEvalConfig:
    n_shots: int = 0
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None
    timeout_sec: float = 3.0
    execute: bool = True


def _extract_code(text: str, entry_point: str) -> str:
    if not text:
        return ""
    m = re.search(r"```(?:python)?\s*([\s\S]*?)```", text, re.I)
    if m:
        text = m.group(1).strip()
    if f"def {entry_point}" in text:
        idx = text.find(f"def {entry_point}")
        text = text[idx:]
    return text.strip()


def _safe_exec_check(prompt: str, completion: str, test: str, entry_point: str, timeout: float) -> bool:
    program = prompt
    if not completion.lstrip().startswith("def "):
        body = completion
        if not body.startswith(" ") and not body.startswith("\t"):
            body = "\n".join("    " + line if line.strip() else line for line in body.splitlines())
        program = prompt.rstrip() + "\n" + body + "\n"
    else:
        program = completion + "\n"
    program += "\n" + test + f"\ncheck({entry_point})\n"
    try:
        ast.parse(program)
    except SyntaxError:
        return False
    namespace: Dict[str, Any] = {"__name__": "__main__"}
    try:
        safe_builtins = {
            "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
            "enumerate": enumerate, "float": float, "int": int, "len": len,
            "list": list, "max": max, "min": min, "range": range, "reversed": reversed,
            "round": round, "set": set, "sorted": sorted, "str": str, "sum": sum,
            "tuple": tuple, "zip": zip, "print": lambda *a, **k: None,
            "True": True, "False": False, "None": None,
            "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
            "IndexError": IndexError, "KeyError": KeyError, "ZeroDivisionError": ZeroDivisionError,
            "__import__": __import__,
        }
        try:
            import typing
            namespace["List"] = typing.List
            namespace["Dict"] = typing.Dict
            namespace["Optional"] = typing.Optional
            namespace["Tuple"] = typing.Tuple
            namespace["Any"] = typing.Any
            namespace["typing"] = typing
        except Exception:
            pass
        exec(compile(program, "<humaneval>", "exec"), {"__builtins__": safe_builtins}, namespace)
        return True
    except Exception:
        logger.debug("HumanEval exec failed: %s", traceback.format_exc(limit=2))
        return False


class HumanEvalBenchmark:
    """Runnable HumanEval harness (pass@1, zero-shot by default)."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, execute: bool = True, timeout_sec: float = 3.0, **kwargs: Any) -> None:
        self.config = HumanEvalConfig(n_shots=0, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path, timeout_sec=timeout_sec, execute=execute)
        self._items: List[Dict[str, Any]] = []

    def _load_items(self) -> List[Dict[str, Any]]:
        if self._items:
            return self._items
        items: List[Dict[str, Any]] = []
        if self.config.cache_path:
            path = Path(self.config.cache_path)
            if path.exists():
                with path.open() as f:
                    for line in f:
                        if line.strip():
                            items.append(json.loads(line))
        if not items:
            try:
                from datasets import load_dataset  # type: ignore
                ds = load_dataset("openai_humaneval", split="test")
                for row in ds:
                    items.append({"task_id": row["task_id"], "prompt": row["prompt"], "canonical_solution": row.get("canonical_solution", ""), "test": row["test"], "entry_point": row["entry_point"]})
                logger.info("Loaded full HumanEval (%d items)", len(items))
            except Exception as e:
                logger.debug("HF HumanEval unavailable (%s); using builtin", e)
        if not items:
            items = list(_BUILTIN)
            logger.info("Using builtin HumanEval micro-subset (%d items)", len(items))
        rng = random.Random(self.config.seed)
        rng.shuffle(items)
        if self.config.limit is not None:
            items = items[: self.config.limit]
        self._items = items
        return self._items

    async def evaluate(self, model_fn: Callable[..., Union[str, Awaitable[str]]], *, record_details: bool = True) -> Dict[str, Any]:
        items = self._load_items()
        if not items:
            return {"overall_score": 0.0, "n_correct": 0, "n_total": 0, "subjects": [], "per_subject": {}, "details": [], "metadata": {"error": "no items"}}
        correct = 0
        total = 0
        details: List[Dict[str, Any]] = []
        for item in items:
            prompt = item["prompt"]
            try:
                raw = model_fn(prompt)
                if hasattr(raw, "__await__"):
                    raw = await raw  # type: ignore
                response = str(raw)
            except Exception as e:
                logger.warning("Model call failed on %s: %s", item["task_id"], e)
                response = ""
            completion = _extract_code(response, item["entry_point"])
            passed = False
            if self.config.execute and completion:
                passed = _safe_exec_check(prompt, completion, item["test"], item["entry_point"], self.config.timeout_sec)
            elif completion and not self.config.execute:
                try:
                    ast.parse(prompt + completion)
                    passed = True
                except SyntaxError:
                    passed = False
            if passed:
                correct += 1
            total += 1
            if record_details:
                details.append({"task_id": item["task_id"], "entry_point": item["entry_point"], "passed": passed, "completion_preview": completion[:120]})
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": ["python_coding"], "per_subject": {"python_coding": correct / total if total else 0.0}, "details": details, "metadata": {"n_shots": 0, "seed": self.config.seed, "metric": "pass@1", "source": "builtin" if len(items) <= len(_BUILTIN) else "full_or_cache", "execute": self.config.execute}}
