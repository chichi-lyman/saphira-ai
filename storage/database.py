from __future__ import annotations

import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL", "")

_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
AsyncSessionFactory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False) if _engine else None


def require_database() -> async_sessionmaker[AsyncSession]:
    if AsyncSessionFactory is None:
        raise RuntimeError("DATABASE_URL is not configured")
    return AsyncSessionFactory
