from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import stripe
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class UsageRecord(BaseModel):
    transaction_id: str
    tenant_id: str
    agent_did: str
    gross_amount_usd: Decimal
    stripe_customer_id: str
    stripe_meter_event_name: str
    timestamp: datetime


class StripeBillingService:
    def __init__(self, session: AsyncSession, batch_size: int = 100):
        self.session = session
        self.batch_size = batch_size

    async def fetch_pending_usage_events(self) -> list[UsageRecord]:
        result = await self.session.execute(text("""
            SELECT art.id, art.tenant_id, art.agent_did, art.gross_amount_usd, art.created_at,
                   tc.stripe_customer_id, COALESCE(am.stripe_meter_event_name, 'agent_execution_units')
            FROM agent_revenue_transactions art
            JOIN tenant_customers tc ON art.tenant_id = tc.tenant_id
            JOIN agent_marketplace am ON art.agent_did = am.agent_did
            WHERE art.status = 'PENDING'
            ORDER BY art.created_at ASC LIMIT :limit
        """), {"limit": self.batch_size})
        return [UsageRecord(
            transaction_id=str(r[0]), tenant_id=r[1], agent_did=r[2], gross_amount_usd=Decimal(str(r[3])),
            timestamp=r[4] or datetime.now(timezone.utc), stripe_customer_id=r[5], stripe_meter_event_name=r[6]
        ) for r in result.fetchall()]

    async def record_stripe_meter_events(self, events: list[UsageRecord]) -> list[str]:
        if not stripe.api_key:
            raise RuntimeError("STRIPE_SECRET_KEY is not configured")
        synced: list[str] = []
        for event in events:
            try:
                # Stripe's SDK call is blocking; keep it off the async event loop.
                await __import__("asyncio").to_thread(
                    stripe.billing.MeterEvent.create,
                    event_name=event.stripe_meter_event_name,
                    payload={"value": str(event.gross_amount_usd), "stripe_customer_id": event.stripe_customer_id},
                    timestamp=int(event.timestamp.timestamp()),
                    identifier=f"saphira_{event.transaction_id}",
                )
                synced.append(event.transaction_id)
            except Exception:
                import logging
                logging.getLogger("saphira.finance.billing").exception("Stripe sync failed for %s", event.transaction_id)
        return synced

    async def mark_transactions_settled(self, transaction_ids: list[str]) -> int:
        if not transaction_ids:
            return 0
        result = await self.session.execute(text("""
            UPDATE agent_revenue_transactions SET status = 'SETTLED'
            WHERE id = ANY(CAST(:ids AS uuid[]))
        """), {"ids": transaction_ids})
        return result.rowcount

    async def sync_metered_billing_batch(self) -> dict[str, Any]:
        events = await self.fetch_pending_usage_events()
        if not events:
            return {"processed_count": 0, "synced_to_stripe": 0, "settled_count": 0}
        synced = await self.record_stripe_meter_events(events)
        settled = await self.mark_transactions_settled(synced)
        await self.session.commit()
        return {"processed_count": len(events), "synced_to_stripe": len(synced), "settled_count": settled}
