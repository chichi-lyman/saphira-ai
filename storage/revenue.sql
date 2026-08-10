-- Revenue and audit ledger support
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS agent_revenue_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(128) NOT NULL,
  agent_did VARCHAR(255) NOT NULL,
  creator_id VARCHAR(128) NOT NULL,
  execution_id UUID NOT NULL,
  gross_amount_usd NUMERIC(18,6) NOT NULL CHECK (gross_amount_usd >= 0),
  platform_fee_usd NUMERIC(18,6) NOT NULL CHECK (platform_fee_usd >= 0),
  creator_payout_usd NUMERIC(18,6) NOT NULL CHECK (creator_payout_usd >= 0),
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',
  status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','SETTLED','DISPUTED','REFUNDED')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(128) NOT NULL,
  actor_did VARCHAR(255) NOT NULL,
  action VARCHAR(255) NOT NULL,
  resource TEXT NOT NULL,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  ip_address INET,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE agent_revenue_transactions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation_revenue ON agent_revenue_transactions;
CREATE POLICY tenant_isolation_revenue ON agent_revenue_transactions
  USING (tenant_id = current_setting('app.current_tenant', true))
  WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation_audit ON audit_events;
CREATE POLICY tenant_isolation_audit ON audit_events
  USING (tenant_id = current_setting('app.current_tenant', true))
  WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE INDEX IF NOT EXISTS idx_revenue_creator ON agent_revenue_transactions(creator_id, status);
CREATE INDEX IF NOT EXISTS idx_revenue_agent ON agent_revenue_transactions(agent_did, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_created ON audit_events(tenant_id, created_at DESC);
