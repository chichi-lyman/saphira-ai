# Creator Platform Wedge (Phase 0 / 1)

**Blueprint rule:** money movement first, community second, discovery third.

## Wedge files

- `src/commerce/products.py` — catalog
- `src/commerce/creator_checkout.py` — GET/POST `/api/v1/creator/*`
- `src/commerce/order_ledger.py` — verified purchase log
- `tests/test_creator_products.py`

## API

- `GET /api/v1/creator/products`
- `POST /api/v1/creator/checkout` with `{ "sku": "blueprint-book" }`

## SKUs

- blueprint-book $47 digital
- saphira-studio-month $199/mo
- makeup-starter $49 blanka
- course-ai-creators $97 digital

## Wire

```python
from src.commerce.creator_checkout import router as creator_router
app.include_router(creator_router)
```

Env: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, PRODUCTION_DOMAIN_URL, optional STRIPE_PRICE_* and DATABASE_URL.

Copyright © 2026 Chelsea Megan Woods
