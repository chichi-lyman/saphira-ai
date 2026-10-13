"""Celery application for opt-in background work.

Start a worker with:
    celery -A src.integrations.celery_app:celery_app worker --loglevel=INFO

No task is scheduled at import time. Set CELERY_BROKER_URL in the environment.
"""
from __future__ import annotations

import os

from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "saphira",
    broker=broker_url,
    backend=result_backend,
    include=["src.integrations.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
)
