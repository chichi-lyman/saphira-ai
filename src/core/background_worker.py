# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Quiet L3 background execution — real-world tasks without blocking conversation.

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

from src.core.autonomy_levels import SaphiraAutonomy

logger = logging.getLogger("SaphiraBackground")


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundJob:
    id: str
    kind: str
    payload: Dict[str, Any]
    autonomy: str = SaphiraAutonomy.L3_BACKGROUND.value
    status: str = JobStatus.QUEUED.value
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    notify_user: bool = False  # soft ping when done if True
    session_id: Optional[str] = None

    def public_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Never expose raw internal agent traces in public widget payload
        if self.result and isinstance(self.result, dict):
            d["result"] = {
                "status": self.result.get("status", "done"),
                "summary": self.result.get("summary") or self.result.get("message"),
            }
        return d


class BackgroundWorker:
    """
    In-process async queue for silent real-world work.

    Conversation stays responsive; jobs run under L2/L3 policy.
    Handlers are registered by kind (e.g. iot.lights, iot.vacuum, research).
    """

    def __init__(self, max_concurrent: int = 4):
        self._jobs: Dict[str, BackgroundJob] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._max_concurrent = max_concurrent
        self._workers: List[asyncio.Task] = []
        self._started = False

    def register_handler(
        self,
        kind: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]],
    ) -> None:
        self._handlers[kind] = handler

    async def start(self) -> None:
        if self._started:
            return
        self._started = True
        for i in range(self._max_concurrent):
            self._workers.append(asyncio.create_task(self._loop(i)))
        logger.info("Background worker started (%s slots)", self._max_concurrent)

    async def stop(self) -> None:
        self._started = False
        for t in self._workers:
            t.cancel()
        self._workers.clear()

    def enqueue(
        self,
        kind: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        autonomy: str = SaphiraAutonomy.L3_BACKGROUND.value,
        notify_user: bool = False,
        session_id: Optional[str] = None,
    ) -> BackgroundJob:
        job = BackgroundJob(
            id=str(uuid.uuid4())[:12],
            kind=kind,
            payload=payload or {},
            autonomy=autonomy,
            notify_user=notify_user,
            session_id=session_id,
        )
        self._jobs[job.id] = job
        try:
            self._queue.put_nowait(job.id)
        except Exception:
            # Fallback if loop not running yet
            asyncio.get_event_loop().create_task(self._queue.put(job.id))
        logger.info("Queued background job %s kind=%s", job.id, kind)
        return job

    def get(self, job_id: str) -> Optional[BackgroundJob]:
        return self._jobs.get(job_id)

    def list_recent(self, limit: int = 20, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        jobs = list(self._jobs.values())
        if session_id:
            jobs = [j for j in jobs if j.session_id == session_id]
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return [j.public_dict() for j in jobs[:limit]]

    def pending_notifications(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for j in self._jobs.values():
            if not j.notify_user or j.status != JobStatus.DONE.value:
                continue
            if session_id and j.session_id != session_id:
                continue
            out.append({
                "job_id": j.id,
                "kind": j.kind,
                "summary": (j.result or {}).get("summary") or (j.result or {}).get("message") or "Done.",
            })
            j.notify_user = False  # one-shot
        return out

    async def _loop(self, worker_id: int) -> None:
        while True:
            job_id = await self._queue.get()
            job = self._jobs.get(job_id)
            if not job or job.status == JobStatus.CANCELLED.value:
                continue
            job.status = JobStatus.RUNNING.value
            job.started_at = time.time()
            handler = self._handlers.get(job.kind)
            try:
                if handler is None:
                    # Default no-op with honest summary — real handlers plug in later
                    await asyncio.sleep(0.05)
                    job.result = {
                        "status": "success",
                        "summary": f"Queued work '{job.kind}' noted; handler not wired yet.",
                        "message": f"Queued work '{job.kind}' noted; handler not wired yet.",
                    }
                else:
                    job.result = await handler(job.payload)
                job.status = JobStatus.DONE.value
            except Exception as e:
                logger.exception("Background job %s failed", job_id)
                job.status = JobStatus.FAILED.value
                job.error = str(e)
                job.result = {"status": "failed", "summary": "Something needed attention in the background."}
            finally:
                job.finished_at = time.time()
                self._queue.task_done()


# Process singleton
background_worker = BackgroundWorker()


def register_default_handlers() -> None:
    """Lightweight stubs so the queue is usable before full IoT wiring."""

    async def _echo(payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "summary": payload.get("summary") or "Background step finished quietly.",
            "message": payload.get("summary") or "Background step finished quietly.",
            "payload": payload,
        }

    for kind in (
        "iot.lights",
        "iot.vacuum",
        "iot.media",
        "iot.bed",
        "iot.appliance",
        "research",
        "memory.ingest",
        "lifestyle.adjust",
        "generic",
    ):
        background_worker.register_handler(kind, _echo)
