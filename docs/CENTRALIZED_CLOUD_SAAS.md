# Saphira AI — Centralized Cloud SaaS Architecture

## Decision

Saphira AI is a centrally hosted SaaS. Web, PWA, Android, iOS, and desktop clients are authenticated interfaces; they do not host the core runtime, agent network, or user database. Supabase Auth is the identity/session provider. FastAPI validates every bearer token against Supabase Auth before accepting user-scoped API requests.

## Production topology

- Web/PWA: Vercel-hosted React/Vite application.
- Identity: Supabase Auth (email/password, verified email, password recovery, optional OAuth, provider-managed MFA).
- Data: Supabase Postgres with RLS on every exposed table; Supabase Storage private user folders.
- API: FastAPI; resolves identity server-side from the Supabase Auth user endpoint.
- Agents/workers: cloud workers with server-only service credentials and task-scoped grants; never trust caller-supplied user IDs or roles.
- AI gateway: provider-neutral model routing with quotas, retries, timeouts, circuit breakers, and usage metering.
- Billing: Stripe webhooks update server-owned subscription entitlements idempotently.
- Operations: centralized logs, alerts, backups, restore tests, dependency scanning, and CI.

## Identity and authorization

1. Supabase Auth owns account creation, password verification, email confirmation, session refresh, and session revocation.
2. Frontend receives only the Supabase publishable key. No service-role key, provider secret, or shared backend API key is shipped in a browser bundle.
3. FastAPI validates bearer tokens with Supabase Auth and creates a trusted request principal.
4. Role and subscription data are server-managed. User-editable metadata and request-body roles are never authorization sources.
5. RLS scopes user-owned rows by auth.uid(). Privileged roles have no client-side write policy.
6. The initial operator/master-admin role must be provisioned by a controlled backend/admin process after the account exists. Public registration cannot assign it.
7. Agent workers receive short-lived, task-scoped permissions from the backend and cannot expand their own scope.

## Data model

auth.users is the identity source. Application tables reference its UUID:
- profiles, user_preferences, user_roles
- conversations, conversation_members, messages, conversation_summaries
- saphira_memory, saphira_task_ledger, agent_tasks, agent_task_events
- user_subscriptions, integrations, usage_events, audit_events

Secrets belong in provider-managed secret storage, not JSON preferences, integration metadata, or browser configuration. Audit events are backend-written and not user-editable.

## Superseded design

The application no longer requires a client-held master key, local keypair, Ed25519 command signature, custom master-command signing gateway, or custom password/session implementation. Remove those components only after checking all imports and runtime entry points. Standard cloud TLS, managed encryption at rest, secure server-side secret storage, MFA, RBAC, RLS, rate limiting, audit logging, backups, and incident response remain mandatory.

## Deployment variables

### Web build (public)
- VITE_SUPABASE_URL
- VITE_SUPABASE_PUBLISHABLE_KEY
- VITE_SAPHIRA_API_BASE_URL

### FastAPI backend (server only)
- SUPABASE_URL
- SUPABASE_PUBLISHABLE_KEY (or legacy SUPABASE_ANON_KEY for compatibility)
- DATABASE_URL
- SUPABASE_SERVICE_ROLE_KEY only if a backend operation genuinely requires elevated database access
- Existing provider, Redis/Celery, Stripe, and observability secrets as required

Never prefix a secret with VITE_ or NEXT_PUBLIC_.

## Rollout and acceptance checklist

- [x] Repository and current database projects inspected.
- [x] Centralized-cloud architecture documented in this branch.
- [x] Supabase Auth client and sign-in, sign-up, reset, and sign-out flows added in this branch.
- [x] FastAPI bearer-token validation added and applied to the primary chat endpoint in this branch.
- [x] Browser static API-key transport removed from the chat client in this branch.
- [x] SQL schema/RLS migration drafted for review in this branch.
- [ ] Confirm the authoritative Supabase project before applying schema changes.
- [ ] Apply reviewed migration; run security/performance advisors and RLS cross-user tests.
- [ ] Configure Supabase Auth email verification, password reset redirect allowlist, session policy, and optional OAuth/MFA.
- [ ] Set Vercel public build variables and backend server-only variables.
- [ ] Wire persistent conversations, messages, memory, and task events to authenticated user IDs.
- [ ] Complete authorization on every API router, websocket, webhook, scheduler, worker, and agent execution path.
- [ ] Add subscription webhook entitlement sync, usage quotas, account suspension/deletion, and retention workflows.
- [ ] Configure cloud workers, Redis, monitoring, alerting, backup, and restore verification.
- [ ] Resolve existing Vercel production build failure and verify CI.
- [ ] Run staging end-to-end tests for registration, verification, login, refresh, logout, reset, cross-user isolation, role escalation denial, billing webhook idempotency, and provider outage recovery.
- [ ] Complete privacy/terms review and Google Play/App Store submission requirements.

Checked items above are code/documentation changes in this branch, not proof of production deployment. Unchecked items require infrastructure access, project selection, provider credentials, or additional runtime integration and must not be marked complete until verified.
