# Saphira AI — Plugin & Integration Catalog

Saphira exposes external systems as capability-scoped plugins behind the executive runtime. A plugin is an integration boundary, not a claim that a provider account or credential is connected.

## Core integrations

| Plugin | Capability | Typical operations | Approval |
|---|---|---|---|
| GitHub | development / repository | inspect repositories, issues, PRs, commits | policy-dependent |
| Shopify | commerce | products, customers, orders, storefront workflows | write actions require approval |
| Stripe | billing | subscriptions, billing events, metering | financial actions require approval |
| CRM | sales / CRM | leads, accounts, pipeline, enrichment | write actions require approval |
| Calendar | calendar | availability, events, scheduling | write actions require approval |
| Communications | outreach | approved email/messaging workflows | send actions require approval |
| Web Research | research | grounding, search, synthesis | low-risk read |
| Memory | memory | recall and durable memory writes | policy-dependent |
| Device | device / smart environment | permissioned phone, Bluetooth, accessibility and environment actions | approval by risk |
| Analytics | intelligence | business and system telemetry | low-risk read |

## Plugin contract

Each plugin should provide:

- manifest metadata
- declared capabilities
- explicit scopes
- health check
- capability invocation
- structured results
- audit metadata
- tenant-aware authorization
- secret references rather than raw credentials

The reference registry is implemented in `src/integrations/plugin_registry.py`.

## Security rules

1. Plugins never receive unrestricted authority by default.
2. Side-effecting capabilities declare `side_effects=true`.
3. Financial, destructive, privacy-sensitive, and external communications actions require approval under the active policy.
4. Tenant credentials must remain isolated.
5. Tool calls should be idempotent where possible and auditable.
6. Plugin failures must return structured errors to the executive runtime.
7. Disabled plugins cannot be invoked.

## Connection status

The catalog defines the architecture and adapter boundaries. Production connection still depends on deployment secrets, provider credentials, OAuth installation, tenant authorization, and provider-specific implementation.

This distinction prevents Saphira from reporting an integration as connected merely because its manifest exists.
