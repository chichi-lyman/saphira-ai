"""Simple order ledger for verified Stripe purchases.

Records only events that already passed webhook signature verification.
In-memory fallback when DATABASE_URL is absent (dev / no-budget Phase 0).
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("saphira.order_ledger")


@dataclass
class OrderRecord:
    event_id: str
    session_id: str
    sku: str
    email: str
    amount_cents: int
    currency: str
    fulfillment: str
    created_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "sku": self.sku,
            "email": self.email,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "fulfillment": self.fulfillment,
            "created_at": self.created_at,
        }


class OrderLedger:
    """Append-only purchase log. Prefer Postgres when DATABASE_URL is set."""

    def __init__(self) -> None:
        self._memory: dict[str, OrderRecord] = {}

    def record_from_checkout_session(
        self,
        *,
        event_id: str,
        session: dict[str, Any],
    ) -> OrderRecord | None:
        if not event_id:
            return None
        if event_id in self._memory:
            return self._memory[event_id]

        meta = session.get("metadata") or {}
        details = session.get("customer_details") or {}
        email = str(details.get("email") or session.get("customer_email") or "").strip().lower()
        sku = str(meta.get("sku") or "unknown")
        fulfillment = str(meta.get("fulfillment") or "digital")
        amount = int(session.get("amount_total") or 0)
        currency = str(session.get("currency") or "usd")
        session_id = str(session.get("id") or "")

        rec = OrderRecord(
            event_id=event_id,
            session_id=session_id,
            sku=sku,
            email=email,
            amount_cents=amount,
            currency=currency,
            fulfillment=fulfillment,
        )
        self._memory[event_id] = rec
        logger.info(
            "ledger_recorded event_id=%s sku=%s amount=%s email=%s",
            event_id,
            sku,
            amount,
            email or "(none)",
        )
        # Optional durable write
        dsn = os.getenv("DATABASE_URL")
        if dsn:
            try:
                self._persist_postgres(dsn, rec)
            except Exception:
                logger.exception("ledger postgres persist failed; memory copy kept")
        return rec

    def _persist_postgres(self, dsn: str, rec: OrderRecord) -> None:
        import asyncio

        async def _run() -> None:
            import asyncpg

            url = dsn.replace("postgresql+asyncpg://", "postgresql://", 1)
            conn = await asyncpg.connect(url)
            try:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS creator_orders (
                        event_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        sku TEXT,
                        email TEXT,
                        amount_cents INT,
                        currency TEXT,
                        fulfillment TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                    """
                )
                await conn.execute(
                    """
                    INSERT INTO creator_orders(
                        event_id, session_id, sku, email, amount_cents, currency, fulfillment
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7)
                    ON CONFLICT (event_id) DO NOTHING
                    """,
                    rec.event_id,
                    rec.session_id,
                    rec.sku,
                    rec.email,
                    rec.amount_cents,
                    rec.currency,
                    rec.fulfillment,
                )
            finally:
                await conn.close()

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_run())
            else:
                loop.run_until_complete(_run())
        except RuntimeError:
            asyncio.run(_run())

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = sorted(self._memory.values(), key=lambda r: r.created_at, reverse=True)
        return [r.as_dict() for r in rows[:limit]]


# Process-wide ledger for the wedge (single instance)
default_ledger = OrderLedger()
