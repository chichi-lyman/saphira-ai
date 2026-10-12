# Copyright © 2026 Chelsea Megan Woods
# Saphira AI — Agent Task & Plugin Draft API
#
# Authenticated endpoints for multi-agent task submission and reviewable
# plugin specifications. Integrates with existing device token auth and
# the swarm / orchestrator layers. Does not execute untrusted code.

from __future__ import annotations

import os
import secrets
import time
import uuid
from pathlib import Path
from typing import Any, List, Literal, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/agents", tags=["agents"])

DEVICE_TOKEN = os.environ.get("SAPHIRA_DEVICE_TOKEN", "")
PLUGIN_DIR = Path(os.environ.get("SAPHIRA_PLUGIN_DRAFT_DIR", "plugin_drafts"))
MAX_ACTIVE_TASKS = 100

AGENT_NAMES = {
    "apex", "lexis", "cipher", "novareign", "novaaethrea",
    "aura", "agent_zero", "agent_two", "lyra", "saphira",
    "instinct", "scholar",
}

# In-memory demo state. Replace with Redis + Celery + PostgreSQL for multi-instance.
_task_status: dict[str, dict[str, Any]] = {}
_task_queue: list[dict[str, Any]] = []


def require_device_token(value: Optional[str]) -> None:
    if not DEVICE_TOKEN:
        raise HTTPException(
            status_code=503, detail="Device authentication is not configured"
        )
    if not value or not secrets.compare_digest(value, DEVICE_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")


class TaskRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=10_000)
    agents: List[str] = Field(default_factory=lambda: ["apex"], max_length=12)


class PluginDraftRequest(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{1,48}$")
    description: str = Field(min_length=10, max_length=4000)
    language: Literal["python", "javascript"] = "python"


@router.post("/tasks", status_code=202)
async def submit_task(
    body: TaskRequest,
    x_saphira_device_token: Optional[str] = Header(default=None),
):
    require_device_token(x_saphira_device_token)

    unknown = set(body.agents) - AGENT_NAMES
    if unknown:
        raise HTTPException(400, f"Unknown agents: {sorted(unknown)}")

    if len(_task_queue) >= MAX_ACTIVE_TASKS:
        raise HTTPException(429, "Task queue is full")

    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "goal": body.goal,
        "agents": list(dict.fromkeys(body.agents)),
    }
    _task_status[task_id] = {"state": "queued", "created_at": time.time()}
    _task_queue.append(task)

    # TODO: hand off to SwarmOrchestrator or Celery task for real execution
    return {"task_id": task_id, "state": "queued"}


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    x_saphira_device_token: Optional[str] = Header(default=None),
):
    require_device_token(x_saphira_device_token)
    item = _task_status.get(task_id)
    if item is None:
        raise HTTPException(404, "Task not found")
    return {"task_id": task_id, **item}


@router.post("/plugins/drafts", status_code=202)
async def create_plugin_draft(
    body: PluginDraftRequest,
    x_saphira_device_token: Optional[str] = Header(default=None),
):
    require_device_token(x_saphira_device_token)

    # Stores a specification only. No code is executed or deployed.
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    draft_id = str(uuid.uuid4())
    destination = PLUGIN_DIR / f"{draft_id}.txt"

    content = (
        f"Plugin: {body.name}\n"
        f"Language: {body.language}\n"
        f"Description:\n{body.description}\n"
        "Status: DRAFT_REQUIRES_REVIEW\n"
    )
    destination.write_text(content, encoding="utf-8")

    return {
        "draft_id": draft_id,
        "status": "DRAFT_REQUIRES_REVIEW",
        "message": "Specification saved. No code executed or deployed.",
    }
