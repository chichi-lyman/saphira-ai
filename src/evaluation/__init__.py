# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI — Standardized Evaluation Package

"""Standardized evaluation benchmarks for Saphira AI / Nova Umbrella.

Surfaces:
  - MMLU, GPQA (knowledge / graduate science)
  - HumanEval, MBPP (Python coding pass@1)
  - MATH, GSM8K, MGSM (mathematical / quantitative / multilingual reasoning)

Additional benchmarks register via BenchmarkRegistry.
"""

from .registry import BenchmarkRegistry, get_registry
from .runner import EvaluationRunner, EvaluationResult
from .benchmarks.mmlu import MMLUBenchmark, MMLUConfig
from .benchmarks.humaneval import HumanEvalBenchmark, HumanEvalConfig
from .benchmarks.mbpp import MBPPBenchmark, MBPPConfig
from .benchmarks.gpqa import GPQABenchmark, GPQAConfig
from .benchmarks.math_bench import MATHBenchmark, MATHConfig
from .benchmarks.gsm8k import GSM8KBenchmark, GSM8KConfig
from .benchmarks.mgsm import MGSMBenchmark, MGSMConfig

__all__ = [
    "BenchmarkRegistry", "get_registry",
    "EvaluationRunner", "EvaluationResult",
    "MMLUBenchmark", "MMLUConfig",
    "HumanEvalBenchmark", "HumanEvalConfig",
    "MBPPBenchmark", "MBPPConfig",
    "GPQABenchmark", "GPQAConfig",
    "MATHBenchmark", "MATHConfig",
    "GSM8KBenchmark", "GSM8KConfig",
    "MGSMBenchmark", "MGSMConfig",
]
