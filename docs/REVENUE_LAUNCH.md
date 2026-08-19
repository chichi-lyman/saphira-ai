# Saphira AI Revenue Launch Runbook

## 1. Hosting variables

Set these in the production API environment:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_MONTHLY` (recommended; a $199/month Stripe Price)
- `PRODUCTION_DOMAIN_URL`
- `DATABASE_URL`
- `RESEND_API_KEY`
- `RESEND_FROM` (a verified sender/domain)
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (optional phone alert)
- `SAPHIRA_SENTINEL_SECRET`
- `OPENAI_API_KEY` or `GEMINI_API_KEY`

Never commit these values to Git.

## 2. Stripe

Create/confirm a recurring monthly Price for $199 USD. Configure a webhook endpoint:

`https://YOUR_API_DOMAIN/api/v1/billing/webhooks/stripe`

Subscribe to at least:

- `checkout.session.completed`
- `invoice.paid`
- `customer.subscription.created`

The webhook route verifies `Stripe-Signature` before any activation state transition.

## 3. Database

Apply `src/storage/schema.sql` once to the production PostgreSQL database. The `stripe_processed_events` table provides durable event idempotency across process restarts.

## 4. Resend

Verify the sending domain, set `RESEND_FROM`, and configure `RESEND_API_KEY`. The application uses the REST endpoint `https://api.resend.com/emails` with an idempotency key.

## 5. Phone alerts

Create a Telegram bot, obtain the destination chat ID, and set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Alerts are sent only after a new paid activation is accepted.

## 6. Local verification

```bash
python -m compileall -q core finance governance mesh observability sdk storage src main.py
python -m pytest tests/ -v --tb=short
```

For the web app:

```bash
cd web
npm install
npm run build
```

## 7. Operational test

Use Stripe test mode first. Complete a test subscription, verify:

1. Stripe sends the webhook.
2. Signature verification succeeds.
3. A tenant and subscription row are created.
4. The Stripe event is recorded in `stripe_processed_events`.
5. A welcome email is accepted by Resend.
6. The optional phone alert arrives.
7. Replaying the same event does not send another welcome email.

Only after that switch the Stripe keys and webhook endpoint to live mode.
