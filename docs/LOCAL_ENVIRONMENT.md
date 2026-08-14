# Local Environment Variable Management

Secrets and environment-specific settings are managed on the developer machine only. They must never be committed to the repository.

## Files and roles

| File | Location | Purpose | Committed? |
|------|----------|---------|------------|
| `.env.example` | Repository root | Template for backend / runtime variables | Yes |
| `.env` or `.env.local` | Repository root | Your real backend secrets for local runs | **No** |
| `saphira-app/.env.local.example` | Frontend app | Template for Vite client variables | Yes |
| `saphira-app/.env.local` | Frontend app | Your real frontend secrets | **No** |

Both root `.gitignore` and `saphira-app/.gitignore` exclude `.env`, `.env.local`, and related local env files.

## Automated generation

From the repository root:

```bash
chmod +x scripts/generate_local_env.sh   # once, if needed
./scripts/generate_local_env.sh
```

This creates:

- `.env` from `.env.example`
- `saphira-app/.env.local` from `saphira-app/.env.local.example`

Existing files are left unchanged unless you pass `--force` (a timestamped `.bak.*` backup is written first):

```bash
./scripts/generate_local_env.sh --force
```

Generate and validate in one step:

```bash
./scripts/generate_local_env.sh --validate
```

The script does **not** inject secrets. After generation, edit the local files and fill in only the values you need.

## Dotenv validation

Environment values are validated with **pydantic-settings** (`src/config/settings.py`).

### At application startup

`main.py` loads `.env` / `.env.local`, then calls `validate_environment()`. Invalid types or constraint violations abort process start so misconfiguration fails fast.

### Offline CLI

```bash
python scripts/validate_env.py
python scripts/validate_env.py --strict    # require at least one LLM provider key
python scripts/validate_env.py --json      # machine-readable report (no secret values)
```

The `/health` endpoint also returns a non-secret `config` summary derived from the same settings object.

Validated fields include (among others):

- `PORT` (1–65535)
- `ENVIRONMENT` / `LOG_LEVEL` (normalized enums)
- `SAPHIRA_ALLOWED_ORIGINS` (parsed to a list for CORS)
- Optional provider and commerce keys (presence reported; not required for minimal local boot)

## Backend (FastAPI / runtime)

```bash
# Manual alternative
cp .env.example .env
# Edit .env and set only the keys you need for local work
```

Minimum useful local set often includes:

- `PORT` (default `8000`)
- `SAPHIRA_ALLOWED_ORIGINS` (include `http://localhost:3000` for the Vite app)
- At least one provider key if the chat path requires it (`OPENAI_API_KEY`, `GEMINI_API_KEY`, or `XAI_API_KEY`)

## Frontend (saphira-app)

```bash
# Manual alternative
cd saphira-app
cp .env.local.example .env.local
# Edit .env.local
```

Required for typical local use:

- `VITE_SAPHIRA_API_BASE_URL=http://localhost:8000`
- `VITE_SAPHIRA_API_KEY` only if the backend expects a bearer token
- `VITE_SAPHIRA_MODEL` if you need a non-default model id

Vite embeds only variables that start with `VITE_` into the client bundle. Restart the dev server after changing `.env.local`.

## Security rules

1. Do not put production secrets in any local file that might be shared or backed up insecurely.
2. Prefer empty or dummy values in example files; never paste real keys into commits or pull requests.
3. If a secret is accidentally committed, rotate it immediately and remove it from history if required by policy.
4. Deployment platforms (Railway, Render, Kubernetes, etc.) should inject secrets as platform environment variables, not via committed files.

## Verification

```bash
# Confirm ignored status
git check-ignore -v .env .env.local saphira-app/.env.local

# Confirm example templates exist
ls -la .env.example saphira-app/.env.local.example

# Regenerate safely (no overwrite of existing secrets)
./scripts/generate_local_env.sh

# Validate types and presence summary
python scripts/validate_env.py
```

See also: `docs/SAPHIRA_ENVIRONMENT_CONTRACT.md` for the full deployment variable contract.
