# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""MMLU — Massive Multitask Language Understanding harness.

Original paper: Hendrycks et al., 2020 (arXiv:2009.03300)
57 subjects, 4-choice multiple choice, elementary → professional level.

This module provides a clean, dependency-light interface that can:
  1. Use a local/cached subset for CI and agent self-tests (no network).
  2. Load the full HuggingFace dataset when `datasets` is available.
  3. Run 0-shot or 5-shot evaluations against any async/sync model callable.

Design notes for Nova Umbrella:
  - Owned primarily by Agent Scholar (knowledge synthesis) + Evaluator.
  - Results feed NovaAethrea memory and NovaReign capability scoring.
  - Never exposed as a user-facing agent name.
"""

from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

logger = logging.getLogger("Saphira.Evaluation.MMLU")

# Canonical 57 MMLU subjects (Hendrycks et al.)
MMLU_SUBJECTS: List[str] = [
    "abstract_algebra",
    "anatomy",
    "astronomy",
    "business_ethics",
    "clinical_knowledge",
    "college_biology",
    "college_chemistry",
    "college_computer_science",
    "college_mathematics",
    "college_medicine",
    "college_physics",
    "computer_security",
    "conceptual_physics",
    "econometrics",
    "electrical_engineering",
    "elementary_mathematics",
    "formal_logic",
    "global_facts",
    "high_school_biology",
    "high_school_chemistry",
    "high_school_computer_science",
    "high_school_european_history",
    "high_school_geography",
    "high_school_government_and_politics",
    "high_school_macroeconomics",
    "high_school_mathematics",
    "high_school_microeconomics",
    "high_school_physics",
    "high_school_psychology",
    "high_school_statistics",
    "high_school_us_history",
    "high_school_world_history",
    "human_aging",
    "human_sexuality",
    "international_law",
    "jurisprudence",
    "logical_fallacies",
    "machine_learning",
    "management",
    "marketing",
    "medical_genetics",
    "miscellaneous",
    "moral_disputes",
    "moral_scenarios",
    "nutrition",
    "philosophy",
    "prehistory",
    "professional_accounting",
    "professional_law",
    "professional_medicine",
    "professional_psychology",
    "public_relations",
    "security_studies",
    "sociology",
    "us_foreign_policy",
    "virology",
    "world_religions",
]


@dataclass
class MMLUConfig:
    n_shots: int = 0
    subjects: Optional[List[str]] = None
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None


_BUILTIN_SUBSET: List[Dict[str, Any]] = [
    {"subject": "astronomy", "question": "What is the approximate age of the universe according to current cosmological measurements?", "choices": ["4.5 billion years", "13.8 billion years", "100 million years", "1 trillion years"], "answer": 1},
    {"subject": "astronomy", "question": "Which planet is known for its prominent ring system?", "choices": ["Jupiter", "Mars", "Saturn", "Neptune"], "answer": 2},
    {"subject": "high_school_computer_science", "question": "What is the time complexity of binary search on a sorted array of n elements?", "choices": ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "answer": 1},
    {"subject": "high_school_computer_science", "question": "In Python, which of the following creates a dictionary?", "choices": ["[]", "()", "{}", "set()"], "answer": 2},
    {"subject": "college_mathematics", "question": "What is the derivative of sin(x) with respect to x?", "choices": ["cos(x)", "-sin(x)", "tan(x)", "-cos(x)"], "answer": 0},
    {"subject": "college_mathematics", "question": "What is the value of the integral of e^x dx?", "choices": ["e^x + C", "x e^x + C", "ln(x) + C", "1/x + C"], "answer": 0},
    {"subject": "formal_logic", "question": "Which of the following is a tautology?", "choices": ["P ∧ ¬P", "P ∨ ¬P", "P → ¬P", "¬(P ∨ Q)"], "answer": 1},
    {"subject": "world_religions", "question": "In Buddhism, what is the term for the cycle of birth, death, and rebirth?", "choices": ["Nirvana", "Karma", "Samsara", "Dharma"], "answer": 2},
    {"subject": "professional_law", "question": "In U.S. constitutional law, which amendment protects freedom of speech?", "choices": ["First Amendment", "Second Amendment", "Fourth Amendment", "Fifth Amendment"], "answer": 0},
    {"subject": "machine_learning", "question": "What does the acronym 'SVM' stand for in machine learning?", "choices": ["Support Vector Machine", "Supervised Vector Model", "Statistical Variance Method", "Stochastic Variable Mapping"], "answer": 0},
    {"subject": "anatomy", "question": "Which organ is primarily responsible for filtering blood and producing urine?", "choices": ["Liver", "Kidney", "Spleen", "Pancreas"], "answer": 1},
    {"subject": "philosophy", "question": "Who is the author of 'Critique of Pure Reason'?", "choices": ["Immanuel Kant", "David Hume", "John Locke", "René Descartes"], "answer": 0},
]


def _extract_choice(text: str) -> Optional[int]:
    if not text:
        return None
    text = text.strip().upper()
    m = re.search(r"\b([ABCD])\b", text)
    if m:
        return ord(m.group(1)) - ord("A")
    m = re.search(r"\b([0-3])\b", text)
    if m:
        return int(m.group(1))
    m = re.search(r"\b([1-4])\b", text)
    if m:
        return int(m.group(1)) - 1
    return None


def _format_prompt(item: Dict[str, Any], fewshot: Sequence[Dict[str, Any]] = ()) -> str:
    parts: List[str] = []
    for ex in fewshot:
        parts.append(_format_single(ex, include_answer=True))
    parts.append(_format_single(item, include_answer=False))
    parts.append("Answer:")
    return "\n\n".join(parts)


def _format_single(item: Dict[str, Any], include_answer: bool) -> str:
    q = item["question"]
    choices = item["choices"]
    lines = [f"Question: {q}"]
    for i, c in enumerate(choices):
        lines.append(f"{chr(65 + i)}. {c}")
    if include_answer:
        ans = item["answer"]
        lines.append(f"Answer: {chr(65 + ans)}")
    return "\n".join(lines)


class MMLUBenchmark:
    """Runnable MMLU evaluation harness."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, **kwargs: Any) -> None:
        self.config = MMLUConfig(n_shots=max(0, min(n_shots, 5)), subjects=subjects, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path)
        self._items: List[Dict[str, Any]] = []
        self._fewshot_pool: Dict[str, List[Dict[str, Any]]] = {}

    def _load_items(self) -> List[Dict[str, Any]]:
        if self._items:
            return self._items
        items: List[Dict[str, Any]] = []
        if self.config.cache_path:
            path = Path(self.config.cache_path)
            if path.exists():
                with path.open() as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            items.append(json.loads(line))
                logger.info("Loaded %d MMLU items from cache %s", len(items), path)
        if not items:
            try:
                from datasets import load_dataset  # type: ignore
                ds = load_dataset("cais/mmlu", "all", split="test")
                for row in ds:
                    items.append({"subject": row["subject"], "question": row["question"], "choices": list(row["choices"]), "answer": int(row["answer"])})
                logger.info("Loaded full MMLU test set via HuggingFace (%d items)", len(items))
            except Exception as e:
                logger.debug("HuggingFace MMLU unavailable (%s); using builtin subset", e)
        if not items or (self.config.use_builtin_subset and not items):
            items = list(_BUILTIN_SUBSET)
            logger.info("Using builtin MMLU micro-subset (%d items)", len(items))
        if self.config.subjects:
            wanted = set(self.config.subjects)
            items = [it for it in items if it["subject"] in wanted]
        rng = random.Random(self.config.seed)
        rng.shuffle(items)
        if self.config.limit is not None:
            items = items[: self.config.limit]
        self._items = items
        for it in _BUILTIN_SUBSET + items:
            subj = it["subject"]
            self._fewshot_pool.setdefault(subj, []).append(it)
        return self._items

    def _select_fewshot(self, subject: str, exclude: Dict[str, Any]) -> List[Dict[str, Any]]:
        pool = [it for it in self._fewshot_pool.get(subject, []) if it is not exclude]
        if len(pool) < self.config.n_shots:
            pool = [it for it in _BUILTIN_SUBSET if it is not exclude]
        rng = random.Random(self.config.seed + hash(subject) % 10_000)
        return rng.sample(pool, min(self.config.n_shots, len(pool)))

    async def evaluate(self, model_fn: Callable[..., Union[str, Awaitable[str]]], *, record_details: bool = True) -> Dict[str, Any]:
        items = self._load_items()
        if not items:
            return {"overall_score": 0.0, "n_correct": 0, "n_total": 0, "subjects": [], "per_subject": {}, "details": [], "metadata": {"error": "no items loaded"}}
        correct = 0
        total = 0
        per_subj_correct: Dict[str, int] = {}
        per_subj_total: Dict[str, int] = {}
        details: List[Dict[str, Any]] = []
        for item in items:
            fewshot = self._select_fewshot(item["subject"], item) if self.config.n_shots else []
            prompt = _format_prompt(item, fewshot)
            try:
                raw = model_fn(prompt)
                if hasattr(raw, "__await__"):
                    raw = await raw  # type: ignore
                response = str(raw)
            except Exception as e:
                logger.warning("Model call failed on MMLU item: %s", e)
                response = ""
            pred = _extract_choice(response)
            gold = int(item["answer"])
            is_correct = pred is not None and pred == gold
            if is_correct:
                correct += 1
            total += 1
            subj = item["subject"]
            per_subj_total[subj] = per_subj_total.get(subj, 0) + 1
            if is_correct:
                per_subj_correct[subj] = per_subj_correct.get(subj, 0) + 1
            if record_details:
                details.append({"subject": subj, "question": item["question"][:120], "gold": gold, "pred": pred, "correct": is_correct})
        per_subject = {s: (per_subj_correct.get(s, 0) / per_subj_total[s]) if per_subj_total[s] else 0.0 for s in per_subj_total}
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": sorted(per_subj_total.keys()), "per_subject": per_subject, "details": details, "metadata": {"n_shots": self.config.n_shots, "seed": self.config.seed, "source": "builtin" if len(items) <= len(_BUILTIN_SUBSET) else "full_or_cache"}}
