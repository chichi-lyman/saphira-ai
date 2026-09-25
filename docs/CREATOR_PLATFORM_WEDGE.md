# Creator Platform Wedge (Phase 0 / 1)

**Rule from the blueprint:** money movement first, community second, discovery third.

Saphira stays the AI agent runtime. This wedge adds a thin product slice so money can move before a full two-sided creator platform exists.

## What already existed

- `CommercialAuthorityPolicy` (ALLOW / REQUIRE_APPROVAL / DENY)
- Append-only commerce audit
- Stripe webhook signature verification
- Subscription checkout (`stripe_checkout.py`) and billing webhook router
- Tenant provisioning on verified `checkout.session.completed`

## What this wedge adds

| Piece | Path | Purpose |
|-------|------|--------|
| Product catalog | `src/commerce/products.py` | Book, studio sub, makeup kit, course SKUs |
| Creator checkout API | `src/commerce/creator_checkout.py` | `GET /api/v1/creator/products`, `POST /api/v1/creator/checkout` |
| Order ledger | `src/commerce/order_ledger.py` | Verified-purchase log (memory + optional Postgres) |

## Critical gaps still open (honest)

| Gap | Status after wedge |
|-----|--------------------|
| Stripe Checkout + webhook activation | Improved (one-time + existing sub) |
| Multi-tenant creator login product | Still missing — runtime ≠ SaaS app |
| Full auth (OAuth, MFA) | Still missing |
| Community (live, DMs, groups) | Phase 2 — not started |
| Media transcoding / CDN | Outsource later (Mux/Cloudflare) |
| Mobile app | Later |
| Stripe Connect multi-creator payouts | Not in wedge — dogfood single merchant first |

## Env vars

```bash
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
PRODUCTION_DOMAIN_URL=https://your-domain
STRIPE_PRICE_ID=                     # optional studio subscription Price
STRIPE_PRICE_BLUEPRINT_BOOK=         # optional
STRIPE_PRICE_MAKEUP_STARTER=         # optional
STRIPE_PRICE_COURSE_AI=              # optional
DATABASE_URL=                        # optional; ledger + tenants
```

## Dogfood path (no-budget)

1. Create Products/Prices in Stripe Dashboard (or rely on inline `price_data`).
2. Point webhook to `/api/v1/billing/webhooks/stripe`.
3. Sell Blueprint book + studio via `POST /api/v1/creator/checkout` with `sku`.
4. Fulfill digital goods manually or by email; makeup via Blanka.
5. Only after self-serve money works, consider Stripe Connect for other creators.

## Wire-up

Register in app factory / `main.py`:

```python
from src.commerce.creator_checkout import router as creator_router
app.include_router(creator_router)
```

Policy: `GENERATE_CHECKOUT` remains ALLOW; `CONFIRM_PAYMENT` / `ACTIVATE_SUBSCRIPTION` stay DENY for the LLM — only verified webhooks activate.

Copyright © 2026 Chelsea Megan Woods
