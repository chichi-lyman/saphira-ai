from __future__ import annotations

import os
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "saphira",
    broker=os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0")),
    backend=os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0")),
)
celery_app.autodiscover_tasks(["finance"])
celery_app.conf.beat_schedule = {
    "sync-stripe-metered-billing-every-5-min": {
        "task": "finance.tasks.sync_stripe_metered_billing",
        "schedule": crontab(minute="*/5"),
    }
}
celery_app.conf.timezone = "UTC"
