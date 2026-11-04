# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""MMLU — Massive Multitask Language Understanding harness.

Original paper: Hendrycks et al., 2020 (arXiv:2009.03300)
57 subjects, 4-choice multiple choice, elementary → professional level.
"""

from __future__ import annotations

import logging
import random
import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

logger = logging.getLogger("Saphira.Evaluation.MMLU")

MMLU_SUBJECTS: List[str] = [
    "abstract_algebra", "anatomy", "astronomy", "business_ethics", "clinical_knowledge",
    "college_biology", "college_chemistry", "college_computer_science", "college_mathematics",
    "college_medicine", "college_physics", "computer_security", "conceptual_physics",
    "econometrics", "electrical_engineering", "elementary_mathematics", "formal_logic",
    "global_facts", "high_school_biology", "high_school_chemistry", "high_school_computer_science",
    "high_school_european_history", "high_school_geography", "high_school_government_and_politics",
    "high_school_macroeconomics", "high_school_mathematics", "high_school_microeconomics",
    "high_school_physics", "high_school_psychology", "high_school_statistics",
    "high_school_us_history", "high_school_world_history", "human_aging", "human_sexuality",
    "international_law", "jurisprudence", "logical_fallacies", "machine_learning", "management",
    "marketing", "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios",
    "nutrition", "philosophy", "prehistory", "professional_accounting", "professional_law",
    "professional_medicine", "professional_psychology", "public_relations", "security_studies",
    "sociology", "us_foreign_policy", "virology", "world_religions",
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
    {"subject": "anatomy", "question": "How many chambers does the human heart have?", "choices": ["2", "3", "4", "5"], "answer": 2},
    {"subject": "nutrition", "question": "Which vitamin is primarily obtained from sunlight exposure?", "choices": ["Vitamin A", "Vitamin C", "Vitamin D", "Vitamin K"], "answer": 2},
]


def _extract_choice(text: str) -> Optional[int]:
    """Map free-form model output to 0-based choice index (0=A … 3=D)."""
    if not text:
        return None
    text = text.strip().upper()
    m = re.search(r"\b([ABCD])\b", text)
    if m:
        return ord(m.group(1)) - ord("A")
    m = re.search(r"\b([1-4])\b", text)
    if m:
        return int(m.group(1)) - 1
    m = re.search(r"\b([0-3])\b", text)
    if m:
        return int(m.group(1))
    return None


def _format_single(item: Dict[str, Any], include_answer: bool) -> str:
    choices = item.get("choices") or []
    lines = [item["question"]]
    for i, c in enumerate(choices):
        lines.append(f"{chr(65 + i)}. {c}")
    if include_answer:
        ans = item.get("answer")
        if isinstance(ans, int) and 0 <= ans < len(choices):
            lines.append(f"Answer: {chr(65 + ans)}")
    return "\n".join(lines)


def _format_prompt(item: Dict[str, Any], fewshot: Sequence[Dict[str, Any]] = ()) -> str:
    parts: List[str] = []
    for ex in fewshot:
        parts.append(_format_single(ex, include_answer=True))
    parts.append(_format_single(item, include_answer=False))
    parts.append("Answer:")
    return "\n\n".join(parts)


class MMLUBenchmark:
    """Offline-friendly MMLU runner used by EvaluationRunner."""

    name = "mmlu"

    def __init__(
        self,
        config: Optional[MMLUConfig] = None,
        *,
        n_shots: int = 0,
        subjects: Optional[List[str]] = None,
        limit: Optional[int] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or MMLUConfig(
            n_shots=n_shots, subjects=subjects, limit=limit, seed=seed
        )

    def load_items(self) -> List[Dict[str, Any]]:
        items = list(_BUILTIN_SUBSET)
        if self.config.subjects:
            wanted = set(self.config.subjects)
            items = [i for i in items if i["subject"] in wanted]
        rng = random.Random(self.config.seed)
        rng.shuffle(items)
        if self.config.limit is not None:
            items = items[: self.config.limit]
        return items

    async def evaluate(
        self,
        model_fn: Callable[[str], Union[str, Awaitable[str]]],
        record_details: bool = False,
    ) -> Dict[str, Any]:
        items = self.load_items()
        correct = 0
        total = 0
        per_subj_total: Dict[str, int] = {}
        per_subj_correct: Dict[str, int] = {}
        details: List[Dict[str, Any]] = []
        fewshot: List[Dict[str, Any]] = []
        if self.config.n_shots > 0:
            pool = [i for i in _BUILTIN_SUBSET if i not in items] or list(_BUILTIN_SUBSET)
            fewshot = pool[: self.config.n_shots]

        for item in items:
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
                details.append({
                    "subject": subj,
                    "question": item["question"][:120],
                    "gold": gold,
                    "pred": pred,
                    "correct": is_correct,
                })
        per_subject = {
            s: (per_subj_correct.get(s, 0) / per_subj_total[s]) if per_subj_total[s] else 0.0
            for s in per_subj_total
        }
        return {
            "overall_score": correct / total if total else 0.0,
            "n_correct": correct,
            "n_total": total,
            "subjects": sorted(per_subj_total.keys()),
            "per_subject": per_subject,
            "details": details,
            "metadata": {
                "n_shots": self.config.n_shots,
                "seed": self.config.seed,
                "source": "builtin",
            },
        }
