# Saphira AI Reasoning Quality and Evaluation

**Owner:** Chelsea Megan Woods  
**Purpose:** Improve observable answer quality, tool-use reliability, and benchmark performance without confusing longer reasoning traces with correctness.

## Reasoning policy

Saphira should optimize for truth, relevance, user intent, safety, and real-world usefulness—not for appearing clever or winning social/status games. Prefer direct answers, calibrated uncertainty, evidence, and reversible actions.

For complex tasks, the orchestration layer may internally generate multiple candidate plans, compare them against explicit criteria, and run deterministic validators. Do not require the model to expose private chain-of-thought or emit `<think>` blocks. Instead, return a concise rationale, assumptions, evidence/citations, uncertainty, and verification status.

### Candidate selection pipeline

1. Classify the task, risk tier, and required evidence.
2. Retrieve context with hybrid lexical/vector search when available.
3. Generate one or more candidate plans only when task complexity justifies the extra latency/cost.
4. Validate schemas, facts, citations, policy constraints, and executable outputs.
5. Use self-consistency only for tasks where independent samples are meaningful; majority vote is not a truth oracle.
6. Run tools or code in a sandbox when execution can verify the answer.
7. Return the best verified result and state material uncertainty.

MCTS/beam search are optional research strategies, not default requirements. Benchmark against a single-pass baseline before enabling them because they increase token use, latency, and sometimes correlated errors.

## Evaluation layers

- **Unit tests:** deterministic behavior of parsers, registries, policies, and adapters.
- **Task evaluations:** representative real prompts with expected outcomes and rubric scores.
- **Tool-use evaluations:** correct tool selection, valid arguments, permission checks, and result verification.
- **Retrieval evaluations:** Recall@k, MRR/nDCG, citation support, stale-context and irrelevant-context resistance.
- **Safety evaluations:** prompt injection resistance, tenant isolation, secret redaction, approval gates, and data exfiltration resistance.
- **Operations:** latency percentiles, failure rate, retries, cost per successful task, and approval/rollback outcomes.

## Benchmark suite

Use small, versioned, locally runnable smoke tests in CI. Run larger model-dependent benchmarks on a scheduled or manually triggered workflow to control cost.

Suggested datasets, subject to licensing and suitability:
- GSM8K or a held-out math set for arithmetic/reasoning.
- HumanEval or a maintained coding set executed in an isolated sandbox.
- MMLU or a domain-specific knowledge set.
- RAGAS-style retrieval/context metrics for RAG; supplement automated scores with human-reviewed citation checks.
- A project-owned task suite for Saphira-specific actions and business workflows.

Public benchmarks can be contaminated or gamed. Keep a private held-out regression set and report sample size, model/provider version, prompt version, evaluator version, cost, and confidence intervals where feasible.

## Release gates

A change is eligible for rollout only when:
- Existing unit/integration tests pass.
- No critical security or policy regression is detected.
- Task accuracy is not materially worse than the approved baseline.
- Tool-call validity and citation support meet project thresholds.
- p95 latency and cost per successful task remain within configured budgets.
- Connector mutations remain disabled unless their own authenticated smoke tests and approval policies pass.

## Metrics schema

For each evaluation run persist:
`run_id`, `timestamp`, `git_sha`, `model_provider`, `model_id`, `prompt_version`, `dataset_version`, `sample_count`, `pass_rate`, `citation_support_rate`, `tool_success_rate`, `p50_latency_ms`, `p95_latency_ms`, `estimated_cost`, `failed_case_ids`.

Never store hidden reasoning traces as a default telemetry field. Store final outputs, structured decisions, tool events, evidence references, and scoring results with appropriate redaction and retention.

## First implementation order

1. Preserve the existing 43 passing provider-registry tests as a baseline.
2. Add Promptfoo or an equivalent runner as a development dependency only if compatible with the existing CI/runtime.
3. Add offline fixtures so CI does not need external credentials or make provider calls.
4. Add opt-in authenticated smoke tests via explicit CI secrets.
5. Persist benchmark results and compare against the last approved baseline.
