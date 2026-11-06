---
name: standardized-evaluation-benchmarks
description: Install and run standardized academic evaluation benchmarks (MMLU and extensions) across Saphira AI and every Nova Umbrella agent. Trigger on MMLU, benchmark, evaluation harness, agent scoring, knowledge tests, or requests to measure multitask academic reasoning.
---

# Standardized Evaluation Benchmarks — Nova Umbrella / Saphira AI

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella

## Purpose

Install a first-class, policy-gated evaluation fabric so every core and extended agent can be measured against industry-standard academic and agent benchmarks. The primary installed benchmark is **MMLU (Massive Multitask Language Understanding)** — 57 subjects covering elementary-to-professional knowledge and cross-domain reasoning.

## Fixed pipeline placement

```
Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance)
→ NovaAethrea (memory) → Agent Zero (execution)
```

Evaluation requests are classified by **Nova Reign**, knowledge items are synthesized by **Scholar**, validation and scoring by **Evaluator**, results written to **NovaAethrea** memory, and execution of the harness by **Agent Zero**.

**User-facing rule:** Only Saphira is named. Internal agent codenames stay masked.

## Capability keys registered

| Key | Meaning |
|-----|---------|
| `eval.mmlu` | Full MMLU evaluation surface |
| `eval.mmlu.0shot` | Zero-shot MMLU |
| `eval.mmlu.5shot` | Five-shot MMLU |
| `knowledge.academic` | Academic knowledge routing |
| `reasoning.multitask` | Multitask reasoning scoring |

## Owner agents

| Agent (internal) | Role |
|------------------|------|
| **Scholar** | Knowledge synthesis, subject routing, few-shot construction |
| **Evaluator** | Output validation, score aggregation, self-correction loops |
| **NovaAethrea** | Persist evaluation results into hybrid memory |
| **Nova Reign** | Policy gates, DAG scheduling of eval jobs |
| **Agent Zero** | Sandbox execution of the harness |

## Installation layout

```
src/evaluation/
  __init__.py
  registry.py          # BenchmarkRegistry
  runner.py            # EvaluationRunner + EvaluationResult
  benchmarks/
    __init__.py
    mmlu.py            # MMLUBenchmark + builtin micro-subset

skills/standardized-evaluation-benchmarks/
  SKILL.md             # this file

docs/STANDARDIZED_EVALUATION_BENCHMARKS.md
tests/evaluation/test_mmlu_harness.py
scripts/run_mmlu_eval.py
```

## Quick start (internal)

```python
from src.evaluation import EvaluationRunner, get_registry

async def my_agent(prompt: str) -> str:
    # Replace with actual agent / LLM call
    return "B"

runner = EvaluationRunner(model_fn=my_agent, agent_name="scholar")
result = await runner.run("mmlu", n_shots=0, limit=20)
print(result.to_dict())
```

CLI:

```bash
python scripts/run_mmlu_eval.py --n-shots 0 --limit 50 --agent scholar
```

## MMLU subject coverage (57)

abstract_algebra, anatomy, astronomy, business_ethics, clinical_knowledge,  
college_biology, college_chemistry, college_computer_science, college_mathematics,  
college_medicine, college_physics, computer_security, conceptual_physics,  
econometrics, electrical_engineering, elementary_mathematics, formal_logic,  
global_facts, high_school_biology, high_school_chemistry, high_school_computer_science,  
high_school_european_history, high_school_geography, high_school_government_and_politics,  
high_school_macroeconomics, high_school_mathematics, high_school_microeconomics,  
high_school_physics, high_school_psychology, high_school_statistics,  
high_school_us_history, high_school_world_history, human_aging, human_sexuality,  
international_law, jurisprudence, logical_fallacies, machine_learning, management,  
marketing, medical_genetics, miscellaneous, moral_disputes, moral_scenarios,  
nutrition, philosophy, prehistory, professional_accounting, professional_law,  
professional_medicine, professional_psychology, public_relations, security_studies,  
sociology, us_foreign_policy, virology, world_religions.

## Design invariants

1. **Offline-first for CI** — builtin micro-subset requires zero network.
2. **Optional full set** — loads `cais/mmlu` via HuggingFace `datasets` when present, or a local JSONL cache.
3. **Policy gated** — evaluation jobs that call external models respect CommercialAuthorityPolicy and autonomy levels.
4. **No marketing claims** — scores are internal design targets / measured harness results, not public leaderboard assertions.
5. **Secret-mask** — never surface Scholar / Evaluator / NovaAethrea names to end users.
6. **Extensible** — new benchmarks register through `BenchmarkRegistry.register(...)`.

## Extending to additional benchmarks

```python
from src.evaluation.registry import get_registry

class MyBench:
    async def evaluate(self, model_fn, **kwargs):
        ...

get_registry().register(
    "my_bench",
    MyBench,
    name="My Benchmark",
    description="...",
    subjects=10,
    category="reasoning",
    owner_agents=["scholar", "evaluator"],
)
```

## Relationship to existing excellence matrix

`docs/SAPHIRA_BENCHMARK_EXCELLENCE.md` tracks system-level pillars (latency, memory hit-rate, tool success, offline path, privacy).  

This skill adds **academic / multitask knowledge** scoring (MMLU) so the Zero-Shot Reasoning pillar and Scholar ownership can be measured against a standardized external reference rather than only internal targets.

## Verification checklist

- [ ] `pytest tests/evaluation/test_mmlu_harness.py` passes offline
- [ ] `eval.mmlu` appears in capability catalog / registry
- [ ] Scholar and Evaluator SKILL or agent docs reference ownership
- [ ] Results can be written to NovaAethrea hybrid memory
- [ ] CI can run the builtin subset without network or HF credentials
