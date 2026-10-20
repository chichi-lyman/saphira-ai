# Stress-Test Engineering Breakdown — Throughput, Drift, Bottlenecks

**Author:** Chelsea Megan Woods  
**Status:** Engineering analysis + fix blueprint (scorecard numbers are **illustrative / not live-measured** unless marked otherwise)  
**Date:** 2026-10-20  
**Related:** `NOVA_UMBRELLA_STRESS_TEST_MATRIX.md`, `execution_contract.py`, `provider_router.py`, `HUMAN_LOGIC_RULEBOOK.md`, `self_healing.py`

---

## 0. Honesty on scores

Live head-to-head numbers (tokens/sec, context decay at 128k, multi-agent drift %) require controlled harnesses, identical prompts, and paid API budgets.  
**The table below is a structural comparison frame**, not a published benchmark from this monorepo’s CI. Saphira rows that depend on a base model inherit that model’s metrics.

When Matrix Levels 2–5 exist, replace illustrative cells with measured values from `EvidenceStore` / telemetry.

---

## 1. Comparison frame (illustrative under load)

| Architecture | Peak throughput under load | Context decay @ long context | Multi-agent loop drift | System latency (TTFT) |
|--------------|----------------------------|------------------------------|------------------------|------------------------|
| Google Gemini-class | High (provider-scale) | Strong long-context retention | Moderate without fixed gatekeeper | Provider-dependent |
| OpenAI frontier-class | High | Moderate decay risk on very long tasks | Moderate without fixed pipeline | Often strong TTFT |
| **Saphira monorepo** | **Variable (local vs API)** | **Driven by routed base model** | **Lower when executive pipeline + contract hold** | **Local routing can be sub-cloud; API path inherits provider** |
| Open multi-agent graphs (e.g. unconstrained AutoGen-style) | Variable | Model-dependent | **High drift risk without hard gatekeeper** | Graph overhead can dominate |

**Drift (definition used here):** share of runs where an autonomous sub-process loses the original user instruction and enters an unrecoverable loop across ≥10 consecutive internal steps.

**Saphira advantage (structural, not magic numbers):** fixed executive pipeline + masked specialists + seven-stage contract reduce ungoverned agent-to-agent chatter.

---

## 2. The good (structural)

### Saphira monorepo
- **Fixed executive pipeline** — single public surface (Saphira); internal agents not user-facing → less leakage and clearer authority.
- **Monorepo cohesion** — shared deps reduce fragmented framework version skew.
- **Contract + commercial authority** — DENY / REQUIRE_APPROVAL never execute gated side-effects.

### Cloud hyper-scalers
- **Brute-force context and serving** — managed long context, global capacity, continuous model iteration.
- Saphira correctly **consumes** them via `provider_registry` rather than trying to own their clusters.

---

## 3. The bad (what breaks under stress)

### Saphira
1. **API routing bottleneck** — heavy reasoning still depends on external keys; provider outage propagates unless local fallback exists.
2. **Tier / queue fragility** — concurrent deep jobs can exhaust workers and plan quotas without hard timeouts and RESERVE metering.
3. **Unmeasured drift** — isolation is architectural; drift % is not yet a published CI metric (Level-1 only covers functional policy).

### Unconstrained multi-agent frameworks
- **Open agent chat without a gatekeeper** — high loop risk, token burn, conflicting intermediate state.

---

## 4. Engineering blueprint (three fixes)

```
[User Input] → [Executive Saphira Pipeline] → [Route decision]
                      │
         prefer local SLM if task is light
                      │
              complex? ──YES──→ cloud provider (registry)
                      └──NO───→ local vLLM/Ollama (if enabled)
```

### Fix 1 — Local fallback routing
- **Code:** `src/core/local_fallback.py`, `provider_router.py`, `providers/registry.py`

### Fix 2 — Worker timeouts
- **Code:** `src/core/worker_timeouts.py` (8s soft / 15s hard, max 10 hops)

### Fix 3 — Human Logic Rulebook validator
- **Code:** `src/core/logic_validator.py` (gates before user-visible COMMIT)

---

## 5. Matrix mapping

| Blueprint item | Matrix features |
|----------------|-----------------|
| Local fallback | 36, 37, 38 |
| Worker timeouts | 13, 20 |
| Logic validator | 2, 7, 22 |

---

## 6. What this document does not claim

- Published production tokens/sec for Saphira vs Gemini  
- 12% drift as a measured CI number  
- Local SLM equals frontier reasoning quality  

---

*Measure under the matrix. Fix bottlenecks with code. Do not invent live scoreboards.*
