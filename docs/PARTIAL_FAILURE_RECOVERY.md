# Partial Failure Recovery and Provider Resilience

## Required behavior
- Missing provider credentials disable only that provider; other configured providers remain eligible.
- Provider timeouts and unexpected adapter exceptions are captured and do not abort fallback.
- Fallback attempts are bounded to the configured preference list and one attempt per provider per invocation.
- Three consecutive provider errors open a process-local 30-second circuit breaker for that provider.
- A successful provider call resets that provider failure counter.
- Explicit safety/policy rejections are returned immediately. Saphira must never evade a refusal by silently switching providers.
- Independent agent subtasks return per-task success/rejected/failed outcomes; one rejection does not cancel siblings.
- Global disablement remains a deliberate hard stop.

## Response semantics
- `success`: all subtasks succeeded.
- `partial`: at least one subtask succeeded and one was rejected or failed.
- `failed`: no subtask succeeded.
- `rejected`: a task was refused by authorization or policy.
- `not_configured`: no eligible provider was configured.
- `unavailable`: provider is cooling down or unreachable.

## Operational limits
The provider circuit breaker is process-local and resets on restart; it is not a distributed breaker. For multi-worker deployments, move breaker state to Redis or a shared coordination store. The current fallback uses a 45-second per-provider timeout, a threshold of three consecutive errors, and a 30-second cooldown. Tune these against provider SLAs and end-to-end latency budgets.

## Security invariants
- Never retry or route around policy/authorization rejections.
- Never treat a partial response as a completed consequential action.
- Preserve idempotency keys for retried writes.
- Require verification before marking an external action complete.
- Do not include provider secrets or raw credentials in task outcome messages.