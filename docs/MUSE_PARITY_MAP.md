# Saphira AI ↔ Meta Muse Capability Parity Map

**Status:** Capability contracts + agent routing live  
**Owner:** Chelsea Megan Woods  
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

This document maps every major Meta Muse capability (as of late 2026) onto the
Nova Umbrella multi-agent control plane. Saphira remains the only user-facing
identity; specialist agents execute behind the fixed pipeline:

```
Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero
```

Extended specialists (Apex, Lexis, Instinct, Cipher, Scholar, Lyra) are
dispatched by NovaReign. All external / commercial / credential actions
pass Agent Cipher (Sentinel) and respect autonomy levels.

## Legend
- **Live** — working connector or core path exists
- **Stub** — contract + routing defined; production OAuth / API wiring pending
- **Planned** — documented for roadmap, not yet in capability registry

---

## 1. Core agent behavior

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| Goals → multi-step plan + execute | `reasoning.plan`, `think.mode`, executive orchestrator | Saphira, NovaReign, Agent Zero | Live |
| Background work + notify on approval | autonomy L2/L3 + activity log | NovaReign, NovaAethrea | Stub |
| Ask before sensitive actions | Cipher Sentinel + autonomy L1 | Cipher, Agent Two | Live |
| Watch / intervene mid-task | sandbox session + activity log | Cipher, Agent Zero | Stub |

## 2. Web & computer use

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| Isolated browser / Secure VM | `packages/saphira_core/sandbox` + BrowserDriver | Cipher, Agent Two | Live (contract) |
| Fill forms, multi-site interaction | DOM action schema + Sentinel gate | Cipher | Live (contract) |
| Mac native apps (Mail, Calendar…) | desktop bridge (future) | Agent Zero | Planned |

## 3. Communication

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| Gmail / Outlook read+draft+send | `gmail`, `microsoft_365` connectors | NovaAethrea, Agent Zero | Stub |
| Calendar read/create | `google_calendar`, Microsoft 365 | NovaAethrea | Stub |
| WhatsApp / Telegram / Muse chat | `twilio`, messaging connectors | NovaAethrea | Stub |
| Strip reset/passcode links before read | dual_prompt_security + Cipher | Cipher, Agent Two | Live (heuristic) |

## 4. Travel, local & everyday errands

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| Flights / hotels (Expedia-style) | `travel.book`, travel connector | Apex, Agent Zero | Stub |
| Restaurant bookings (OpenTable) | `local.reserve`, local connector | Instinct, Agent Zero | Stub |
| Wait times, directions | `local.directions`, maps connector | Instinct | Stub |
| Grocery / Instacart-style | `shopping.grocery` | Instinct, Lyra | Stub |
| Fitness (Peloton-style) | `health.fitness` | Lyra | Planned |

## 5. Shopping & money

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| One-time virtual card (Stripe Link) | commerce Stripe + virtual card intent | Apex, Cipher | Stub |
| Shop Pay / Shopify | shopping connector | Apex | Stub |
| Negotiate price / bill | `commerce.negotiate` | Apex, Instinct | Stub |
| Plaid / QuickBooks | finance connectors | Lyra, Apex | Stub |

## 6. Productivity & work

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| Documents, PDFs, dashboards | Aura + document intelligence | Aura, Agent Zero | Stub |
| Reminders, goal tracking, monitors | NovaAethrea memory + awareness loop | NovaAethrea | Stub |
| Notion, Slack, Zoom, Asana, Box, Dropbox, Figma, Canva, GitHub… | MCP + Zapier + dedicated connectors | NovaAethrea, Agent Zero | Partial / Stub |
| Preference memory (editable/forgettable) | NovaAethrea + memory.read/write | NovaAethrea | Live (contract) |
| Full activity log | operational telemetry + audit | NovaReign, Cipher | Stub |

## 7. Creative & media

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| Q&A, image generation | Imagine + persona | Saphira, Aura | Live |
| Recipe reel → grocery list / menu | `creative.recipe_to_list` | Aura, Instinct | Stub |
| Instagram / Facebook / Meta Catalog | existing social connectors | Instinct, Aura | Stub |

## 8. Small-business surface

| Muse capability | Saphira mapping | Agent(s) | Status |
|-----------------|-----------------|----------|--------|
| 15 business connectors one-click | MCP registry + Zapier + commerce | Apex, NovaAethrea | Stub |
| Meta ad / Page / IG professional | Facebook + Instagram connectors | Instinct, Apex | Stub |

## 9. Announced Muse features (not shipped by Meta either)

| Feature | Saphira stance |
|---------|----------------|
| AI glasses / camera view | Planned (device / vision layer) |
| Real-time voice + avatar | Voice stack already partially live |
| Muse email address | Can be added as connector identity |
| Muse Charm pocket device | Out of scope for software monorepo |
| Confidential VM | Local Docker sandbox + Cipher already target this |
| 1Password | Future vault backend for CredentialVault |

## Governance rule (immutable)

Any capability tagged `external_side_effect=true` or involving credentials,
payments, messages, or account changes **must**:

1. Pass Agent Cipher Sentinel gate  
2. Respect `minimum_autonomy` (L1 = user confirm)  
3. Write an audit event  
4. Never place raw secrets in LLM context (CredentialVault only)

See also: `docs/SENTINEL_SANDBOX.md`, `src/core/muse_capabilities.py`, `src/core/autonomy_levels.py`.
