from __future__ import annotations

import asyncio
import logging
import os
import uuid

from celery import shared_task
from redis import Redis

from finance.billing import StripeBillingService
from storage.database import require_database

logger = logging.getLogger("saphira.finance.tasks")
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
LOCK_EXPIRE_SECONDS = 280


@shared_task(name="finance.tasks.sync_stripe_metered_billing", bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def sync_stripe_metered_billing(self):
    lock_key = "lock:finance:stripe-metered-billing"
    token = uuid.uuid4().hex
    if not redis_client.set(lock_key, token, nx=True, ex=LOCK_EXPIRE_SECONDS):
        return {"status": "SKIPPED", "reason": "Concurrent execution locked"}

    async def run():
        SessionFactory = require_database()
        async with SessionFactory() as session:
            return await StripeBillingService(session, batch_size=200).sync_metered_billing_batch()

    try:
        result = asyncio.run(run())
        return {"status": "SUCCESS", "details": result}
    except Exception as exc:
        logger.exception("Stripe billing sync failed")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {"status": "FAILED", "reason": str(exc)}
    finally:
        # Delete only our lock token; never release a lock acquired by another worker.
        redis_client.eval("if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end", 1, lock_key, token)
