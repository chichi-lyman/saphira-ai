# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""Benchmark registry — maps capability keys to concrete evaluation harnesses.

Owned by: Agent Scholar (knowledge synthesis) + Evaluator (QA/verification)
Governed by: Nova Reign
Routed through: Capability Registry / NovaReign DAG
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type
import logging

logger = logging.getLogger("Saphira.Evaluation.Registry")


class BenchmarkRegistry:
    """Singleton-style registry of standardized evaluation benchmarks."""

    _instance: Optional["BenchmarkRegistry"] = None

    def __init__(self) -> None:
        self._benchmarks: Dict[str, Type] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def instance(cls) -> "BenchmarkRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._register_defaults()
        return cls._instance

    def register(self, key: str, benchmark_cls: Type, *, name: str, description: str, subjects: int = 0, category: str = "knowledge", owner_agents: Optional[list[str]] = None, capability_keys: Optional[list[str]] = None) -> None:
        self._benchmarks[key] = benchmark_cls
        self._metadata[key] = {"name": name, "description": description, "subjects": subjects, "category": category, "owner_agents": owner_agents or ["scholar", "evaluator"], "capability_keys": capability_keys or [f"eval.{key}"]}
        logger.info("Registered benchmark %s (%s)", key, name)

    def get(self, key: str) -> Optional[Type]:
        return self._benchmarks.get(key)

    def metadata(self, key: str) -> Optional[Dict[str, Any]]:
        return self._metadata.get(key)

    def list_keys(self) -> list[str]:
        return sorted(self._benchmarks.keys())

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return {k: dict(v) for k, v in self._metadata.items()}

    def _register_defaults(self) -> None:
        from .benchmarks.mmlu import MMLUBenchmark
        from .benchmarks.humaneval import HumanEvalBenchmark
        from .benchmarks.mbpp import MBPPBenchmark
        from .benchmarks.gpqa import GPQABenchmark
        from .benchmarks.math_bench import MATHBenchmark
        from .benchmarks.gsm8k import GSM8KBenchmark
        from .benchmarks.mgsm import MGSMBenchmark

        self.register("mmlu", MMLUBenchmark, name="MMLU (Massive Multitask Language Understanding)", description="Tests broad academic, factual, and cross-domain reasoning across 57 subjects.", subjects=57, category="knowledge", owner_agents=["scholar", "evaluator", "nova_aethrea"], capability_keys=["eval.mmlu", "eval.mmlu.0shot", "eval.mmlu.5shot", "knowledge.academic", "reasoning.multitask"])
        self.register("humaneval", HumanEvalBenchmark, name="HumanEval (Python Coding)", description="164 handwritten Python problems; zero-shot pass@1 code generation (OpenAI, 2021).", subjects=164, category="coding", owner_agents=["scholar", "evaluator", "agent_zero", "nova_aethrea"], capability_keys=["eval.humaneval", "eval.humaneval.pass_at_1", "coding.python", "coding.zero_shot", "reasoning.code_generation"])
        self.register("mbpp", MBPPBenchmark, name="MBPP (Mostly Basic Python Problems)", description="Crowd-sourced Python tasks; pass@1 functional correctness (Google Research).", subjects=974, category="coding", owner_agents=["scholar", "evaluator", "agent_zero", "nova_aethrea"], capability_keys=["eval.mbpp", "eval.mbpp.pass_at_1", "coding.python", "coding.basic", "reasoning.code_generation"])
        self.register("gpqa", GPQABenchmark, name="GPQA (Graduate-Level Google-Proof Q&A)", description="Graduate-level MCQ in biology, chemistry, physics; Google-proof (Rein et al., 2023).", subjects=448, category="reasoning", owner_agents=["scholar", "evaluator", "nova_aethrea"], capability_keys=["eval.gpqa", "eval.gpqa.diamond", "reasoning.graduate", "reasoning.science", "knowledge.biology", "knowledge.chemistry", "knowledge.physics"])
        self.register("math", MATHBenchmark, name="MATH (Competition Mathematics)", description="Competition mathematics; step-by-step quantitative reasoning via exact-match final answer (Hendrycks et al., 2021).", subjects=12500, category="math", owner_agents=["scholar", "evaluator", "nova_aethrea"], capability_keys=["eval.math", "eval.math.exact_match", "reasoning.mathematical", "reasoning.quantitative", "knowledge.competition_math"])
        self.register("gsm8k", GSM8KBenchmark, name="GSM8K (Grade School Math 8K)", description="Grade-school math word problems; multi-step arithmetic exact-match (Cobbe et al., 2021).", subjects=8500, category="math", owner_agents=["scholar", "evaluator", "nova_aethrea"], capability_keys=["eval.gsm8k", "eval.gsm8k.exact_match", "reasoning.mathematical", "reasoning.quantitative", "knowledge.grade_school_math"])
        self.register("mgsm", MGSMBenchmark, name="MGSM (Multilingual Grade School Math)", description="250 grade-school math word problems in 10 typologically diverse languages (+ English); exact-match numeric answer (Shi et al., 2022).", subjects=250, category="math", owner_agents=["scholar", "evaluator", "nova_aethrea"], capability_keys=["eval.mgsm", "eval.mgsm.exact_match", "reasoning.mathematical", "reasoning.multilingual", "knowledge.grade_school_math"])


def get_registry() -> BenchmarkRegistry:
    return BenchmarkRegistry.instance()
