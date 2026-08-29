# Saphira AI — Plugin & Integration Catalog

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Saphira exposes external systems as capability-scoped plugins behind the executive runtime. A plugin is an integration boundary, not a claim that a provider account or credential is connected.

## Core Utility Plugins (Everyday & Productivity)

| Plugin | Capability | Typical operations | Approval |
|---|---|---|---|
| Google Workspace | workspace / productivity | schedule appointments, draft emails, read Drive files | write actions require approval |
| Microsoft 365 | workspace / productivity | Outlook, Teams, OneDrive, calendar, and document automation | write actions require approval |
| Web Research | research / grounding | live web browse, scrape, fact-check, summarized research | low-risk read |
| Document Intelligence | document / pdf | parse and summarize PDFs, spreadsheets, and text | low-risk read |
| Code Interpreter | code / sandbox | execute Python, analyze data, generate charts and assets | execute gated by policy |
| Image Generation | media / image | generate visual assets via DALL·E / Midjourney-class bridges | generation requires approval |

## Extended Workflow & Automation Plugins

| Plugin | Capability | Typical operations | Approval |
|---|---|---|---|
| Zapier / Make.com | automation / workflow | connect to 5,000+ apps for background workflows (CRM, content, ops) | side-effecting actions require approval |
| Twilio | communications / sms / voice | SMS alerts, voice-to-text, multi-channel messaging | send and call require approval |
| Stripe | billing / payments | subscriptions, checkout links, micro-transactions | financial actions require approval |
| Social & Content Transmutation | social / content | ingest video/links, transcripts, auto captions and summaries | publish actions require approval |

## Additional Core Integrations

| Plugin | Capability | Typical operations | Approval |
|---|---|---|---|
| GitHub | development / repository | inspect repositories, issues, PRs, commits | policy-dependent |
| Shopify | commerce | products, customers, orders, storefront workflows | write actions require approval |
| CRM | sales / CRM | leads, accounts, pipeline, enrichment | write actions require approval |
| Calendar | calendar | availability, events, scheduling | write actions require approval |
| Communications | outreach | approved email/messaging workflows | send actions require approval |
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

Connector stubs for Google Workspace, Microsoft 365, Zapier, Twilio, Document Intelligence, Code Interpreter, Image Generation, and Social Content live under `src/connectors/`.

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

## Gemini-style workspace reference

A modular single-screen workspace component with Deep Obsidian & Cyberpunk Neon aesthetic is documented in `docs/GEMINI_WORKSPACE_COMPONENT.md` and implemented as a reference under `saphira-app/src/components/workspace/`.
