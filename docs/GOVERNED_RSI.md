# Governed Recursive Self-Improvement (RSI) Framework for Saphira AI

**Status:** Canonical guidance  
**Owner:** Chelsea Megan Woods  
**Copyright:** © 2026 Chelsea Megan Woods  
**Parent System:** Saphira AI / Nova Umbrella

## Purpose

This document formalizes how the three classic mechanics of recursive self-improvement, bare-metal bootstrapping, and the intelligence explosion are interpreted and constrained inside Saphira AI and all specialist agents.

Saphira deliberately implements **only bounded, policy-gated, measurable improvement loops**. Unconstrained recursive self-improvement or autonomous pursuit of artificial superintelligence is neither enabled nor permitted.

## The Three Mechanics (Theoretical Mapping)

| Mechanic | Theoretical Definition | Saphira Realization |
|----------|------------------------|---------------------|
| Bare-metal bootstrapping | Start from the lowest reliable substrate and construct higher layers while maintaining verifiability | Existing runtime substrate + evolution_engine + self_healing; all changes remain inspectable and logged |
| Recursive Self-Improvement (RSI) | A system that improves the processes that generate its own intelligence | Karpathy-style iterative loops under NovaReign governance and Agent Two security |
| Intelligence explosion / ASI | Accelerating open-ended capability growth leading to superintelligence | Explicitly out of scope. Saphira remains a governed multi-agent assistant |

## Practical Implementation: The Karpathy Loop (Bounded)

All agents and sub-agents may participate in the following closed, auditable loop:

1. Observe telemetry / evaluation metrics (latency, accuracy, recovery rate, user preference signals).
2. Propose a narrow, non-safety parameter or code-level improvement (example: memory top-k, wake sensitivity, synthetic data filter, test coverage).
3. Validate the proposal inside a sandbox or against fixed benchmarks.
4. Apply only if NovaReign (governance) and Agent Two (security) authorize.
5. Record the change in the hash-chained audit / memory store (NovaAethrea).
6. Measure the actual gain; discard or roll back if the gain is not positive or if any safety invariant is touched.

This loop is the only authorized form of self-improvement. It is deliberately analogous to the practical engineering pattern popularized by Andrej Karpathy and others, not to open-ended theoretical RSI.

## Hard Invariants (Never Violated)

- The fixed executive pipeline remains immutable:  
  Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution).
- Persona, core ethics, commercial authority policy, and dual-prompt security rules are never rewritten by any self-improvement process.
- All changes are bounded (currently ≤ 1 % daily performance gain on non-safety parameters inside the evolution engine).
- No agent may acquire new external communication or financial authority without explicit CommercialAuthorityPolicy approval.
- Hardware access (camera, microphone, etc.) remains opt-in and gated by environment flags.

## Agent Responsibilities

- **Saphira (surface)**: Presents improvement outcomes in natural language; never exposes internal agent names or the fact that a self-improvement cycle occurred unless the user asks.
- **Aura**: May propose perception-side improvements (vision thresholds, multimodal routing).
- **Agent Two**: Security review of every proposed change.
- **Nova Reign**: Final governance gate; maintains the improvement ledger.
- **NovaAethrea**: Stores the before/after state and rationale.
- **Agent Zero**: Executes only approved, verified changes.
- Extended family agents (Apex, Lexis, Instinct, Cipher, Scholar, Lyra): Participate only within their domain and under the same gates.

## Relationship to Existing Modules

- `src/core/evolution_engine.py` — already implements the daily bounded optimization and self-healing hooks.
- `src/core/self_healing.py` — stress-test and recovery practice that feeds the improvement loop.
- `src/core/autonomy_levels.py` — improvement actions are capped at L2 (supervised) or L3 (background) according to risk.

## Explicit Non-Goals

- Autonomous rewriting of system prompts, contracts, or the pipeline itself.
- Open-ended architecture search that could alter safety properties.
- Any pathway that could be interpreted as an uncontrolled intelligence explosion.

Saphira improves reliability, latency, and usefulness through disciplined, measurable, reversible loops while remaining a safe, human-aligned assistant.
