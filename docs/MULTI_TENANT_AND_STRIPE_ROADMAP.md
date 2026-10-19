# Multi-Tenant Auth & Stripe Monetization Roadmap

**Owner:** Chelsea Megan Woods  
**Status:** Scaffolding present — expansion in progress  
**Date:** 2026-10-19

---

## Existing Foundation (already in repo)

| Component | Path | Notes |
|-----------|------|-------|
| Stripe Checkout | `src/commerce/stripe_checkout.py` | Subscription session creation |
| Stripe Webhooks | `src/commerce/stripe_webhooks.py` | Event handling surface |
| Commercial Authority | `src/commerce/authority.py` | ALLOW / REQUIRE_APPROVAL / DENY matrix |
| Audit / Ledger | `src/commerce/audit.py`, `order_ledger.py` | Hash-chained commercial audit |
| Products | `src/commerce/products.py` | Product definitions |
| Billing Router | `src/commerce/billing_router.py` | FastAPI routes |

## Target Tiers (from valuation roadmap)

| Tier | Price | Capabilities |
|------|-------|--------------|
| Freemium | $0 | Limited messages, basic skills |
| Pro | $10–$20 / mo | Higher limits, priority skills, memory depth |
| Ultra | $30–$50 / mo | Full Super Saphira Heavy limits, advanced agents, priority support |

## Immediate Expansion Tasks

1. **Entitlement Service**
   - Map Stripe `price_id` / product → internal entitlement set
   - Store tenant_id → plan → limits (messages/4h, DeepSearch/day, images/day, voice minutes)
   - Enforce limits inside orchestrator / capability registry before expensive work

2. **Multi-Tenant Isolation**
   - Every request carries `tenant_id` (from auth token or API key)
   - Memory, conversation history, and tool results scoped by tenant
   - No cross-tenant data leakage

3. **Stripe Product & Price Setup**
   - Create three products in Stripe Dashboard (Freemium is free tier, no price)
   - Pro and Ultra as recurring prices
   - Update `STRIPE_PRICE_ID_PRO` and `STRIPE_PRICE_ID_ULTRA` env vars

4. **Webhook Hardening**
   - Signature verification (already expected)
   - On `customer.subscription.updated` / `deleted` → update local entitlement record
   - On `invoice.paid` → confirm active status

5. **Usage Metering**
   - Emit usage events (messages, tool calls, tokens) tagged with tenant_id
   - Optional future: metered billing for overage

## Policy Invariants (do not break)

- LLM never activates subscriptions or confirms payments directly (`ACTIVATE_SUBSCRIPTION` and `CONFIRM_PAYMENT` are DENY in authority matrix).
- All commercial state changes flow through signed Stripe webhooks + local ledger.
- Agent Zero and tool fabric remain downstream of entitlement checks.

## Next Concrete Code Deliverables

- [ ] `src/commerce/entitlements.py` — plan → limits lookup + enforcement helper
- [ ] Orchestrator pre-flight check that consults entitlements
- [ ] Environment variable documentation for the two paid price IDs
- [ ] Simple admin endpoint (protected) to inspect tenant plan status

**Copyright © 2026 Chelsea Megan Woods**
