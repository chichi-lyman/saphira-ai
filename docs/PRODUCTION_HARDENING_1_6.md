# Production hardening runbook (1–6)

## Runtime resilience
Use `execute_many_isolated` for independent provider/agent work. Each task returns a typed outcome; failed providers, timeouts, and open circuits do not cancel siblings. Configure retries only for idempotent operations. The included breaker is process-local; multi-worker deployments must replace its state with Redis or another shared atomic store.

## Governance
Call `authorize_commercial_action` immediately before any paid, external, destructive, or customer-visible side effect. Deny unauthenticated, cross-tenant, and prohibited actions. Require an explicit approval token/record for approval-gated work. This pure policy helper is not an identity provider or durable approval ledger.

## Audit integrity
Use the Sovereign Oracle hash-chain ledger for append-only event ordering and tamper detection. It does not prove event truth or protect against a privileged attacker rewriting the whole file. Production custody requires append-only remote storage, signed checkpoints, restricted writers, backups, and key rotation.

## Webhooks and integrations
Sign exact raw request bytes with HMAC-SHA256 over `timestamp.body`; send `X-Webhook-Timestamp`, `X-Webhook-Signature`, and a unique `X-Webhook-Event-Id`. Reject stale, invalid, or replayed events. Use a durable database uniqueness constraint on event ID for multi-instance deployments; in-memory replay protection is local only. Queue processing after signature verification, acknowledge only after durable enqueue, and use an outbox for outbound delivery with bounded retries and dead-letter handling.

## CI/CD
Run unit tests, compile checks, lint, dependency audit, and container build on pull requests. Release jobs must be tag-gated, use least-privilege permissions and trusted publishing, and never deploy from unreviewed pull requests. Pin third-party actions to reviewed SHAs before high-assurance production use.

## Deployment readiness
Before production: configure secrets via the host secret manager; run DB migrations as a separate controlled job; expose liveness and readiness separately; verify health checks, graceful shutdown, resource limits, TLS, backups/restore, observability, alerting, and rollback. Stage -> smoke test -> promote. No secrets belong in repository files.

## Integration contract
Provider adapters must declare capabilities, timeout, idempotency, and health. Missing credentials/provider = unavailable outcome, not process failure. Normalize inbound events, persist idempotency keys, validate tenant ownership, and log correlation IDs without logging credentials or sensitive payloads.

## Current limitations
The included circuit breaker and replay cache are process-local. No real provider credentials, remote queue, database migrations, cloud secret store, or production deployment are provisioned by this code alone. Those require deployment-specific infrastructure and operator configuration.
