-- Saphira AI persistent semantic memory and agent task ledger.
-- Apply after confirming the target PostgreSQL instance supports pgvector.
-- Embeddings must be produced by a model configured to return exactly 1536 dimensions.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS saphira_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saphira_memory_created_at
    ON saphira_memory (created_at DESC);

-- Add the vector index only after enough rows exist to justify its maintenance cost.
-- HNSW supports cosine-distance queries via the <=> operator.
CREATE INDEX IF NOT EXISTS idx_saphira_memory_embedding_hnsw
    ON saphira_memory USING hnsw (embedding vector_cosine_ops)
    WHERE embedding IS NOT NULL;

CREATE TABLE IF NOT EXISTS saphira_task_ledger (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saphira_task_ledger_status_updated
    ON saphira_task_ledger (status, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_saphira_task_ledger_agent_updated
    ON saphira_task_ledger (agent_name, updated_at DESC);

CREATE OR REPLACE FUNCTION saphira_set_task_ledger_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_saphira_task_ledger_updated_at ON saphira_task_ledger;
CREATE TRIGGER trg_saphira_task_ledger_updated_at
BEFORE UPDATE ON saphira_task_ledger
FOR EACH ROW
EXECUTE FUNCTION saphira_set_task_ledger_updated_at();

-- Production deployment note:
-- Apply tenant ownership and Row Level Security policies before exposing these
-- tables to client roles. Keep database credentials and service-role keys server-side.
