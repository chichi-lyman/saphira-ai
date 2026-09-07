"""Saphira AI distributed asynchronous task fabric."""
from __future__ import annotations

import asyncio
import os
from celery import Celery
from celery.schedules import crontab

from src.core.awareness_loop import SaphiraAwarenessEngine
from src.storage.event_ledger import SaphiraEventLedger

broker = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
backend = os.getenv("CELERY_RESULT_BACKEND") or "redis://localhost:6379/1"

celery_app = Celery(
    "saphira_workforce",
    broker=broker,
    backend=backend,
    include=["workers.roofing_tasks"],
)
app = celery_app

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
)

celery_app.autodiscover_tasks(["finance"])
celery_app.conf.beat_schedule = {
    "sync-stripe-metered-billing-every-5-min": {
        "task": "finance.tasks.sync_stripe_metered_billing",
        "schedule": crontab(minute="*/5"),
    }
}


def run_async(coroutine):
    """Run an async coroutine from Celery's synchronous task context."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    raise RuntimeError("run_async cannot execute inside an already-running event loop")


@celery_app.task(name="tasks.deploy_gemini_perception_loop", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def deploy_gemini_perception_loop(self, target_goal: str, tenant_id: str = "DEFAULT"):
    """Run a bounded Gemini perception/reasoning verification job."""
    ledger = SaphiraEventLedger()
    run_async(ledger.commit_log(
        layer="CELERY_WORKER", node="AWARENESS", tenant_id=tenant_id,
        status="STARTED", payload={"target_goal": target_goal},
    ))
    try:
        result = run_async(SaphiraAwarenessEngine().execute_goal_with_awareness(target_goal))
        run_async(ledger.commit_log(
            layer="CELERY_WORKER", node="AWARENESS", tenant_id=tenant_id,
            status=result.get("status", "UNKNOWN"), payload={"result": result},
        ))
        return result
    except Exception as exc:
        run_async(ledger.commit_log(
            layer="CELERY_WORKER", node="AWARENESS", tenant_id=tenant_id,
            status="FAILED", payload={"error": str(exc)},
        ))
        raise


@celery_app.task(name="tasks.execute_omnipresent_workflow", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def execute_omnipresent_workflow(self, job_title: str, user_instruction: str, tenant_context: dict):
    """Coordinate an enterprise job without granting model output direct execution authority."""
    tenant_id = tenant_context.get("tenant_id", "DEFAULT")
    ledger = SaphiraEventLedger()
    run_async(ledger.commit_log(
        layer="CELERY_WORKER", node="ORCHESTRATOR", tenant_id=tenant_id,
        status="STARTED", payload={"job_title": job_title, "instruction": user_instruction},
    ))

    try:
        # The first production workload is the governed awareness pipeline.
        result = run_async(SaphiraAwarenessEngine().execute_goal_with_awareness(user_instruction))
        run_async(ledger.commit_log(
            layer="CELERY_WORKER", node="ORCHESTRATOR", tenant_id=tenant_id,
            status=result.get("status", "UNKNOWN"), payload={"outcome": result},
        ))
        return {"status": result.get("status", "UNKNOWN"), "telemetry": result}
    except Exception as exc:
        run_async(ledger.commit_log(
            layer="CELERY_WORKER", node="CRITICAL_FAILURE", tenant_id=tenant_id,
            status="FAILED", payload={"error": str(exc), "job_title": job_title},
        ))
        raise
