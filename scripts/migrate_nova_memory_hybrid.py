#!/usr/bin/env python3
"""Hybrid vector + graph memory migration for Saphira Nova Umbrella.

Creates / upgrades the PostgreSQL 16 `nova_memory` database with:
  • pgvector extension for semantic search
  • Apache AGE (or Neo4j bridge tables) for relational knowledge graph
  • Append-only episodic event log
  • Bi-directional sync markers for mobile ↔ server

Run once:
    python -m scripts.migrate_nova_memory_hybrid

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import asyncpg
except ImportError:
    print("asyncpg required: pip install asyncpg")
    sys.exit(1)


DATABASE_URL = os.getenv(
    "NOVA_MEMORY_DATABASE_URL",
    "postgresql://saphira:saphira@localhost:5432/nova_memory",
)


MIGRATION_SQL = """
-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Optional: Apache AGE if available on the server
-- CREATE EXTENSION IF NOT EXISTS age;
-- LOAD 'age';
-- SET search_path = ag_catalog, "$user", public;

-- 2. Episodic event log (append-only)
CREATE TABLE IF NOT EXISTS episodic_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         TEXT NOT NULL,
    session_id      TEXT,
    agent_id        TEXT,                     -- internal only, never exposed
    event_type      TEXT NOT NULL,             -- preference | decision | observation | summary
    content         TEXT NOT NULL,
    embedding       vector(1536),             -- adjust dim to your embedding model
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    synced_at       TIMESTAMPTZ,              -- mobile ↔ server sync marker
    policy_hash     TEXT                      -- integrity / audit
);

CREATE INDEX IF NOT EXISTS idx_episodic_user_created
    ON episodic_events (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_episodic_embedding
    ON episodic_events USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- 3. Durable facts / preferences (structured)
CREATE TABLE IF NOT EXISTS durable_facts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         TEXT NOT NULL,
    key             TEXT NOT NULL,
    value           JSONB NOT NULL,
    confidence      REAL DEFAULT 1.0,
    source_event_id UUID REFERENCES episodic_events(id),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, key)
);

-- 4. Knowledge-graph edges (lightweight relational layer)
--    Can later be replaced / mirrored by Apache AGE or Neo4j
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         TEXT NOT NULL,
    subject         TEXT NOT NULL,            -- entity or fact key
    predicate       TEXT NOT NULL,            -- relationship type
    object          TEXT NOT NULL,
    weight          REAL DEFAULT 1.0,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edges_user_subject
    ON knowledge_edges (user_id, subject);

CREATE INDEX IF NOT EXISTS idx_edges_user_object
    ON knowledge_edges (user_id, object);

-- 5. Sync cursor for mobile clients
CREATE TABLE IF NOT EXISTS sync_cursors (
    user_id         TEXT PRIMARY KEY,
    last_event_id   UUID,
    last_synced_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Helpful view for hybrid retrieval
CREATE OR REPLACE VIEW hybrid_memory_view AS
SELECT
    e.id,
    e.user_id,
    e.event_type,
    e.content,
    e.embedding,
    e.metadata,
    e.created_at,
    array_agg(DISTINCT ke.predicate) FILTER (WHERE ke.id IS NOT NULL) AS related_predicates
FROM episodic_events e
LEFT JOIN knowledge_edges ke
    ON ke.user_id = e.user_id
   AND (ke.subject = e.id::text OR ke.object = e.id::text)
GROUP BY e.id;
"""


async def run_migration() -> None:
    print(f"Connecting to {DATABASE_URL.split('@')[-1]} …")
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(MIGRATION_SQL)
        print("✅ Hybrid vector + graph memory schema applied successfully.")
        print("   Tables: episodic_events, durable_facts, knowledge_edges, sync_cursors")
        print("   View:   hybrid_memory_view")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
