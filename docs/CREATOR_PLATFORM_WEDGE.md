# Creator Platform Wedge (Phase 0 / 1)

Money movement first. Saphira stays the AI runtime; this wedge sells products through Stripe Checkout.

## Added

- `src/commerce/products.py` — catalog (book, studio sub, makeup, course)
- `src/commerce/creator_checkout.py` — GET products, POST checkout
- `src/commerce/order_ledger.py` — verified purchase log

## Env

STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, PRODUCTION_DOMAIN_URL, optional STRIPE_PRICE_* and DATABASE_URL.

Wire: `app.include_router(creator_router)` from `src.commerce.creator_checkout`.

Copyright © 2026 Chelsea Megan Woods
