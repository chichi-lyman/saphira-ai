# GPQA — Graduate-Level Google-Proof Q&A

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella  
**Parent:** `docs/STANDARDIZED_EVALUATION_BENCHMARKS.md`  
**Paper:** Rein et al., 2023 (arXiv:2311.12022)

## Overview

GPQA is a challenging multiple-choice benchmark of graduate-level questions in **biology**, **chemistry**, and **physics**, written and validated by domain experts (PhD or PhD-track).

| Split | Questions | Expert acc. | Non-expert (web) acc. |
|-------|-----------|-------------|------------------------|
| Extended | 546 | ~65% | ~34% |
| Main | 448 | ~72% | ~30% |
| **Diamond** | 198 | ~81% | ~22% |

Questions are intentionally **Google-proof**: skilled non-experts with unrestricted web access still score near chance on the Diamond set. This makes GPQA a strong probe of high-level scientific reasoning rather than retrieval.

## Metric

- **Accuracy** on 4-choice MCQ (exact match A/B/C/D)
- Standard reporting today uses the **Diamond** subset (198 items)
- Random baseline: 25%

## Capability keys registered

| Key | Meaning |
|-----|---------|
| `eval.gpqa` | Full GPQA evaluation surface |
| `eval.gpqa.diamond` | Diamond subset preference |
| `reasoning.graduate` | Graduate-level reasoning |
| `reasoning.science` | Scientific reasoning |
| `knowledge.biology` | Biology domain |
| `knowledge.chemistry` | Chemistry domain |
| `knowledge.physics` | Physics domain |

## Pipeline ownership

| Agent (internal) | Role |
|------------------|------|
| **Scholar** | Knowledge synthesis, domain routing, few-shot construction |
| **Evaluator** | Choice extraction, accuracy scoring |
| **NovaAethrea** | Persist EvaluationResult |
| **Nova Reign** | Policy / DAG scheduling |
| **Saphira (surface)** | Never names internal agents |

## Module

```
src/evaluation/benchmarks/gpqa.py   # GPQABenchmark, GPQAConfig, GPQA_DOMAINS
```

## Usage

```python
from src.evaluation import EvaluationRunner

async def reasoner(prompt: str) -> str:
    ...

runner = EvaluationRunner(model_fn=reasoner, agent_name="scholar")
# Diamond-preferring, all domains
result = await runner.run("gpqa", n_shots=0, limit=50)
# Physics only
phys = await runner.run("gpqa", subjects=["physics"], limit=30)
print(result.overall_score, result.per_subject)
```

## Offline / CI

Builtin micro-subset (8 items across biology, chemistry, physics) requires zero network. Full main/Diamond sets load when HuggingFace `datasets` can reach `Idavidrein/gpqa`, or from a local JSONL cache via `cache_path`.

## Honesty boundary

Scores are internal calibration / regression numbers for Scholar quality and graduate reasoning tracking — not public leaderboard claims. Official GPQA examples should not be republished in plain text to reduce training contamination risk.

## Relationship to excellence matrix

GPQA strengthens the **Zero-Shot Reasoning** pillar in `docs/SAPHIRA_BENCHMARK_EXCELLENCE.md` with a standardized graduate science probe beyond MMLU’s broader (but easier) subject mix.

---

Part of the **Nova Umbrella Ecosystem** by Chelsea Megan Woods.
