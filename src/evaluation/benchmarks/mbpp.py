# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""MBPP — Mostly Basic Python Problems (Google Research).

Crowd-sourced Python programming tasks solvable by entry-level programmers.
Each item: natural-language description + reference code + 3 assert tests.
Primary metric: pass@1 (functional correctness under execution).

Offline-first micro-subset for CI; full set via HF `google-research-datasets/mbpp`
or local JSONL cache.

Owner agents: Scholar + Evaluator | Governance: Nova Reign | Memory: NovaAethrea
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

logger = logging.getLogger("Saphira.Evaluation.MBPP")

_BUILTIN: List[Dict[str, Any]] = [
    {"task_id": 1, "text": "Write a function to find the minimum cost of a path to reach (m, n) from (1, 1) for the given cost matrix with a cost of each cell.", "code": "def min_cost(cost, m, n):\n    R = [list(row) for row in cost]\n    for i in range(1, m + 1):\n        R[i][0] += R[i - 1][0]\n    for j in range(1, n + 1):\n        R[0][j] += R[0][j - 1]\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            R[i][j] += min(R[i - 1][j - 1], R[i - 1][j], R[i][j - 1])\n    return R[m][n]\n", "test_list": ["assert min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) == 8", "assert min_cost([[2, 1, 1], [1, 1, 1], [1, 1, 1]], 2, 2) == 5", "assert min_cost([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 2, 2) == 5"]},
    {"task_id": 2, "text": "Write a function to find the similar elements from the given two tuple lists.", "code": "def similar_elements(test_tup1, test_tup2):\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return res\n", "test_list": ["assert similar_elements((3, 4, 5, 6), (5, 7, 4, 10)) == (4, 5)", "assert similar_elements((1, 2, 3, 4), (5, 4, 3, 7)) == (3, 4)", "assert similar_elements((11, 12, 14, 13), (17, 15, 14, 13)) == (13, 14)"]},
    {"task_id": 3, "text": "Write a python function to identify non-prime numbers.", "code": "import math\ndef is_not_prime(n):\n    if n <= 1:\n        return True\n    for i in range(2, int(math.sqrt(n)) + 1):\n        if n % i == 0:\n            return True\n    return False\n", "test_list": ["assert is_not_prime(2) == False", "assert is_not_prime(10) == True", "assert is_not_prime(35) == True"]},
    {"task_id": 4, "text": "Write a function to find the largest integers from a given list of numbers using heap queue algorithm.", "code": "import heapq as hq\ndef heap_queue_largest(nums, n):\n    largest_nums = hq.nlargest(n, nums)\n    return largest_nums\n", "test_list": ["assert heap_queue_largest([25, 35, 22, 85, 14, 65, 75, 22, 58], 3) == [85, 75, 65]", "assert heap_queue_largest([25, 35, 22, 85, 14, 65, 75, 22, 58], 2) == [85, 75]", "assert heap_queue_largest([25, 35, 22, 85, 14, 65, 75, 22, 58], 5) == [85, 75, 65, 58, 35]"]},
    {"task_id": 5, "text": "Write a function to find the number of ways to fill a 3 x n wall with 2 x 1 tiles.", "code": "def count_ways(n):\n    A = [0] * (n + 1)\n    B = [0] * (n + 1)\n    A[0] = 1\n    A[1] = 0\n    B[0] = 0\n    B[1] = 1\n    for i in range(2, n + 1):\n        A[i] = A[i - 2] + 2 * B[i - 1]\n        B[i] = A[i - 1] + B[i - 2]\n    return A[n]\n", "test_list": ["assert count_ways(2) == 3", "assert count_ways(8) == 153", "assert count_ways(12) == 2131"]},
    {"task_id": 6, "text": "Write a python function to check whether the two numbers differ at one bit position only or not.", "code": "def differ_At_One_Bit_Pos(a, b):\n    x = a ^ b\n    return x and (not (x & (x - 1)))\n", "test_list": ["assert differ_At_One_Bit_Pos(13, 9) == True", "assert differ_At_One_Bit_Pos(15, 8) == False", "assert differ_At_One_Bit_Pos(2, 4) == False"]},
    {"task_id": 7, "text": "Write a function to find all words which are at least 4 characters long in a string by using regex.", "code": "import re\ndef find_char_long(text):\n    return re.findall(r\"\\b\\w{4,}\\b\", text)\n", "test_list": ["assert find_char_long('Please move back to stream') == ['Please', 'move', 'back', 'stream']", "assert find_char_long('Jing Eco and Tech') == ['Jing', 'Tech']", "assert find_char_long('Jhingai wulu road Zone 3') == ['Jhingai', 'wulu', 'road', 'Zone']"]},
    {"task_id": 8, "text": "Write a function to find squares of individual elements in a list using list comprehension / lambda / map.", "code": "def square_nums(nums):\n    return list(map(lambda x: x ** 2, nums))\n", "test_list": ["assert square_nums([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]", "assert square_nums([10, 20, 30]) == [100, 400, 900]", "assert square_nums([12, 15]) == [144, 225]"]},
]


@dataclass
class MBPPConfig:
    n_shots: int = 0
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None
    timeout_sec: float = 3.0
    execute: bool = True


def _extract_code(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"```(?:python)?\s*([\s\S]*?)```", text, re.I)
    if m:
        return m.group(1).strip()
    if "def " in text:
        return text[text.find("def "):].strip()
    return text.strip()


def _build_prompt(item: Dict[str, Any]) -> str:
    tests = "\n".join(item.get("test_list", [])[:3])
    return (
        f"You are an expert Python programmer. Here is your task:\n"
        f"{item['text']}\n\n"
        f"Your code should pass these tests:\n{tests}\n\n"
        f"[BEGIN]\n"
    )


def _safe_exec_mbpp(code: str, test_list: List[str], timeout: float) -> bool:
    if not code or not test_list:
        return False
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    program = code + "\n\n"
    for t in test_list:
        program += t + "\n"
    namespace: Dict[str, Any] = {}
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
            import math, re as re_mod, heapq
            namespace["math"] = math
            namespace["re"] = re_mod
            namespace["heapq"] = heapq
            namespace["hq"] = heapq
        except Exception:
            pass
        exec(compile(program, "<mbpp>", "exec"), {"__builtins__": safe_builtins}, namespace)
        return True
    except Exception:
        logger.debug("MBPP exec failed: %s", traceback.format_exc(limit=2))
        return False


class MBPPBenchmark:
    """Runnable MBPP harness (pass@1)."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, execute: bool = True, timeout_sec: float = 3.0, **kwargs: Any) -> None:
        self.config = MBPPConfig(n_shots=n_shots, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path, timeout_sec=timeout_sec, execute=execute)
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
                ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="test")
                for row in ds:
                    items.append({"task_id": row.get("task_id", 0), "text": row["text"], "code": row.get("code", ""), "test_list": list(row.get("test_list") or [])})
                logger.info("Loaded MBPP sanitized test (%d items)", len(items))
            except Exception as e:
                logger.debug("HF MBPP unavailable (%s); using builtin", e)
        if not items:
            items = list(_BUILTIN)
            logger.info("Using builtin MBPP micro-subset (%d items)", len(items))
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
            prompt = _build_prompt(item)
            try:
                raw = model_fn(prompt)
                if hasattr(raw, "__await__"):
                    raw = await raw  # type: ignore
                response = str(raw)
            except Exception as e:
                logger.warning("Model call failed on MBPP %s: %s", item.get("task_id"), e)
                response = ""
            code = _extract_code(response)
            passed = False
            if self.config.execute and code:
                passed = _safe_exec_mbpp(code, item.get("test_list") or [], self.config.timeout_sec)
            elif code and not self.config.execute:
                try:
                    ast.parse(code)
                    passed = True
                except SyntaxError:
                    passed = False
            if passed:
                correct += 1
            total += 1
            if record_details:
                details.append({"task_id": item.get("task_id"), "passed": passed, "completion_preview": code[:120]})
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": ["python_coding"], "per_subject": {"python_coding": correct / total if total else 0.0}, "details": details, "metadata": {"n_shots": self.config.n_shots, "seed": self.config.seed, "metric": "pass@1", "source": "builtin" if len(items) <= len(_BUILTIN) else "full_or_cache", "execute": self.config.execute}}
