-- Saphira Enterprise marketplace + licensing schema
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS agent_marketplace (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_did VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(128) NOT NULL,
  description TEXT NOT NULL,
  creator_id VARCHAR(128) NOT NULL,
  category VARCHAR(64) NOT NULL,
  pricing_model VARCHAR(32) NOT NULL CHECK (pricing_model IN ('FREE','FLAT_MONTHLY','PER_EXECUTION','USAGE_BASED')),
  subscription_price_usd NUMERIC(18,6) NOT NULL DEFAULT 0,
  version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  stripe_meter_event_name VARCHAR(128),
  rating NUMERIC(3,2) NOT NULL DEFAULT 5.00,
  total_installs INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_installations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(128) NOT NULL,
  agent_did VARCHAR(255) NOT NULL REFERENCES agent_marketplace(agent_did) ON DELETE CASCADE,
  installed_version VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL CHECK (status IN ('ACTIVE','SUSPENDED','UNINSTALLED')),
  config_overrides JSONB NOT NULL DEFAULT '{}'::jsonb,
  installed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (tenant_id, agent_did)
);

ALTER TABLE agent_installations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation_agent_installations ON agent_installations;
CREATE POLICY tenant_isolation_agent_installations ON agent_installations
  USING (tenant_id = current_setting('app.current_tenant', true))
  WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE TABLE IF NOT EXISTS tenant_customers (
  tenant_id VARCHAR(128) PRIMARY KEY,
  stripe_customer_id VARCHAR(255) UNIQUE NOT NULL,
  payment_method_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_marketplace_category ON agent_marketplace(category);
CREATE INDEX IF NOT EXISTS idx_installations_tenant ON agent_installations(tenant_id, status);
