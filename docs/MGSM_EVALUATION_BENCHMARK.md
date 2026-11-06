# MGSM — Multilingual Grade School Math

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella  
**Parent:** `docs/STANDARDIZED_EVALUATION_BENCHMARKS.md`  
**Paper:** Shi et al., 2022 — *Language Models are Multilingual Chain-of-Thought Reasoners* (arXiv:2210.03057)

## Overview

MGSM extends GSM8K by translating **250** grade-school math word problems into **10 typologically diverse languages** (+ English). It evaluates multi-step mathematical reasoning under multilingual conditions.

| Code | Language |
|------|----------|
| `en` | English |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `ru` | Russian |
| `zh` | Chinese |
| `ja` | Japanese |
| `th` | Thai |
| `sw` | Swahili |
| `bn` | Bengali |
| `te` | Telugu |

## Metric

- **Exact match** on the final numeric answer
- Scores typically averaged across all languages
- Random / non-reasoning baseline is low for multi-step items

## Capability keys

| Key | Meaning |
|-----|---------|
| `eval.mgsm` | Full MGSM surface |
| `eval.mgsm.exact_match` | Exact-match scoring |
| `reasoning.mathematical` | Mathematical reasoning |
| `reasoning.multilingual` | Cross-lingual reasoning |
| `knowledge.grade_school_math` | Grade-school math knowledge |

## Pipeline ownership

| Agent (internal) | Role |
|------------------|------|
| **Scholar** | Multilingual prompt synthesis, few-shot selection |
| **Evaluator** | Numeric answer extraction (language-aware patterns), scoring |
| **NovaAethrea** | Persist EvaluationResult |
| **Nova Reign** | Policy / DAG scheduling |

## Usage

```python
from src.evaluation import EvaluationRunner

runner = EvaluationRunner(model_fn=your_agent, agent_name="scholar")
result = await runner.run("mgsm", n_shots=0, limit=50)
subset = await runner.run("mgsm", subjects=["es", "zh"], limit=30)
print(result.overall_score, result.per_subject)
```

## Offline / CI

Builtin micro-subset (8 items across en/es/fr/de/zh/ja) requires zero network. Full set loads via HuggingFace `juletxara/mgsm` or local JSONL cache.

## Honesty boundary

Internal calibration scores only — not public leaderboard claims.

---

Part of the **Nova Umbrella Ecosystem** by Chelsea Megan Woods.
