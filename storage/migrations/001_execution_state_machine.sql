-- Saphira transactional execution truth.
-- PostgreSQL is the authoritative state store for consequential operations.

CREATE TYPE saphira_execution_state AS ENUM (
  'proposed', 'validated', 'authorized', 'reserved', 'executing', 'verifying',
  'committed', 'validation_failed', 'authorization_denied', 'reservation_failed',
  'execution_failed', 'verification_failed', 'rolled_back', 'reconciliation_required'
);

CREATE TABLE IF NOT EXISTS saphira_executions (
  execution_id UUID PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  conversation_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  parent_execution_id UUID NULL REFERENCES saphira_executions(execution_id),
  actor_id TEXT NOT NULL,
  tool TEXT,
  operation TEXT,
  arguments_hash TEXT,
  idempotency_key TEXT NOT NULL,
  state saphira_execution_state NOT NULL DEFAULT 'proposed',
  policy_decision TEXT NOT NULL,
  approval_id TEXT,
  result_hash TEXT,
  error_code TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_saphira_exec_tenant_created
  ON saphira_executions (tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saphira_exec_context
  ON saphira_executions (tenant_id, user_id, conversation_id, task_id);
CREATE INDEX IF NOT EXISTS idx_saphira_exec_state
  ON saphira_executions (state);

CREATE TABLE IF NOT EXISTS saphira_execution_events (
  event_id BIGSERIAL PRIMARY KEY,
  execution_id UUID NOT NULL REFERENCES saphira_executions(execution_id),
  tenant_id TEXT NOT NULL,
  from_state saphira_execution_state,
  to_state saphira_execution_state NOT NULL,
  event_type TEXT NOT NULL,
  evidence_hash TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_saphira_events_execution
  ON saphira_execution_events (execution_id, created_at);
CREATE INDEX IF NOT EXISTS idx_saphira_events_tenant
  ON saphira_execution_events (tenant_id, created_at DESC);

-- Defense-in-depth: PostgreSQL row-level security must be enabled in production
-- with the application setting app.tenant_id per transaction.
ALTER TABLE saphira_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE saphira_execution_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY saphira_execution_tenant_isolation ON saphira_executions
  USING (tenant_id = current_setting('app.tenant_id', true));

CREATE POLICY saphira_event_tenant_isolation ON saphira_execution_events
  USING (tenant_id = current_setting('app.tenant_id', true));
