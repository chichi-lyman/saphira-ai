# Patch note — Standardized Evaluation (MMLU) integration

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

This file documents the addition of the MMLU standardized evaluation surface
to the existing Benchmark Excellence Matrix (`docs/SAPHIRA_BENCHMARK_EXCELLENCE.md`).

## What was added

1. **New package** `src/evaluation/` with:
   - `BenchmarkRegistry` (capability-keyed)
   - `EvaluationRunner` / `EvaluationResult`
   - `MMLUBenchmark` (0-shot / 5-shot, offline-first builtin subset + optional full HF load)

2. **Skill** `skills/standardized-evaluation-benchmarks/SKILL.md`

3. **Canonical doc** `docs/STANDARDIZED_EVALUATION_BENCHMARKS.md`

4. **Tests** `tests/evaluation/test_mmlu_harness.py` (offline)

5. **CLI** `scripts/run_mmlu_eval.py`

## Excellence matrix linkage

The existing Zero-Shot Reasoning pillar (target 84.5 → continuous improvement)
now has a concrete, external calibration harness:

| Component | Path |
|-----------|------|
| Academic multitask knowledge | `src/evaluation/benchmarks/mmlu.py` |
| Owner agents | Scholar (synthesis), Evaluator (scoring), NovaAethrea (memory) |
| Capability keys | `eval.mmlu`, `eval.mmlu.0shot`, `eval.mmlu.5shot`, `knowledge.academic`, `reasoning.multitask` |

Internal design-target numbers in the excellence matrix remain the product goals.
MMLU scores are measured harness results used for regression detection and
Scholar quality tracking — not public leaderboard claims.

## Agent ownership (updated)

| Agent (internal) | Additional responsibility |
|------------------|---------------------------|
| Scholar | MMLU subject routing, few-shot construction, knowledge synthesis |
| Evaluator | Choice extraction, score aggregation, self-correction on eval failures |
| NovaAethrea | Persist EvaluationResult into hybrid memory |
| Nova Reign | Schedule eval jobs under governance DAG + policy gates |
| Agent Zero | Execute harness in sandbox |

User-facing surface continues to name only **Saphira**.
