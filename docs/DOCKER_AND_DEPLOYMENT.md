# Docker & Deployment Notes

**Owner:** Chelsea Megan Woods  
**Status:** Initial packaging added 2026-10-19

---

## Files Added

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage ready, non-root, healthcheck, production-oriented |
| `docker-compose.yml` | Local/staging orchestration |
| `.dockerignore` | Keeps image lean and secrets out |

## Quick Start

```bash
# Build
docker build -t saphira-ai:latest .

# Run (requires .env with at least OPENAI_API_KEY, etc.)
docker compose up --build
```

## Health Endpoint

The container expects a `/health` route. If it does not yet exist, add a minimal one:

```python
@app.get("/health")
async def health():
    return {"status": "ok", "service": "saphira-ai"}
```

## Buyer / Due-Diligence Notes

- Image runs as non-root user `saphira`
- No secrets are baked in; everything comes from environment / `.env`
- Source can be volume-mounted for development; production images should be built without the dev volume mounts
- Future: add a `docker-compose.prod.yml` that also starts Postgres + Redis when multi-tenant ledger and rate limiting move to persistent stores

## Next Hardening Steps

- [ ] Confirm the exact ASGI import path (`src.api.main:app` or equivalent) and update CMD if needed
- [ ] Add a minimal `/health` endpoint if missing
- [ ] Optional: multi-stage build that produces a smaller runtime image
- [ ] Document required environment variables in `.env.example`

**Copyright © 2026 Chelsea Megan Woods**
