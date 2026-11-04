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


def _extract_choice(text: str) -> Optional[int]:
    """Map free-form model output to 0-based choice index (0=A … 3=D).

    Prefer letter forms, then 1-based digits (1–4), then 0-based (0–3).
    """
    if not text:
        return None
    text = text.strip().upper()
    m = re.search(r"\b([ABCD])\b", text)
    if m:
        return ord(m.group(1)) - ord("A")
    # Prefer 1-based human phrasing ("I choose 3" → index 2)
    m = re.search(r"\b([1-4])\b", text)
    if m:
        return int(m.group(1)) - 1
    m = re.search(r"\b([0-3])\b", text)
    if m:
        return int(m.group(1))
    return None
