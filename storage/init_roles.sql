-- Run as PostgreSQL superuser during provisioning.
-- Credentials are intentionally NOT stored in source control. Inject passwords via your secret manager.
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='saphira_admin') THEN CREATE ROLE saphira_admin LOGIN; END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='saphira_runtime') THEN CREATE ROLE saphira_runtime LOGIN; END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='saphira_readonly') THEN CREATE ROLE saphira_readonly LOGIN; END IF;
END $$;

GRANT CONNECT ON DATABASE saphira_enterprise TO saphira_admin, saphira_runtime, saphira_readonly;
GRANT ALL ON SCHEMA public TO saphira_admin;
GRANT USAGE ON SCHEMA public TO saphira_runtime, saphira_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO saphira_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO saphira_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO saphira_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO saphira_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO saphira_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO saphira_readonly;

-- IMPORTANT: set LOGIN passwords outside Git, e.g. with ALTER ROLE in your secret-managed provisioning job.
