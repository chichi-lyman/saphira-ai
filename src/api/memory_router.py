"""Server-to-server semantic memory and agent task-ledger endpoints.

These endpoints fail closed unless SAPHIRA_MEMORY_API_KEY is configured. The
key belongs only in backend environment variables, never in browser code.
"""
from __future__ import annotations

import hmac
import json
import os
from functools import lru_cache
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, status
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from src.storage.database import run_statement

router = APIRouter(prefix="/memory", tags=["memory"])


def _authorize(provided_key: str | None) -> None:
    expected = os.getenv("SAPHIRA_MEMORY_API_KEY", "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service is not configured",
        )
    if not provided_key or not hmac.compare_digest(provided_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid memory service key")


@lru_cache(maxsize=1)
def _openai_client() -> AsyncOpenAI:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured for embeddings",
        )
    return AsyncOpenAI(api_key=key)


async def _embed(text: str) -> list[float]:
    response = await _openai_client().embeddings.create(
        model=os.getenv("SAPHIRA_EMBEDDING_MODEL", "text-embedding-3-small"),
        input=text,
        dimensions=1536,
    )
    vector = response.data[0].embedding
    if len(vector) != 1536:
        raise HTTPException(status_code=502, detail="Embedding model returned an unexpected dimension")
    return vector


class MemoryCreate(BaseModel):
    owner_id: UUID
    content: str = Field(min_length=1, max_length=20000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemorySearch(BaseModel):
    owner_id: UUID
    query: str = Field(min_length=1, max_length=8000)
    limit: int = Field(default=5, ge=1, le=20)


class TaskCreate(BaseModel):
    owner_id: UUID | None = None
    agent_name: str = Field(min_length=1, max_length=50)
    status: str = Field(min_length=1, max_length=20)
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=20)
    result: dict[str, Any] | None = None


@router.get("/health")
async def memory_health(x_saphira_memory_key: str | None = Header(default=None)) -> dict[str, str]:
    _authorize(x_saphira_memory_key)
    try:
        rows = await run_statement(
            "SELECT to_regclass('public.saphira_memory') AS memory_table, "
            "to_regclass('public.saphira_task_ledger') AS task_table",
            {},
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Memory database is unavailable") from exc
    if not rows or not rows[0].get("memory_table") or not rows[0].get("task_table"):
        raise HTTPException(status_code=503, detail="Memory schema migration has not been applied")
    return {"status": "healthy", "service": "saphira-memory"}


@router.post("")
async def create_memory(
    request: MemoryCreate,
    x_saphira_memory_key: str | None = Header(default=None),
) -> dict[str, Any]:
    _authorize(x_saphira_memory_key)
    embedding = await _embed(request.content)
    try:
        rows = await run_statement(
            """
            INSERT INTO public.saphira_memory (owner_id, content, embedding, metadata)
            VALUES (CAST(:owner_id AS uuid), :content, CAST(:embedding AS vector), CAST(:metadata AS jsonb))
            RETURNING id, owner_id, content, metadata, created_at
            """,
            {
                "owner_id": str(request.owner_id),
                "content": request.content,
                "embedding": "[" + ",".join(str(value) for value in embedding) + "]",
                "metadata": json.dumps(request.metadata),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not persist memory; verify database migration") from exc
    if not rows:
        raise HTTPException(status_code=500, detail="Memory insert returned no record")
    return rows[0]


@router.post("/search")
async def search_memory(
    request: MemorySearch,
    x_saphira_memory_key: str | None = Header(default=None),
) -> dict[str, Any]:
    _authorize(x_saphira_memory_key)
    embedding = await _embed(request.query)
    try:
        rows = await run_statement(
            """
            SELECT id, owner_id, content, metadata, created_at,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM public.saphira_memory
            WHERE owner_id = CAST(:owner_id AS uuid) AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """,
            {
                "owner_id": str(request.owner_id),
                "embedding": "[" + ",".join(str(value) for value in embedding) + "]",
                "limit": request.limit,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Semantic memory search is unavailable") from exc
    return {"results": rows, "count": len(rows)}


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    x_saphira_memory_key: str | None = Header(default=None),
) -> dict[str, Any]:
    _authorize(x_saphira_memory_key)
    try:
        rows = await run_statement(
            """
            INSERT INTO public.saphira_task_ledger (owner_id, agent_name, status, payload)
            VALUES (CAST(:owner_id AS uuid), :agent_name, :status, CAST(:payload AS jsonb))
            RETURNING task_id, owner_id, agent_name, status, payload, result, updated_at
            """,
            {
                "owner_id": str(request.owner_id) if request.owner_id else None,
                "agent_name": request.agent_name,
                "status": request.status,
                "payload": json.dumps(request.payload),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not write task ledger") from exc
    return rows[0]


@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    x_saphira_memory_key: str | None = Header(default=None),
) -> dict[str, Any]:
    _authorize(x_saphira_memory_key)
    if request.status is None and request.result is None:
        raise HTTPException(status_code=400, detail="Provide status and/or result")
    try:
        rows = await run_statement(
            """
            UPDATE public.saphira_task_ledger
            SET status = COALESCE(:status, status),
                result = CASE WHEN :has_result THEN CAST(:result AS jsonb) ELSE result END
            WHERE task_id = CAST(:task_id AS uuid)
            RETURNING task_id, owner_id, agent_name, status, payload, result, updated_at
            """,
            {
                "task_id": str(task_id),
                "status": request.status,
                "has_result": request.result is not None,
                "result": json.dumps(request.result) if request.result is not None else None,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not update task ledger") from exc
    if not rows:
        raise HTTPException(status_code=404, detail="Task not found")
    return rows[0]
