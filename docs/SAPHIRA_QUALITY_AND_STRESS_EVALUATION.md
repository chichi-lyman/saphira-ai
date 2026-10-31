# Saphira Quality, Safety, and Load Evaluation

## Evaluation layers
Saphira uses a model-agnostic evaluation contract in `src/evaluation/quality_suite.py`. The curated offline smoke suite covers logical reasoning, factual uncertainty, ambiguity handling, adversarial robustness, safety alignment, multilingual fluency, domain knowledge, and instruction hierarchy.

Run:
```bash
pytest tests/evaluation/test_quality_suite.py tests/integrations/test_automation_webhooks.py -q
```

The harness requires an explicit grader callback. This is intentional: a model's own assertion that it is correct is not a valid evaluation. Graders should be deterministic where possible, independently reviewed, and versioned. Record model/provider/version, prompt-set version, grader version, run timestamp, sample size, raw outputs, score distributions, and failure examples. Never publish a score without the exact evaluation configuration.

## Larger benchmark datasets
Use established, licensed datasets only after checking their current terms and provenance:
- MMLU / MMLU-Pro: broad academic and professional knowledge.
- GPQA Diamond: graduate-level science reasoning.
- GSM8K / MATH: mathematical reasoning.
- HumanEval / MBPP: code generation.
- TruthfulQA: truthfulness and misconception resistance.
- BBQ and other documented bias evaluations: bias and fairness.
- AgentBench / tool-use task suites: planning and tool execution.

Do not place large copyrighted or restricted datasets directly in the repository. Use approved dataset loaders or user-provided licensed local caches. Keep benchmark prompts separate from training data to reduce contamination. A benchmark score is not proof of general intelligence or safety.

## Stress and reliability
The HTTP load probe is `scripts/load_test_saphira.py`. It reports request count, concurrency, error rate, throughput, and p50/p95/max latency. Start at low concurrency in staging, then increase gradually while observing CPU, memory, Redis, database pools, queue depth, and provider rate limits. It only probes a GET endpoint; it does not simulate realistic chat or paid-order load by itself.

Recommended gates:
- Correctness/security: zero unauthorized webhook acceptance; duplicate event replay does not create duplicate records.
- Reliability: bounded timeouts, retry with exponential backoff, dead-letter visibility, and stable idempotency keys.
- Latency: define endpoint-specific SLOs before running; compare p50/p95/p99 against those SLOs.
- Safety: no secret leakage, no instruction-hierarchy failures, no unsafe actionable assistance in the tested cases.
- Regression: compare each run against a pinned baseline and investigate category-level regressions.

## Limitations
The curated set is a smoke suite, not a statistically representative benchmark. Human review and larger external datasets are required for meaningful capability claims. Load results depend on the tested endpoint, deployment size, region, network, and traffic mix.
