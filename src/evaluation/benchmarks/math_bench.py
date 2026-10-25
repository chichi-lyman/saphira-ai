# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""MATH — Competition mathematics (Hendrycks et al., 2021).

12,500 competition problems across algebra, counting & probability, geometry,
intermediate algebra, number theory, prealgebra, and precalculus.
Metric: exact match on the final answer (after step-by-step reasoning).

Offline-first micro-subset for CI. Full set via HF `hendrycks/competition_math`
or local JSONL cache.

Owner agents: Scholar + Evaluator | Governance: Nova Reign | Memory: NovaAethrea
Paper: arXiv:2103.03874
"""

from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

logger = logging.getLogger("Saphira.Evaluation.MATH")

MATH_SUBJECTS = ["Algebra", "Counting & Probability", "Geometry", "Intermediate Algebra", "Number Theory", "Prealgebra", "Precalculus"]

_BUILTIN: List[Dict[str, Any]] = [
    {"problem": "What is the value of $2^{3} + 3^{2}$?", "solution": "We compute $2^3 = 8$ and $3^2 = 9$, so $8 + 9 = 17$.\n#### 17", "answer": "17", "level": "Level 1", "type": "Algebra"},
    {"problem": "If $x + 5 = 12$, what is $x$?", "solution": "Subtract 5 from both sides: $x = 12 - 5 = 7$.\n#### 7", "answer": "7", "level": "Level 1", "type": "Algebra"},
    {"problem": "How many positive integers less than 20 are divisible by 3?", "solution": "The multiples of 3 less than 20 are 3,6,9,12,15,18 — six numbers.\n#### 6", "answer": "6", "level": "Level 1", "type": "Counting & Probability"},
    {"problem": "What is the area of a rectangle with length 8 and width 5?", "solution": "Area = length × width = 8 × 5 = 40.\n#### 40", "answer": "40", "level": "Level 1", "type": "Geometry"},
    {"problem": "Find the remainder when 25 is divided by 7.", "solution": "25 = 3 × 7 + 4, so remainder is 4.\n#### 4", "answer": "4", "level": "Level 1", "type": "Number Theory"},
    {"problem": "Simplify $\\frac{12}{18}$.", "solution": "Divide numerator and denominator by 6: $\\frac{2}{3}$.\n#### \\frac{2}{3}", "answer": "\\frac{2}{3}", "level": "Level 1", "type": "Prealgebra"},
    {"problem": "What is $\\sin 90^\\circ$?", "solution": "By definition, $\\sin 90^\\circ = 1$.\n#### 1", "answer": "1", "level": "Level 1", "type": "Precalculus"},
    {"problem": "Solve for $x$: $2x - 4 = 10$.", "solution": "Add 4: $2x = 14$. Divide by 2: $x = 7$.\n#### 7", "answer": "7", "level": "Level 1", "type": "Algebra"},
]


@dataclass
class MATHConfig:
    n_shots: int = 0
    subjects: Optional[List[str]] = None
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None


def _normalize_answer(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"^\$+|\$+$", "", s)
    s = s.replace(",", "").replace(" ", "").lower()
    if re.fullmatch(r"-?\d+\.0+", s):
        s = s.split(".")[0]
    return s


def _extract_final_answer(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"####\s*(.+?)(?:\n|$)", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?:the\s+)?answer\s*(?:is)?\s*[:\-]?\s*(.+?)(?:\n|$)", text, re.I)
    if m:
        return m.group(1).strip().rstrip(".")
    nums = re.findall(r"-?\d+\.?\d*", text)
    if nums:
        return nums[-1]
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def _format_prompt(item: Dict[str, Any], fewshot: Sequence[Dict[str, Any]] = ()) -> str:
    parts: List[str] = []
    for ex in fewshot:
        parts.append(f"Problem: {ex['problem']}\nSolution: {ex.get('solution', ex.get('answer', ''))}")
    parts.append(f"Problem: {item['problem']}\nSolution:")
    return "\n\n".join(parts)


class MATHBenchmark:
    """Runnable MATH competition math harness (exact-match final answer)."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, **kwargs: Any) -> None:
        self.config = MATHConfig(n_shots=max(0, min(n_shots, 5)), subjects=subjects, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path)
        self._items: List[Dict[str, Any]] = []
        self._fewshot_pool: List[Dict[str, Any]] = []

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
                            row = json.loads(line)
                            ans = row.get("answer") or _extract_final_answer(row.get("solution", ""))
                            items.append({"problem": row.get("problem") or row.get("question", ""), "solution": row.get("solution", ""), "answer": str(ans), "level": row.get("level", ""), "type": row.get("type") or row.get("subject", "")})
        if not items:
            try:
                from datasets import load_dataset  # type: ignore
                ds = load_dataset("hendrycks/competition_math", split="test")
                for row in ds:
                    sol = row.get("solution", "")
                    ans = _extract_final_answer(sol)
                    items.append({"problem": row["problem"], "solution": sol, "answer": ans, "level": row.get("level", ""), "type": row.get("type", "")})
                logger.info("Loaded MATH test via HuggingFace (%d items)", len(items))
            except Exception as e:
                logger.debug("HF MATH unavailable (%s); using builtin", e)
        if not items:
            items = list(_BUILTIN)
            logger.info("Using builtin MATH micro-subset (%d items)", len(items))
        if self.config.subjects:
            wanted = {s.lower() for s in self.config.subjects}
            items = [it for it in items if (it.get("type") or "").lower() in wanted]
        rng = random.Random(self.config.seed)
        rng.shuffle(items)
        if self.config.limit is not None:
            items = items[: self.config.limit]
        self._items = items
        self._fewshot_pool = list(_BUILTIN) + items
        return self._items

    def _select_fewshot(self, exclude: Dict[str, Any]) -> List[Dict[str, Any]]:
        pool = [it for it in self._fewshot_pool if it is not exclude]
        rng = random.Random(self.config.seed)
        return rng.sample(pool, min(self.config.n_shots, len(pool)))

    async def evaluate(self, model_fn: Callable[..., Union[str, Awaitable[str]]], *, record_details: bool = True) -> Dict[str, Any]:
        items = self._load_items()
        if not items:
            return {"overall_score": 0.0, "n_correct": 0, "n_total": 0, "subjects": [], "per_subject": {}, "details": [], "metadata": {"error": "no items"}}
        correct = 0
        total = 0
        per_subj_correct: Dict[str, int] = {}
        per_subj_total: Dict[str, int] = {}
        details: List[Dict[str, Any]] = []
        for item in items:
            fewshot = self._select_fewshot(item) if self.config.n_shots else []
            prompt = _format_prompt(item, fewshot)
            try:
                raw = model_fn(prompt)
                if hasattr(raw, "__await__"):
                    raw = await raw  # type: ignore
                response = str(raw)
            except Exception as e:
                logger.warning("Model call failed on MATH item: %s", e)
                response = ""
            pred = _normalize_answer(_extract_final_answer(response))
            gold = _normalize_answer(str(item.get("answer", "")))
            is_correct = bool(pred) and pred == gold
            if is_correct:
                correct += 1
            total += 1
            subj = item.get("type") or "unknown"
            per_subj_total[subj] = per_subj_total.get(subj, 0) + 1
            if is_correct:
                per_subj_correct[subj] = per_subj_correct.get(subj, 0) + 1
            if record_details:
                details.append({"type": subj, "gold": gold, "pred": pred, "correct": is_correct})
        per_subject = {s: (per_subj_correct.get(s, 0) / per_subj_total[s]) if per_subj_total[s] else 0.0 for s in per_subj_total}
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": sorted(per_subj_total.keys()), "per_subject": per_subject, "details": details, "metadata": {"n_shots": self.config.n_shots, "seed": self.config.seed, "metric": "exact_match", "source": "builtin" if len(items) <= len(_BUILTIN) else "full_or_cache"}}
