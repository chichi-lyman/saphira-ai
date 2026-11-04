# Saphira AI — Environment Contract

Secrets are injected by the deployment platform. Never commit secret values.

## Core

- `API_HOST`
- `API_PORT`
- `SAPHIRA_ALLOWED_ORIGINS`
- `ENVIRONMENT`
- `LOG_LEVEL`

## Persistence

- `DATABASE_URL`
- `REDIS_URL`
- `MEMORY_BACKEND`
- `MEMORY_TTL`

## AI / multimodal

- `OPENAI_API_KEY` or deployment-specific provider credentials
- `SAPHIRA_MODEL`
- `SAPHIRA_REASONING_MODEL`
- `SAPHIRA_VISION_MODEL`
- `SAPHIRA_TTS_VOICE`
- `SAPHIRA_WAKE_WORD_ENABLED`

## Commerce / billing

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SHOPIFY_SHOP_DOMAIN`
- `SHOPIFY_ACCESS_TOKEN`

## Integrations

- `GITHUB_TOKEN`
- `CRM_BASE_URL`
- `CRM_ACCESS_TOKEN`
- `COMMUNICATIONS_PROVIDER_KEY`
- `CALENDAR_PROVIDER_KEY`

## Identity and security

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY` (server-side token validation)
- `SAPHIRA_ENCRYPTION_KEY` (temporary server-only credential-vault encryption key; migrate to managed secret storage/KMS before production scale)

Supabase Auth owns user passwords and sessions. The application does not use a custom user JWT secret or a client-held master signing key.

## Device / realtime

- `SAPHIRA_WS_URL`
- `SAPHIRA_DEVICE_GATEWAY_URL`
- `SAPHIRA_DEVICE_SHARED_SECRET`

Values are deployment-specific. An environment variable being defined does not mean the corresponding integration is connected; the plugin registry and health checks must report actual availability.
