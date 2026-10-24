"""Safe starter tasks for Saphira's Celery worker."""
from __future__ import annotations

from src.integrations.celery_app import celery_app


@celery_app.task(
    name="saphira.healthcheck",
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def healthcheck(self) -> dict[str, str]:
    """Worker liveness task; does not call external services or mutate user data."""
    return {"status": "ok", "task_id": str(self.request.id)}
