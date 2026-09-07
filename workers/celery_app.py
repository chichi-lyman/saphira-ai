"""Celery application entry point for Saphira background work."""
from __future__ import annotations

import os

from celery import Celery

broker = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
backend = os.getenv("CELERY_RESULT_BACKEND") or "redis://localhost:6379/1"

celery_app = Celery(
    "saphira",
    broker=broker,
    backend=backend,
    include=["workers.roofing_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Compatibility alias for `celery -A workers.celery_app worker`.
app = celery_app
