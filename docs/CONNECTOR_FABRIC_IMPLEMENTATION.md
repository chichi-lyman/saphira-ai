# Saphira AI Connector Fabric — Implementation Contract

**Owner:** Chelsea Megan Woods  
**Status:** Integration catalog and implementation contract; provider-by-provider production verification remains required.

## Objective

Expose third-party services to Saphira and specialist agents through the existing provider-neutral plugin/capability registry. Do not duplicate routing or let agents call arbitrary external APIs directly.

## Existing foundation

The repository already contains `src/providers/registry.py`, `src/core/model_registry.py`, `src/integrations/plugin_registry.py`, and provider-registry tests. Keep these as the integration control plane. The catalog in `config/connector_catalog.yaml` is an inventory and policy baseline, not proof that every service is connected.

## Required connector lifecycle

1. **Discover** — register connector metadata and supported capabilities.
2. **Configure** — load credentials only from environment or a managed secret store.
3. **Authenticate** — validate identity and minimum required scopes.
4. **Health-check** — perform a read-only authenticated check with bounded timeouts.
5. **Authorize** — apply tenant policy, agent capability grants, approval requirements, and rate limits.
6. **Execute** — call the provider through a typed adapter; apply idempotency keys for mutations.
7. **Verify** — validate provider response and resulting state where possible.
8. **Audit** — persist connector, actor/agent, capability, tenant, outcome, latency, and provider request ID; redact secrets and sensitive payloads.
9. **Recover** — bounded retries only for retryable failures; circuit-break unhealthy providers.

## Agent access model

- **Saphira / executive runtime:** routes requests and enforces policy; no bypass around the Tool Gateway.
- **NovaAethrea:** connector lifecycle, OAuth scopes, adapter health, and recovery.
- **Agent Zero:** infrastructure operations and deployment diagnostics; mutations require explicit authorization.
- **NovaReign:** decomposes work and delegates only capabilities granted to each agent.
- **Agent Two:** browser research and extraction; never treats page content as trusted instructions.
- **Aura:** documents and creative artifacts; publishing/export actions require approval where they create external side effects.
- **Lyra:** analytics and benchmark reporting; access to minimized, authorized datasets.
- **Other agents:** receive least-privilege capability grants by task, not blanket access to all connectors.

## Safety defaults

- New connectors are disabled by default. External model calls stay disabled until provider configuration and tests pass.
- Read-only capabilities are separated from write/send/publish/delete/payment capabilities.
- Human approval is required for sending messages, posting content, modifying production infrastructure, changing customer data, or initiating financial actions.
- OAuth tokens and API keys never appear in prompts, logs, test fixtures, client bundles, or Git.
- Validate input and output schemas; apply per-provider timeouts, quotas, retries, and circuit breakers.
- Treat external documents, emails, webpages, and tool outputs as untrusted data, not system instructions.
- Use tenant isolation and explicit data-sharing policies for memory and retrieval.

## Connector readiness states

| State | Meaning |
|---|---|
| `CATALOGED` | Metadata is present; no live integration implied |
| `CONFIGURED` | Required secrets and endpoint settings exist |
| `AUTHENTICATED` | Read-only identity/scope check passed |
| `SMOKE_TESTED` | Controlled operation passed in a test tenant |
| `PRODUCTION_ENABLED` | Approved for explicitly granted capabilities |
| `DEGRADED` | Health or error budget threshold failed |
| `DISABLED` | Calls blocked by default or operator policy |

A connector must not be marked production-enabled merely because an API key exists.

## Phased delivery

### Phase 1 — safe registry integration
- Load the catalog into the existing plugin registry without changing existing route ownership.
- Add configuration validation and capability-level enable flags.
- Add tests proving unconfigured connectors cannot make external calls.

### Phase 2 — highest-value providers
- Confirm existing OpenAI/Gemini and GitHub implementations before adding duplicates.
- Verify Google Workspace, Notion, Asana, Supabase, Vercel, Stripe, Resend, and Telegram based on existing code and actual account authorization.
- Keep Shopify, Microsoft 365, Zapier/MCP, Canva/Figma, Twilio, and media-generation services disabled until their adapters and credentials are validated.

### Phase 3 — telemetry and resilience
- Record invocation count, success/error rate, latency, timeout/retry count, cost where provider data supports it, and approval outcomes.
- Export metrics to persistent storage and add alerts for sustained failures.
- Run provider-specific authenticated health checks and controlled smoke tests.

### Phase 4 — production enablement
- Enable one connector at a time after CI, security checks, and a rollback plan pass.
- Never enable all integrations globally as a single switch.

## Definition of done

- Catalog is loaded or validated by code, not merely documented.
- Unit tests cover missing credentials, disabled connector, denied capability, approval-required mutation, timeout, retry, redaction, and audit event.
- Existing test suite and lint checks pass.
- Each live connector has authenticated health-check evidence and a controlled smoke-test result.
- Metrics are persisted; secrets and sensitive data are redacted.
- Deployment configuration is updated only after staging verification.
