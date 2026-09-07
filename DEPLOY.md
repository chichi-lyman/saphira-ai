# Saphira AI™ — Deployment Matrix

**Architected by Chelsea Megan Woods™**

## Canonical production topology

```text
Vercel Production Web / PWA
        |
        | SAPHIRA_API_URL (build-time)
        v
Railway Production FastAPI
        |
        +--> PostgreSQL / Supabase
        +--> Redis / Celery
        +--> AI providers
        +--> Stripe / commerce
        |
        +--> Android APK (SAPHIRA_BASE_URL)
        +--> Tauri Desktop (same API)
```

The canonical web client is `saphira-app/` (React + Vite). Vercel builds it into `saphira-app/dist`. The legacy root `public/` dashboard is no longer a production entrypoint.

Provider secrets stay server-side. Never place AI-provider, database, Redis, Stripe secret, or encryption keys in Vercel browser assets or native clients.

## 1. Railway backend

Railway uses `railway.json` and the repository Dockerfile. Set these variables in the Railway production service:

```text
ENVIRONMENT=production
PORT=8000
SAPHIRA_ALLOWED_ORIGINS=https://YOUR-VERCEL-DOMAIN.vercel.app,https://YOUR-CUSTOM-DOMAIN
OPENAI_API_KEY=...
GEMINI_API_KEY=...
DATABASE_URL=...
REDIS_URL=...
CELERY_BROKER_URL=...
CELERY_RESULT_BACKEND=...
SAPHIRA_JWT_SECRET=...
SAPHIRA_ENCRYPTION_KEY=...
SAPHIRA_ADMIN_AUDIT_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_PRICE_ID=...
STRIPE_WEBHOOK_SECRET=...
PRODUCTION_DOMAIN_URL=https://YOUR-VERCEL-DOMAIN.vercel.app
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
SAPHIRA_TTS_PROVIDER=elevenlabs
```

Use the public Railway service URL as the backend root:

```text
https://YOUR-RAILWAY-SERVICE.up.railway.app
```

The browser chat boundary is:

```text
https://YOUR-RAILWAY-SERVICE.up.railway.app/api/chat
```

Verify:

```bash
curl https://YOUR-RAILWAY-SERVICE.up.railway.app/
curl https://YOUR-RAILWAY-SERVICE.up.railway.app/health
```

Expected root status is `running`; `/health` must return `healthy`.

## 2. Vercel production web/PWA

Vercel builds the canonical React/Vite client with:

```text
buildCommand: cd saphira-app && npm install && npm run build
outputDirectory: saphira-app/dist
```

Set this Vercel Production environment variable:

```text
SAPHIRA_API_URL=https://YOUR-RAILWAY-SERVICE.up.railway.app/api
```

`vite.config.ts` reads `SAPHIRA_API_URL` during the production build and injects only the public API base URL into the browser bundle. The frontend then calls `/chat` against that base, producing the canonical `/api/chat` boundary.

Do not use the former Render endpoint. There is no Render fallback in the canonical build.

Also set:

```text
PRODUCTION_DOMAIN_URL=https://YOUR-VERCEL-DOMAIN.vercel.app
```

Redeploy Production after changing variables.

### PWA requirements

The Vite client includes:

- `/manifest.json`
- standalone display mode
- `#0B0813` theme/background
- service worker at `/sw.js`
- service-worker registration from `src/main.tsx`
- offline shell caching
- API requests explicitly excluded from service-worker caching

Install the production PWA from Chrome on Pixel or Chromebook after verifying HTTPS and the manifest/service worker in DevTools.

## 3. Frontend streaming

The canonical client uses `useSaphiraStream` → `streamChat` → `POST /api/chat` with `stream=true`.

The transport accepts SSE, JSON chunk, and raw text streaming formats and incrementally renders Saphira's response.

## 4. Android APK

GitHub Actions reads repository variable:

```text
SAPHIRA_BASE_URL=https://YOUR-RAILWAY-SERVICE.up.railway.app
```

The workflow rejects localhost/emulator URLs and builds `app-debug.apk` only against an HTTPS production backend.

Artifact:

```text
saphira-ai-apk/app-debug.apk
```

## 5. Stripe

Stripe checkout is exposed at:

```text
POST /api/v1/checkout/create-session
```

Webhook:

```text
POST /api/v1/billing/webhooks
```

Configure Stripe's webhook destination to the Railway backend and use the generated endpoint secret as `STRIPE_WEBHOOK_SECRET`.

## 6. Voice

Browser voice uses the Web Speech APIs. Server TTS uses the configured provider. Android has native speech recognition and Text-to-Speech support in the companion application.

## 7. Deployment acceptance test

A deployment is considered green only when all of these pass:

- Vercel Production deployment: completed
- Railway Production deployment: completed
- `GET /` on Railway: `status=running`
- `GET /health` on Railway: `status=healthy`
- Browser client reaches `POST /api/chat` on the configured Railway backend
- streaming response renders incrementally
- PWA manifest is valid
- service worker registers successfully
- API traffic is not cached by the service worker
- governance remains fail-closed for consequential actions
- Stripe checkout/webhook checks pass when billing is enabled
- Android workflow produces `app-debug.apk`
- APK points to the Railway HTTPS backend

## Ownership

© 2026 Chelsea Megan Woods™. All rights reserved.
