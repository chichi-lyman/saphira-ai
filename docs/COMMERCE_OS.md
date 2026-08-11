# Saphira Autonomous Commerce OS — Foundation Status

This document records what is **implemented and tested** in the repository for the Commerce OS foundation. It does not claim production deployment or autonomous external communication.

## Implemented (Phase 1 foundations)

| Component | Module | Status |
|-----------|--------|--------|
| CommercialAuthorityPolicy | `src/commerce/authority.py` | Implemented + tested |
| Append-only hash-chained audit | `src/commerce/audit.py` | Implemented + tested |
| Commercial lifecycle state machine | `src/commerce/states.py` | Implemented + tested |
| Stripe webhook signature verification | `src/commerce/stripe_webhooks.py` | Implemented + tested |

Package entrypoint: `src/commerce/__init__.py`  
Tests: `tests/commerce/test_authority_audit_stripe.py` (29 tests)

## Non-negotiable invariants

- `PROSPECT → ACTIVE` is rejected.
- `PAYMENT_PENDING → CUSTOMER` is allowed **only** after a signature-verified Stripe event.
- `DENY` and `REQUIRE_APPROVAL` never execute.
- `ALLOW` may execute.
- Every consequential action produces an audit record (including denied and failed attempts).
- The language model does **not** own financial state. Only verified Stripe events activate customers.
- Duplicate Stripe event IDs are ignored (idempotent).

## Commercial product boundary

Initial offer: **Saphira LeadOS — $500/month**

Out-of-policy pricing, unsupported guarantees, and unapproved communication channels are denied by policy.

## First acquisition channel

The Tampa Bay roofing Revenue Brain remains the first controlled acquisition channel:

- Seed runner: `src/tools/run_tampa_roofing_seed.py`
- Pipeline: `src/tools/tampa_roofing_pipeline.py`
- Artifacts: `storage/tampa_roofing_approval_queue.csv`, `storage/tampa_roofing_approval_summary.md`
- All records default to `PENDING_REVIEW` / `NOT_SENT`
- Observed facts are separated from opportunity hypotheses

## Not yet enabled

- Autonomous external communication (voice / SMS / email / chat)
- Provider adapters with live credentials
- Autonomous sales execution
- Live Stripe traffic in production
- Customer OS post-sale automation beyond the state-machine skeleton

## Required environment variables (commerce)

```text
STRIPE_SECRET_KEY=          # existing billing key
STRIPE_WEBHOOK_SECRET=      # webhook signing secret (required for signature verification)
```

Never commit secrets. Configure these in the deployment environment only.

## Build order remaining (locked contract)

1. ~~Governance Kernel~~ (done)
2. ~~Commercial State Machine~~ (done)
3. Provider Interfaces (Voice / SMS / Email / Chat) — contracts only; no external send
4. Sales Agent state machine
5. Stripe checkout session creation + webhook HTTP route wiring
6. Customer OS lifecycle services
7. Integration of Tampa prospects into the commercial state machine
8. Full test gates before controlled activation
9. Controlled activation of external communication by policy only

## Audit record fields

```text
audit_id, execution_id, timestamp, actor, action,
target_type, target_id, policy_decision, reason,
previous_state, resulting_state, event_id, metadata,
previous_hash, record_hash, executed
```

Hash chaining: each record’s `previous_hash` equals the prior record’s `record_hash`. `AuditStore.verify_chain()` detects breaks or content tampering.
