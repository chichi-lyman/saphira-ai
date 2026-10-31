# Saphira AI — Integration Workflows (Zapier · Make · n8n)

**Owner:** Chelsea Megan Woods  
**Repo:** `chichi-lyman/saphira-ai`

Automation tools act as **bridges**. Saphira speaks JSON over HTTPS; Zapier / Make / n8n route that data into spreadsheets, CRMs, email, and the revenue-engine tracker.

---

## Architecture

```text
Saphira FastAPI
   │
   ├─ Outbound  POST → Zapier Catch Hook / Make Webhook / n8n Webhook
   │                 (cross-post, onboarding, revenue sync, broadcast)
   │
   └─ Inbound   POST ← automation tool
                 /api/webhooks/inbound
                 /api/webhooks/inbound/revenue
                 Header: X-Saphira-Automation-Key
```

---

## Environment variables

Add to Railway (or local `.env`):

```bash
# Outbound destinations
N8N_CROSS_POST_WEBHOOK=https://...
N8N_ONBOARDING_WEBHOOK=https://...
N8N_REVENUE_WEBHOOK=https://...          # optional dedicated revenue path
MAKE_WEBHOOK_URL=https://hook.eu1.make.com/...
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/...
SAPHIRA_OUTBOUND_WEBHOOKS=https://...,https://...   # comma-separated extras

# Inbound auth (required in production)
SAPHIRA_AUTOMATION_WEBHOOK_SECRET=long-random-string
```

---

## 1. Revenue engine tracker (recommended first Zap / Scenario)

**Goal:** Every commerce or manual revenue event lands in a Google Sheet / Excel tracker.

### Outbound from Saphira

```python
from src.services.webhook_bridge import get_webhook_bridge

bridge = get_webhook_bridge()
bridge.sync_revenue_event(
    event_type="stripe_payment",
    amount=29.00,
    currency="USD",
    source="stripe",
    metadata={"customer_email": "fan@example.com", "tier": "super"},
)
```

Or via HTTP (secured):

```bash
curl -X POST https://YOUR-BACKEND/api/webhooks/outbound/trigger \
  -H "Content-Type: application/json" \
  -H "X-Saphira-Automation-Key: $SAPHIRA_AUTOMATION_WEBHOOK_SECRET" \
  -d '{"target":"revenue","payload":{"event_type":"manual","amount":50,"currency":"USD"}}'
```

### Zapier / Make / n8n side

1. Create a **Catch Hook** (Zapier) or **Custom Webhook** (Make / n8n).
2. Map fields: `event_type`, `amount`, `currency`, `timestamp`, `metadata.*`.
3. Action: **Create Spreadsheet Row** (Google Sheets / Excel Online).
4. Optional: also notify Telegram / Discord / email.

### Inbound (sheet → Saphira)

If a human edits the tracker and you want Saphira to know:

- Zapier: “New Spreadsheet Row” → Webhooks by Zapier POST to  
  `https://YOUR-BACKEND/api/webhooks/inbound/revenue`  
  with header `X-Saphira-Automation-Key`.

---

## 2. Cross-post & onboarding

Already wired in `WebhookBridge`:

- `trigger_cross_post(payload)` → `N8N_CROSS_POST_WEBHOOK`
- `trigger_onboarding(email, tier)` → `N8N_ONBOARDING_WEBHOOK`

Use the same pattern for Make or Zapier by setting `MAKE_WEBHOOK_URL` / `ZAPIER_WEBHOOK_URL` and calling `trigger_make` / `trigger_zapier`, or use `broadcast()`.

---

## 3. Knowledge expansion

Inbound events with `type` / `event` / `action` of `knowledge_expand`, `ingest`, or `research_result` are accepted and logged for the memory / knowledge pipeline. Extend `WebhookBridge.handle_inbound_event` when you attach a real ingestion worker.

---

## 4. Security

- Always set `SAPHIRA_AUTOMATION_WEBHOOK_SECRET` in production.
- Never put provider API keys or Stripe secrets in Zapier/Make scenario steps that are visible to third parties; keep secrets on the Saphira side or in the automation tool’s secret store.
- Inbound endpoints return 401 when the key is missing or wrong (production).

---

## 5. Health check

```bash
curl https://YOUR-BACKEND/api/webhooks/health
```

---

© 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies / Nova Umbrella
