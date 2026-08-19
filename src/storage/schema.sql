-- Saphira AI production commerce/persistence baseline
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS system_tenants (
    tenant_id VARCHAR(64) PRIMARY KEY,
    owner_name VARCHAR(128) NOT NULL,
    company_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tenant_subscriptions (
    subscription_id VARCHAR(128) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES system_tenants(tenant_id) ON DELETE CASCADE,
    customer_email VARCHAR(255) NOT NULL,
    stripe_customer_id VARCHAR(128) NOT NULL,
    account_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_period_end TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(stripe_customer_id)
);

CREATE TABLE IF NOT EXISTS stripe_processed_events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_leads_queue (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES system_tenants(tenant_id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    industry_category VARCHAR(128) NOT NULL,
    contact_phone VARCHAR(64),
    contact_email VARCHAR(255),
    website_url TEXT,
    enrichment_status VARCHAR(32) NOT NULL DEFAULT 'PENDING_REVIEW',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS god_memory_ledger (
    event_id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) REFERENCES system_tenants(tenant_id) ON DELETE CASCADE,
    layer_source VARCHAR(64) NOT NULL,
    node_name VARCHAR(128) NOT NULL,
    event_status VARCHAR(32) NOT NULL,
    context_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_tenant_status
    ON market_leads_queue(tenant_id, enrichment_status);
CREATE INDEX IF NOT EXISTS idx_memory_tenant_node
    ON god_memory_ledger(tenant_id, layer_source, node_name);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer
    ON tenant_subscriptions(stripe_customer_id);
