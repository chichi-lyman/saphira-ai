# Saphira AI — Deployment Matrix

**Architected by Chelsea Megan Woods**

## Canonical production topology

```text
Vercel Production Web
        |
        | SAPHIRA_API_URL
        v
Railway Production FastAPI
        |
        +--> PostgreSQL
        +--> Redis / Celery
        +--> AI providers
        +--> Stripe / commerce
        |
        +--> Android APK (SAPHIRA_BASE_URL)
```

Vercel serves the static production UI. Railway runs the FastAPI control plane. The Android app calls the same production FastAPI endpoint. Do not put provider secrets in Vercel static assets or the Android application.

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

Use the public Railway service URL as the backend base URL, for example:

```text
https://YOUR-RAILWAY-SERVICE.up.railway.app
```

Verify:

```bash
curl https://YOUR-RAILWAY-SERVICE.up.railway.app/
curl https://YOUR-RAILWAY-SERVICE.up.railway.app/health
```

Expected root status is `running`; `/health` must return `healthy`.

## 2. Vercel production

The repository deploys `public/` as a static site. Set the Vercel project environment variable:

```text
SAPHIRA_API_URL=https://YOUR-RAILWAY-SERVICE.up.railway.app/api
```

The Vercel build writes this value into `public/runtime-config.js`, so the browser never relies on the old Render endpoint unless the variable is omitted. The build retains a temporary Render fallback for backwards compatibility.

Also set:

```text
PRODUCTION_DOMAIN_URL=https://YOUR-VERCEL-DOMAIN.vercel.app
```

Redeploy Production after changing variables.

## 3. Android APK

GitHub Actions reads repository variable:

```text
SAPHIRA_BASE_URL=https://YOUR-RAILWAY-SERVICE.up.railway.app
```

The workflow rejects localhost/emulator URLs and builds `app-debug.apk` only against an HTTPS production backend.

Artifact:

```text
saphira-ai-apk/app-debug.apk
```

## 4. Stripe

Stripe checkout is exposed at:

```text
POST /api/v1/checkout/create-session
```

Webhook:

```text
POST /api/v1/billing/webhooks
```

Configure Stripe's webhook destination to the Railway backend and use the generated endpoint secret as `STRIPE_WEBHOOK_SECRET`.

## 5. Voice

Browser voice uses the Web Speech APIs. Server TTS uses the configured provider. Android has native speech recognition and Text-to-Speech support in the companion application.

## 6. Deployment acceptance test

A deployment is considered green only when all of these pass:

- Vercel Production deployment: completed
- Railway Production deployment: completed
- `GET /` on Railway: `status=running`
- `GET /health` on Railway: `status=healthy`
- Vercel chat reaches `POST /api/chat` on the configured backend
- Stripe checkout returns a hosted checkout session when billing secrets are configured
- Stripe webhook signature verification succeeds
- Android workflow produces `app-debug.apk`
- APK points to the Railway HTTPS backend

## Ownership

© 2026 Chelsea Megan Woods. All rights reserved.
