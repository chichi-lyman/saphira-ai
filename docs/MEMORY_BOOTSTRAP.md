# Saphira AI semantic memory bootstrap

## What this adds

- PostgreSQL/pgvector storage for durable, per-user semantic memories.
- Cosine-similarity retrieval using 1536-dimensional embeddings from OpenAI `text-embedding-3-small`.
- An agent task ledger with status/result updates and automatic `updated_at`.
- Server-to-server API routes mounted below `/api/memory`.
- Fail-closed API-key authentication. The memory key must never be sent to browser or mobile clients.

## Required backend environment

Set these in the backend host (Render or another server), not in Vite/Vercel public variables:

- `DATABASE_URL`: PostgreSQL connection URL for the selected Saphira Supabase project.
- `OPENAI_API_KEY`: server-side key for embeddings.
- `SAPHIRA_MEMORY_API_KEY`: long random secret shared only by trusted backend services.
- `SAPHIRA_EMBEDDING_MODEL=text-embedding-3-small` (optional; output must remain 1536 dimensions).

Do not use the sample values from `.env.example` as production credentials. Keep `.env` untracked.

## Migration

Apply `storage/migrations/002_pgvector_memory_and_task_ledger.sql` to the intended Supabase project after confirming the project ID. It creates the `vector` extension, tables, indexes, trigger, and disables client-role access using RLS plus revoked grants. The migration is additive; it does not modify the existing chat or billing tables.

The migration must be applied to the same database referenced by the backend's `DATABASE_URL`. This repository is connected to more than one Supabase project, so do not guess which database is production.

## Endpoints

All endpoints require the `X-Saphira-Memory-Key` header.

- `GET /api/memory/health` — confirms the tables exist and the database is reachable.
- `POST /api/memory` — store a memory. JSON body: `owner_id`, `content`, optional `metadata`.
- `POST /api/memory/search` — semantic retrieval. JSON body: `owner_id`, `query`, optional `limit` (1–20).
- `POST /api/memory/tasks` — create an agent task ledger entry.
- `PATCH /api/memory/tasks/{task_id}` — update a task's `status` and/or `result`.

The caller must derive `owner_id` from a verified authenticated user identity on the trusted server. Never accept a browser-supplied owner ID as proof of identity. Do not expose the shared API key to clients.

## Verification checklist

1. Apply the migration to the chosen project.
2. Set the three required backend environment variables.
3. Deploy the backend.
4. Call `GET /api/memory/health` with the server-to-server key.
5. Store a test memory for a test user and search for it semantically.
6. Run the repository test suite and inspect the deployment logs.
7. Run Supabase security and performance advisors.

## Current limitations

This bootstrap exposes the persistence primitives; it does not automatically migrate old JSON-file history into pgvector, nor does it yet replace every existing call to the JSON-backed `persistent_memory` store. That integration should be a separate migration so existing chat behavior is not silently changed.
