"""Async PostgreSQL connection helpers for Saphira's server-side stores."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def _database_url() -> str:
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(
        _database_url(),
        pool_pre_ping=True,
        connect_args={"statement_cache_size": 0},
    )


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def database_ready() -> bool:
    try:
        async with get_engine().connect() as connection:
            await connection.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False


async def run_statement(statement: str, parameters: dict[str, Any]) -> list[dict[str, Any]]:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(__import__("sqlalchemy").text(statement), parameters)
        rows = [dict(row) for row in result.mappings().all()]
        await session.commit()
        return rows
