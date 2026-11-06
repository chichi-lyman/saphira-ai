# Coding Evaluation Benchmarks — HumanEval & MBPP

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella  
**Parent:** `docs/STANDARDIZED_EVALUATION_BENCHMARKS.md`

## Installed benchmarks

### HumanEval (OpenAI, 2021)

- **Size:** 164 handwritten Python problems
- **Format:** Function signature + docstring prompt; model completes the body
- **Metric:** **pass@1** (fraction of problems where a single generated completion passes all unit tests)
- **Setting:** Zero-shot (standard)
- **Capability keys:** `eval.humaneval`, `eval.humaneval.pass_at_1`, `coding.python`, `coding.zero_shot`, `reasoning.code_generation`

### MBPP — Mostly Basic Python Problems (Google Research)

- **Size:** ~974 problems (sanitized test split commonly ~500)
- **Format:** Natural-language task description + 3 assert tests
- **Metric:** **pass@1**
- **Setting:** Zero-shot or few-shot (InCoder-style prompts supported)
- **Capability keys:** `eval.mbpp`, `eval.mbpp.pass_at_1`, `coding.python`, `coding.basic`, `reasoning.code_generation`

Both harnesses are **offline-first**: a curated micro-subset ships in-repo for CI and smoke tests. Full datasets load automatically when HuggingFace `datasets` is available (`openai_humaneval`, `google-research-datasets/mbpp`).

## Pipeline ownership

| Layer | Role |
|-------|------|
| **Nova Reign** | Schedules coding eval jobs; applies autonomy / sandbox policy |
| **Scholar** | Prompt construction, few-shot selection |
| **Evaluator** | Extracts code, runs restricted execution, aggregates pass@1 |
| **Agent Zero** | Sandbox execution of generated programs |
| **NovaAethrea** | Stores EvaluationResult history |
| **Saphira (surface)** | Never names internal agents |

## Module map

```
src/evaluation/benchmarks/
  humaneval.py    # HumanEvalBenchmark
  mbpp.py         # MBPPBenchmark
  mmlu.py         # (existing)

src/evaluation/registry.py   # registers humaneval + mbpp
tests/evaluation/test_coding_benchmarks.py
```

## Usage

```python
from src.evaluation import EvaluationRunner

async def coder(prompt: str) -> str:
    # Wire to coding agent / provider
    ...

runner = EvaluationRunner(model_fn=coder, agent_name="scholar")
he = await runner.run("humaneval", limit=20)
mb = await runner.run("mbpp", limit=50)
print(he.overall_score, mb.overall_score)  # pass@1
```

## Safety notes

- Execution uses a restricted `__builtins__` set and short timeouts.
- Production runs should route through Agent Zero’s existing sandbox / policy gates.
- Scores are internal calibration numbers, not public leaderboard claims.

## Relationship to excellence matrix

Coding pass@1 feeds the **Task Automation & Tool Execution** and **Zero-Shot Reasoning** pillars in `docs/SAPHIRA_BENCHMARK_EXCELLENCE.md`, giving Scholar / Agent Zero a standardized external reference for Python code generation quality.

---

Part of the **Nova Umbrella Ecosystem** by Chelsea Megan Woods.
