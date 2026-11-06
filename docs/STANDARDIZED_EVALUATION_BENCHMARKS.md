# Standardized Evaluation Benchmarks — Nova Umbrella Ecosystem

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella  
**Primary repository:** `chichi-lyman/saphira-ai`

## Overview

This document installs **Standardized Evaluation Benchmark Tests** into the Nova Umbrella Ecosystem, Saphira AI, and all core + extended agents.

The first (and currently primary) installed benchmark is:

### MMLU — Massive Multitask Language Understanding

- **Paper:** Hendrycks et al., 2020 (arXiv:2009.03300)
- **Scope:** 57 subjects spanning humanities, social sciences, STEM, and professional domains
- **Format:** 4-choice multiple-choice questions
- **Difficulty:** Elementary → professional level
- **What it measures:** Broad academic, factual, and cross-domain reasoning

MMLU is the closest widely-used “general knowledge + reasoning” test for language models and agent systems. It is now largely saturated at the frontier, yet remains a valuable **internal calibration** tool for routing, Scholar quality, and regression detection.

## Architecture placement

| Layer | Responsibility |
|-------|----------------|
| **Capability Registry** | Registers `eval.mmlu`, `eval.mmlu.0shot`, `eval.mmlu.5shot`, `knowledge.academic`, `reasoning.multitask` |
| **Nova Reign** | Schedules evaluation jobs inside the governance DAG; applies autonomy / policy gates |
| **Scholar** | Owns knowledge synthesis, subject routing, and few-shot example selection |
| **Evaluator** | Validates model outputs, extracts choices, aggregates scores, drives self-correction |
| **NovaAethrea** | Persists `EvaluationResult` objects into hybrid memory for longitudinal tracking |
| **Agent Zero** | Executes the harness inside the existing sandbox / tool fabric |
| **Saphira (surface)** | Never names internal agents; may surface high-level “knowledge calibration” status if asked |

## Module map

```
src/evaluation/
├── __init__.py
├── registry.py          # BenchmarkRegistry (singleton)
├── runner.py            # EvaluationRunner, EvaluationResult
└── benchmarks/
    ├── __init__.py
    └── mmlu.py          # MMLUBenchmark, MMLUConfig, builtin subset

skills/standardized-evaluation-benchmarks/SKILL.md
tests/evaluation/test_mmlu_harness.py
scripts/run_mmlu_eval.py
```

## Running evaluations

### Programmatic

```python
from src.evaluation import EvaluationRunner

async def agent_call(prompt: str) -> str:
    # Wire to Scholar / provider router / local model
    ...

runner = EvaluationRunner(model_fn=agent_call, agent_name="scholar")
result = await runner.run(
    "mmlu",
    n_shots=0,          # or 5
    subjects=None,      # or ["astronomy", "machine_learning"]
    limit=100,          # optional cap for smoke tests
    seed=42,
)
print(result.overall_score, result.per_subject)
```

### CLI

```bash
python scripts/run_mmlu_eval.py --n-shots 0 --limit 50 --agent scholar
python scripts/run_mmlu_eval.py --n-shots 5 --subjects astronomy,machine_learning
```

### Offline / CI mode

By default the harness uses a curated **builtin micro-subset** (12 items across key subjects). This requires:

- zero network
- zero HuggingFace credentials
- deterministic seeding

Full MMLU is loaded automatically when the `datasets` package is available and the `cais/mmlu` dataset can be fetched, or when a local JSONL cache is supplied via `cache_path`.

## Relationship to existing excellence matrix

`docs/SAPHIRA_BENCHMARK_EXCELLENCE.md` already defines system-level design targets:

- Latency (TTS/STT/TTFT)
- Memory retention & recall
- Task automation & tool execution
- Edge / offline capability
- Zero-shot reasoning
- Data privacy & local ownership

MMLU supplies a **standardized external reference** for the Zero-Shot Reasoning pillar and for Scholar’s knowledge surface. Scores produced here are **internal calibration numbers**, not public marketing claims.

## Future benchmark extensions

The `BenchmarkRegistry` is designed for growth. Candidate next installs (when requested):

| Benchmark | Focus |
|-----------|--------|
| MMLU-Pro | Harder, more robust MMLU variant |
| GPQA / GPQA-Diamond | Graduate-level science questions |
| MATH / MATH-500 | Competition mathematics |
| HumanEval / SWE-bench | Code generation & software engineering |
| MMAU | Agent multitask understanding (tool-use, planning, self-correction) |
| AgentBench / AgentBoard | Interactive agent environments |

Each new benchmark follows the same pattern: implement `evaluate(model_fn) → dict`, register under a stable key, assign owner agents, add tests, update this document.

## Honesty & policy boundary

- Scores are measured harness results or design targets only.
- External model calls for evaluation remain under CommercialAuthorityPolicy and autonomy levels (L0–L3).
- No autonomous publication of leaderboard claims.
- Internal agent names stay masked from end users.

## Verification

1. `pytest tests/evaluation/ -q` passes offline.
2. `eval.mmlu` is visible in the capability catalog.
3. A smoke run of the builtin subset completes in < 30 s with a mock model.
4. Results can be serialized and stored via NovaAethrea memory interfaces.

---

Part of the **Nova Umbrella Ecosystem** by Chelsea Megan Woods.
