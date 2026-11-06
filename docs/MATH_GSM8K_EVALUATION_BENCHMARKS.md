# MATH & GSM8K — Mathematical Reasoning Benchmarks

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella  
**Parent:** `docs/STANDARDIZED_EVALUATION_BENCHMARKS.md`

## MATH (Hendrycks et al., 2021)

- **Scope:** Competition mathematics (~12,500 problems)
- **Subjects:** Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- **Metric:** Exact match on final answer (after step-by-step solution)
- **Capability keys:** `eval.math`, `eval.math.exact_match`, `reasoning.mathematical`, `reasoning.quantitative`, `knowledge.competition_math`
- **Paper:** arXiv:2103.03874

## GSM8K (Cobbe et al., 2021)

- **Scope:** ~8.5K grade-school math word problems (1,319 public test)
- **Difficulty:** 2–8 elementary arithmetic steps
- **Metric:** Exact match on final numeric answer (`####` marker)
- **Capability keys:** `eval.gsm8k`, `eval.gsm8k.exact_match`, `reasoning.mathematical`, `reasoning.quantitative`, `knowledge.grade_school_math`
- **Paper:** arXiv:2110.14168

## Pipeline ownership

| Agent (internal) | Role |
|------------------|------|
| **Scholar** | Problem synthesis, few-shot selection |
| **Evaluator** | Answer extraction, exact-match scoring |
| **NovaAethrea** | Persist EvaluationResult |
| **Nova Reign** | Policy / DAG scheduling |

## Usage

```python
from src.evaluation import EvaluationRunner

runner = EvaluationRunner(model_fn=your_agent, agent_name="scholar")
math_res = await runner.run("math", n_shots=0, limit=50)
gsm_res = await runner.run("gsm8k", n_shots=3, limit=100)
print(math_res.overall_score, gsm_res.overall_score)
```

## Offline / CI

Builtin micro-subsets (8 items each) require zero network. Full sets load via HuggingFace (`hendrycks/competition_math`, `openai/gsm8k`) or local JSONL cache.

## Honesty boundary

Internal calibration scores only — not public leaderboard claims.

---

Part of the **Nova Umbrella Ecosystem** by Chelsea Megan Woods.
