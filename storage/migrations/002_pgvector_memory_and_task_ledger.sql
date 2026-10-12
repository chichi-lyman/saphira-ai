-- Saphira AI persistent semantic memory and agent task ledger.
-- Embeddings use 1536 dimensions (OpenAI text-embedding-3-small default).
-- Tables remain server-managed; browser clients must never receive the memory service key.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.saphira_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saphira_memory_owner_created
    ON public.saphira_memory (owner_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_saphira_memory_embedding_hnsw
    ON public.saphira_memory USING hnsw (embedding vector_cosine_ops)
    WHERE embedding IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.saphira_task_ledger (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saphira_task_ledger_owner_status_updated
    ON public.saphira_task_ledger (owner_id, status, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_saphira_task_ledger_agent_updated
    ON public.saphira_task_ledger (agent_name, updated_at DESC);

CREATE OR REPLACE FUNCTION public.saphira_set_task_ledger_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_saphira_task_ledger_updated_at ON public.saphira_task_ledger;
CREATE TRIGGER trg_saphira_task_ledger_updated_at
BEFORE UPDATE ON public.saphira_task_ledger
FOR EACH ROW
EXECUTE FUNCTION public.saphira_set_task_ledger_updated_at();

-- Defense in depth. No client-role policies are created; access is server-only.
ALTER TABLE public.saphira_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saphira_task_ledger ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.saphira_memory FROM anon, authenticated;
REVOKE ALL ON TABLE public.saphira_task_ledger FROM anon, authenticated;
REVOKE ALL ON FUNCTION public.saphira_set_task_ledger_updated_at() FROM PUBLIC, anon, authenticated;

-- Production API uses a server-side database connection. Do not expose the
-- DATABASE_URL or SAPHIRA_MEMORY_API_KEY to the browser.
