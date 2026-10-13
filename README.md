# Saphira AI — Monorepo

© 2026 Chelsea Megan Woods

Unified workspace for **Saphira AI** and specialist agents.

## Layout

```text
saphira-ai/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── packages/saphira_core/
├── agents/
├── src/
│   └── integrations/
│       ├── celery_app.py
│       ├── tasks.py
│       └── stripe_service.py
├── config/connector_catalog.yaml
├── docs/
└── tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-dev.txt
pip install -e .
make test
```

## Celery worker

Provision Redis first, configure `CELERY_BROKER_URL` and optionally `CELERY_RESULT_BACKEND`, then run:

```bash
celery -A src.integrations.celery_app:celery_app worker --loglevel=INFO
```

The worker is opt-in. Importing the app does not schedule jobs. See [Celery and Stripe integration](docs/CELERY_STRIPE_INTEGRATION.md).

## Stripe

Configure server-side `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and `STRIPE_PRICE_MONTHLY` with Stripe **test-mode** values first. Checkout and webhook helper functions are implemented, but the API routes, authenticated live smoke tests, webhook event persistence, and production enablement remain deployment tasks. Do not grant subscription access based on a redirect alone; grant it after verified webhook processing.

## Connector security

Catalog entries are disabled by default. Credentials belong in environment variables or a secret manager, never source control or prompts. Mutating integrations require caller-side authentication, authorization, idempotency, and audit logging. The catalog is not proof that a third-party account is connected.
