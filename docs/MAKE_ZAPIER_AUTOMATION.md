# Saphira AI — Make/Zapier Automation Webhooks

## Purpose
This integration gives Saphira a provider-neutral event contract. Make.com and Zapier can receive outbound Saphira events and send approved automation events back to Saphira. The automation platform remains responsible for routing records into Google Sheets or another CRM.

## Endpoints
- `GET /api/integrations/automation/health` — reports configuration presence only; never returns secrets.
- `POST /api/integrations/automation/events` — authenticated inbound event; writes accepted events to Redis Stream `saphira:automation:inbox`.
- `POST /api/integrations/automation/test` — authenticated outbound connectivity test to the configured catch-hook.
- `publish_automation_event(...)` — internal async function for domain services to emit an event to the configured catch-hook.

## Environment
Set these in the deployment secret manager (never commit values):
- `SAPHIRA_AUTOMATION_WEBHOOK_SECRET` — high-entropy shared secret sent as `X-Saphira-Automation-Key` by Make/Zapier when calling Saphira.
- `SAPHIRA_AUTOMATION_OUTBOUND_URL` — Make Custom Webhook URL or Zapier Catch Hook URL.
- `REDIS_URL` — durable event inbox and 24-hour idempotency keys. Inbound events fail closed when Redis is unavailable.

## Event envelope
```json
{
  "event_id": "shopify-order-98765-paid",
  "event_type": "order.paid",
  "source": "shopify",
  "occurred_at": "2026-10-31T12:00:00Z",
  "tenant_id": "tenant-1",
  "correlation_id": "campaign-TT-001",
  "data": {
    "order_id": "98765",
    "currency": "USD",
    "gross_amount": "35.00",
    "payment_status": "paid",
    "campaign_id": "TT-001"
  }
}
```

Allowed event types: `lead.created`, `lead.qualified`, `lead.opted_out`, `order.paid`, `order.refunded`, `order.fulfilled`, `content.metrics.updated`, `automation.test`.

## Make.com scenario
1. Create a **Custom Webhook** trigger.
2. Copy its URL into `SAPHIRA_AUTOMATION_OUTBOUND_URL`.
3. Add a filter on `event_type`.
4. Map `lead.created`, `order.paid`, `order.refunded`, and `content.metrics.updated` into Google Sheets modules.
5. Use `event_id` as the unique key for an upsert/search-before-add step; do not blindly append retries.
6. For events sent back to Saphira, use HTTP > Make a request to `POST https://YOUR_SAPHIRA_HOST/api/integrations/automation/events`, JSON body matching the envelope, and header `X-Saphira-Automation-Key`.

## Zapier scenario
1. Create **Webhooks by Zapier → Catch Hook** and set its URL as `SAPHIRA_AUTOMATION_OUTBOUND_URL`.
2. Add Paths/Filters by `event_type`.
3. Map fields to Google Sheets using Lookup Spreadsheet Row + Create/Update Row, keyed by `event_id` or the stable business key (`lead_id` / `order_id`).
4. To send an event to Saphira, use Webhooks by Zapier → Custom Request to the same inbound endpoint with the same authentication header.

## Revenue Engine mapping
- Leads: stable `lead_id`, received timestamp, platform, campaign/post ID, keyword, permission basis, stage, next action, outcome.
- Orders: stable Shopify `order_id`, order timestamp, payment status, gross, refunds, fees, chargebacks, net, fulfillment status, campaign ID/UTM evidence.
- Content: platform, post ID, reach, profile visits, unique keyword requests, clicks, product visitors, checkout starts, verified paid orders, gross/net receipts.
- Consent: source/evidence, purpose, status, opt-out timestamp. Suppress opted-out contacts.

## Reliability and safety
- Inbound requests require a shared secret, constant-time credential comparison, allowlisted event types, Redis-backed 24-hour deduplication, and a Redis Stream inbox.
- Redis is required for durable inbound acceptance; the endpoint returns 503 if the event store is unavailable so the sender can retry.
- Outbound HTTP requests have bounded timeouts. Failed delivery is reported; production callers should retry with exponential backoff and preserve the same `event_id`.
- Never include access tokens, payment credentials, full card data, or unnecessary personal data in event payloads.
- Treat paid orders as revenue only after Shopify confirms payment. Refunds and chargebacks must update net receipts. Unmatched campaign attribution remains `unattributed`; do not infer attribution.
- This scaffold does not create Make/Zapier scenarios, connect Google Sheets, provision Redis, or deploy secrets. Those require credentials and configuration in the respective accounts.

## Local verification
```bash
pip install -e '.[dev]'
pytest tests/integrations/test_automation_webhooks.py -q
```
