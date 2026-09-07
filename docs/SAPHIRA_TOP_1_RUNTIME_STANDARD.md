# Saphira™ Top-1% Runtime Standard

**Owner:** Chelsea Megan Woods™
**Status:** Canonical architectural contract

## Core invariant

> The model proposes; Saphira's deterministic runtime decides.

No LLM output may directly cause a side effect. Every consequential action follows:

`PROPOSE → VALIDATE → AUTHORIZE → RESERVE → EXECUTE → VERIFY → COMMIT`

Failure or uncertainty follows an explicit terminal/recovery path. Repair and re-planning happen upstream of side effects.

## Trust boundaries

| Component | Trust role |
|---|---|
| LLM | Untrusted planner/compiler |
| Pydantic/JSON contracts | Structural validation |
| Policy engine | Deterministic authority |
| Reservation layer | Idempotency/concurrency boundary |
| PostgreSQL ledger | Transactional execution truth |
| Workers/tools | Controlled side effects |
| Verification/reconciliation | External truth confirmation |

## SLO targets

These are engineering targets, not claims about current production performance:

- UI acknowledgment: ≤100 ms
- Text first token: ≤500 ms
- Voice first audio: ≤700 ms
- Tool progress event: ≤250 ms
- Background-task acknowledgment: ≤500 ms

Hard invariants: zero unauthorized consequential side effects, zero duplicate consequential executions, zero cross-tenant leakage, zero phantom completions.

## Execution states

```text
PROPOSED → VALIDATED → AUTHORIZED → RESERVED → EXECUTING → VERIFYING → COMMITTED
```

Failure states:

`VALIDATION_FAILED`, `AUTHORIZATION_DENIED`, `RESERVATION_FAILED`, `EXECUTION_FAILED`, `VERIFICATION_FAILED`, `ROLLED_BACK`.

Unknown external outcomes enter `RECONCILIATION_REQUIRED`.

```text
CONFIRMED → COMMIT
NOT_FOUND  → SAFE RETRY
AMBIGUOUS  → HUMAN REVIEW / HOLD
```

Blind retries are prohibited for unknown side-effect outcomes.

## Immutable context scope

Every memory retrieval and authorization decision must carry:

`tenant → user → conversation → task → execution`

Required execution context is immutable. Global, unscoped memory retrieval is prohibited for private task state.

## Dual execution paths

### Fast path

Use for zero-side-effect conversational work, direct streaming, simple reads, and low-risk transformations. Avoid unnecessary agent orchestration.

### Work path

Use for complex tasks. It supports asynchronous queues, workers, checkpoints, deadlines, verification, reconciliation, and governance gates.

## Feature shipping gate

Every feature must answer **yes** to all five questions:

1. **Execution truth:** Are all state transitions recorded and verifiable?
2. **Context isolation:** Can another tenant/task/session influence this state?
3. **Deterministic authority:** Can the model bypass policy? It must be **no**.
4. **Latency budget:** Does the feature fit the relevant SLO or explicitly declare a different budget?
5. **Recoverability:** Does failure reconcile, retry safely, or roll back without guessing?

If any answer is no, the feature is not production-ready.

## Operational truth rule

Saphira must never claim an action completed unless the execution ledger contains verified evidence of completion.

**By Chelsea Megan Woods™ #ChelseaMe**
