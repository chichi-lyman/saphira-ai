# Saphira AI — Unified Upgrade Roadmap

## Phase A — Canonical foundation

- Unified executive runtime contracts
- Capability registry
- Plugin registry
- Approval and autonomy policies
- Verification contract
- Persistent memory boundaries
- Event/audit contract

## Phase B — Integration fabric

- GitHub adapter
- Web research adapter
- CRM adapter
- Calendar adapter
- Communications adapter
- Shopify adapter
- Stripe adapter
- Analytics adapter
- Memory adapter
- Device gateway adapter

Each adapter must implement the plugin contract, expose health, enforce scopes, and return structured results.

## Phase C — Business execution

- Lead discovery and enrichment
- Qualification
- Outreach sequencing
- CRM synchronization
- Appointment workflows
- Commerce automation
- Subscription/billing events
- Revenue analytics
- Creator/content workflows

## Phase D — Device intelligence

- `Okay Saphira` wake-word boundary
- realtime STT/TTS
- Android foreground/background voice service
- notification and accessibility adapters
- Bluetooth/device gateway
- smart-environment adapter
- device health and permission telemetry

## Phase E — Enterprise control plane

- tenant provisioning
- RBAC
- agent/worker registry
- task/workflow observability
- memory telemetry
- model and tool usage
- audit events
- cost/revenue dashboards
- policy administration

## Phase F — Production hardening

- integration test matrix
- idempotency and replay protection
- secrets rotation
- rate limits
- circuit breakers and bulkheads
- distributed tracing
- load tests
- backup/restore verification
- disaster recovery runbook
- security review

## Definition of done

Saphira is considered complete for a capability only when the implementation is connected through the executive runtime, has an authenticated adapter, has explicit authorization policy, has verification coverage, emits audit/telemetry events, and passes its integration tests.

Architecture files and manifests in this repository establish the target; they do not falsely mark external credentials or third-party services as connected.
