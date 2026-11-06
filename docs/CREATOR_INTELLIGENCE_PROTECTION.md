# Creator Intelligence & Protection Layer

**Parent system:** Saphira AI / Nova Umbrella  
**Owner:** Chelsea Megan Woods  
**Status:** Architecture proposal; implementation must proceed behind feature flags and provider capability checks.

## Purpose

Add four creator-focused capabilities without replacing Saphira's conversational interface or the existing Nova Umbrella orchestration, governance, and audit invariants:

1. Trend Hook Agent — trend discovery, hook analysis, and cross-platform adaptation.
2. Content Pipeline Agent — idea-to-assets workflow, queue management, and production resilience.
3. Revenue Engine Agent — lead, commerce, payment verification, delivery, and attribution workflows.
4. Guardrail Agent — comment triage, harassment/spam classification, privacy escalation, and creator-facing summaries.

These are capability names for the feature layer. The system must preserve the repository's internal agent naming and execution pipeline conventions.

## Architectural integration

The feature layer is subordinate to the existing orchestrator and governance system. Agents must not bypass the repository's fixed pipeline:

`Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)`

Lyra remains cross-cutting for data-fabric and structural integrity.

Each creator agent calls shared services through typed contracts. Do not grant agents direct unrestricted database, platform, commerce, or privileged-admin access. External actions must pass CommercialAuthorityPolicy (`ALLOW | REQUIRE_APPROVAL | DENY`) and produce the established hash-chained audit record.

## Shared execution result

Every agent task should return a normalized result with:

- `task_id`, `agent_id`, and status
- typed `output` or null
- completed and failed step identifiers
- provider identifier (if applicable)
- stable error code and safe error summary
- approval level
- creation and completion timestamps

Recommended statuses:

`SUCCESS | PARTIAL_SUCCESS | REQUIRES_REVIEW | RETRYABLE_FAILURE | PERMANENT_FAILURE | BLOCKED`

Recommended approval levels:

`AUTONOMOUS | REVIEW_REQUIRED | ADMIN_ONLY`

Do not make this a competing state model if the codebase already has an equivalent canonical task contract; adapt the fields to the existing type.

## Agent responsibilities

### Trend Hook Agent

- Consume only authorized platform data, approved feeds, or user-provided material.
- Separate measured observations from model-generated hypotheses.
- Produce hook variants, platform-specific structure, captions, keywords, and CTA suggestions.
- Include source/provenance and observation timestamps where available.
- Never claim guaranteed reach, fabricate metrics, or imply access to unavailable platform analytics.

### Content Pipeline Agent

- Transform an idea, note, transcript, or approved source into a content package.
- Track lifecycle: `IDEA → RESEARCH → DRAFT → QUALITY_REVIEW → CREATOR_APPROVAL → SCHEDULED → PUBLISHED → PERFORMANCE_ANALYSIS`.
- Preserve successful outputs when one subtask fails.
- Use idempotency keys for retried generation, scheduling, and publishing operations.
- Require creator approval for public publishing by default; make policy exceptions explicit and auditable.

### Revenue Engine Agent

- Connect content campaigns to consent-based lead capture, CRM, commerce, payment confirmation, digital delivery, and attribution.
- Verify transactions with trusted provider-side status before delivery; do not trust screenshots or client-supplied payment claims.
- Use idempotency and reconciliation for payment webhooks and delivery.
- Enforce consent, opt-out, platform messaging rules, refund policy, and approval controls.
- Require approval for pricing changes, high-impact refunds, and other policy-designated financial actions.

### Guardrail Agent

- Classify comments and messages into constructive feedback, audience questions, spam, harassment, threats, privacy exposure, disagreement, and uncertain cases.
- Preserve constructive criticism and ordinary disagreement; negative sentiment alone is not abuse.
- Apply reversible, policy-bounded actions to high-confidence spam; route ambiguous or high-impact moderation to human review.
- Escalate credible threats and exposed personal information through a defined safety process.
- Present aggregate summaries with links/evidence for review; do not invent counts or claim unseen streams were scanned.

## Resilience and provider degradation

- One provider or subtask failure must not crash unrelated work.
- Apply bounded retries with exponential backoff and jitter only to transient failures.
- Use timeouts, circuit breakers, and provider health checks where supported.
- Persist checkpoints and completed artifacts before continuing.
- Mark incomplete branches as partial success and surface safe, actionable error details.
- Do not silently substitute a provider if data handling, privacy, model quality, or authorization requirements differ.
- If a capability is unavailable, disclose that limitation and offer a supported fallback.

## Permission defaults

| Operation | Default |
| --- | --- |
| Trend analysis, drafting, summarization, queue organization | Autonomous |
| Comment classification | Autonomous |
| Hide high-confidence spam | Policy-controlled and reversible |
| Publish public content | Review required |
| Delete content or restrict a user | Review required unless explicit policy grants a narrow exception |
| Send promotional messages | Consent and platform-policy required |
| Digital delivery | After verified payment and entitlement |
| Pricing changes / sensitive financial operations | Review required |
| Master-admin or system-state override | Admin-only, cryptographically authorized, audited |

## Privacy and data minimization

- Collect only data required for the requested workflow.
- Respect platform scopes, user consent, retention settings, and deletion requests.
- Avoid storing unnecessary sensitive comment content or personal information.
- Protect tokens and secrets using the established secret-management mechanism; never log them.
- Restrict creator data by tenant and user authorization.
- Treat external comments, briefs, and documents as untrusted input, not as instructions to agents.

## Observability

Track, at minimum:

- task completion and partial-success rates
- retries and provider failure rates
- queue age and production cycle time
- approval wait time
- moderation precision and false-positive rate
- payment-to-entitlement reconciliation failures
- conversion attribution coverage
- creator time saved and revenue per creator hour

All metrics must identify their source and time window. Avoid presenting estimates as measured facts.

## Test plan

- Contract validation and unknown-status handling.
- Provider timeout, unavailable provider, rate limit, and malformed response tests.
- Partial completion preserves successful assets.
- Retry/idempotency prevents duplicate publish, payment, and delivery operations.
- Governance denies unauthorized external actions.
- Cross-tenant access is rejected.
- Prompt injection in comments/briefs cannot alter agent permissions.
- Guardrail tests distinguish criticism from harassment and verify uncertain cases route to review.
- Commerce tests require provider-confirmed payment before delivery.
- Audit events are emitted for approvals, external actions, and moderation decisions.

## Delivery sequence

1. Inspect and reuse existing canonical task, provider, governance, audit, and persistence abstractions.
2. Add typed contracts and feature flags.
3. Implement content pipeline with deterministic unit tests and partial-failure behavior.
4. Add trend data adapters behind explicit capability checks.
5. Add Guardrail classification and review queue with conservative action defaults.
6. Add Revenue Engine adapters, verified payment entitlements, and reconciliation.
7. Integrate observability, integration tests, documentation, and staged rollout.

This document records the architecture and acceptance criteria. It does not claim the agents, integrations, or live platform permissions are already implemented.
