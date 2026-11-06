# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""GSM8K — Grade School Math 8K (Cobbe et al., 2021).

~8.5K grade-school math word problems requiring 2–8 steps of elementary
arithmetic. Metric: exact match on the final numeric answer (#### marker).

Offline-first micro-subset for CI. Full set via HF `openai/gsm8k` or JSONL cache.

Owner agents: Scholar + Evaluator | Governance: Nova Reign | Memory: NovaAethrea
Paper: arXiv:2110.14168
"""

from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

logger = logging.getLogger("Saphira.Evaluation.GSM8K")

_BUILTIN: List[Dict[str, Any]] = [
    {"question": "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?", "answer": "Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.\n#### 72"},
    {"question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?", "answer": "Weng earns 12/60 = <<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = <<0.2*50=10>>10.\n#### 10"},
    {"question": "Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?", "answer": "In the beginning, Betty has only 100 / 2 = <<100/2=50>>50.\nBetty's grandparents gave her 15 * 2 = <<15*2=30>>30.\nThis means, Betty needs 100 - 50 - 15 - 30 = <<100-50-15-30=5>>5 more.\n#### 5"},
    {"question": "Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages should she read tomorrow?", "answer": "Maila read 12 x 2 = <<12*2=24>>24 pages today.\nSo she was able to read a total of 12 + 24 = <<12+24=36>>36 pages since yesterday.\nThere are 120 - 36 = <<120-36=84>>84 pages left to be read.\nSince she wants to read half of the remaining pages tomorrow, then she should read 84/2 = <<84/2=42>>42 pages.\n#### 42"},
    {"question": "James writes a 3-page letter to 2 different friends twice a week. How many pages does he write a year?", "answer": "He writes each friend 3*2=<<3*2=6>>6 pages a week\nSo he writes 6*2=<<6*2=12>>12 pages every week\nThat means he writes 12*52=<<12*52=624>>624 pages a year\n#### 624"},
    {"question": "Mark has a garden with flowers. He planted 3 rose bushes and 2 tulip beds. Each rose bush has 12 roses and each tulip bed has 8 tulips. How many flowers does Mark have in total?", "answer": "Roses: 3 * 12 = <<3*12=36>>36\nTulips: 2 * 8 = <<2*8=16>>16\nTotal: 36 + 16 = <<36+16=52>>52\n#### 52"},
    {"question": "A store had 50 apples. They sold 12 in the morning and 18 in the afternoon. How many apples are left?", "answer": "Sold total: 12 + 18 = <<12+18=30>>30\nLeft: 50 - 30 = <<50-30=20>>20\n#### 20"},
    {"question": "Tom has 4 boxes of pencils. Each box contains 6 pencils. He gives 5 pencils to his friend. How many pencils does Tom have left?", "answer": "Total: 4 * 6 = <<4*6=24>>24\nLeft: 24 - 5 = <<24-5=19>>19\n#### 19"},
]


@dataclass
class GSM8KConfig:
    n_shots: int = 0
    subjects: Optional[List[str]] = None
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None


def _extract_gsm8k_answer(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")
    m = re.search(r"(?:the\s+)?answer\s*(?:is)?\s*[:\-]?\s*(-?[\d,]+(?:\.\d+)?)", text, re.I)
    if m:
        return m.group(1).replace(",", "")
    nums = re.findall(r"-?[\d,]+(?:\.\d+)?", text)
    if nums:
        return nums[-1].replace(",", "")
    return ""


def _gold_from_solution(answer_field: str) -> str:
    return _extract_gsm8k_answer(answer_field)


def _format_prompt(item: Dict[str, Any], fewshot: Sequence[Dict[str, Any]] = ()) -> str:
    parts: List[str] = []
    for ex in fewshot:
        parts.append(f"Question: {ex['question']}\nAnswer: {ex.get('answer', '')}")
    parts.append(f"Question: {item['question']}\nAnswer:")
    return "\n\n".join(parts)


class GSM8KBenchmark:
    """Runnable GSM8K harness (exact-match final numeric answer)."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, **kwargs: Any) -> None:
        self.config = GSM8KConfig(n_shots=max(0, min(n_shots, 8)), subjects=subjects, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path)
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
                            items.append({"question": row.get("question", ""), "answer": row.get("answer", "")})
        if not items:
            try:
                from datasets import load_dataset  # type: ignore
                ds = load_dataset("openai/gsm8k", "main", split="test")
                for row in ds:
                    items.append({"question": row["question"], "answer": row["answer"]})
                logger.info("Loaded GSM8K test via HuggingFace (%d items)", len(items))
            except Exception as e:
                logger.debug("HF GSM8K unavailable (%s); using builtin", e)
        if not items:
            items = list(_BUILTIN)
            logger.info("Using builtin GSM8K micro-subset (%d items)", len(items))
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
                logger.warning("Model call failed on GSM8K item: %s", e)
                response = ""
            pred = _extract_gsm8k_answer(response)
            gold = _gold_from_solution(item.get("answer", ""))
            is_correct = False
            if pred and gold:
                try:
                    is_correct = float(pred) == float(gold)
                except ValueError:
                    is_correct = pred.replace(" ", "") == gold.replace(" ", "")
            if is_correct:
                correct += 1
            total += 1
            if record_details:
                details.append({"gold": gold, "pred": pred, "correct": is_correct})
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": ["grade_school_math"], "per_subject": {"grade_school_math": correct / total if total else 0.0}, "details": details, "metadata": {"n_shots": self.config.n_shots, "seed": self.config.seed, "metric": "exact_match", "source": "builtin" if len(items) <= len(_BUILTIN) else "full_or_cache"}}
