# Celery and Stripe integration

**Owner:** Chelsea Megan Woods  
**Status:** Implemented as opt-in runtime modules; not yet authenticated against a live service or mounted into public FastAPI routes.

## Celery background jobs

Runtime dependencies include `celery[redis]`. The Celery app is `src.integrations.celery_app:celery_app`; its starter task is `saphira.healthcheck`. Importing the app does not enqueue work. JSON-only serialization is configured, and tasks use late acknowledgements and bounded retry settings where declared.

Environment:
- `CELERY_BROKER_URL` — Redis or another supported Celery broker URL.
- `CELERY_RESULT_BACKEND` — optional result backend URL.
- `REDIS_URL` — fallback broker URL.

Run a worker after provisioning Redis:

```bash
celery -A src.integrations.celery_app:celery_app worker --loglevel=INFO
```

Do not use the local default Redis URL in production without provisioning, authentication, network controls, and monitoring. Avoid placing secrets in task arguments; use stable IDs and fetch authorized data inside tasks. Tasks that send messages, modify records, or initiate payments must require explicit authorization, idempotency, and audit logging.

## Stripe subscription checkout

`src.integrations.stripe_service.create_subscription_checkout` creates a Stripe-hosted Checkout Session in subscription mode. It requires `STRIPE_SECRET_KEY`, a Price ID via `STRIPE_PRICE_MONTHLY` or `STRIPE_PRICE_ID`, authenticated user context supplied by the caller, and an idempotency key. `verify_webhook` validates the raw request body using `STRIPE_WEBHOOK_SECRET`.

Security requirements before exposing this through the API:
1. Authenticate the customer and derive `user_id` server-side; never trust a client-provided account identity.
2. Allowlist success/cancel URL hosts in the API route; HTTPS validation in the helper is only a baseline.
3. Keep secret keys and webhook secrets in a managed secret store/environment only.
4. Verify webhook signatures against the unmodified raw request bytes.
5. Make webhook processing idempotent by persisting Stripe event IDs and processing subscription state from verified events.
6. Treat Checkout redirect as UX only; grant entitlements only after verified webhook events.
7. Use Stripe test mode first; live charges are not enabled by these modules alone.
8. Add authorization, rate limiting, audit records, and tenant checks in the API layer before invoking the helper.

## Verification status

Unit tests use a mocked Stripe SDK and do not make network calls. No live Stripe request, Redis connection, worker deployment, or production billing enablement has been performed by these code changes.
