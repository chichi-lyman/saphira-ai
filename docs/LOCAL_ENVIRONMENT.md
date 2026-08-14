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

The script does **not** inject secrets. After generation, edit the local files and fill in only the values you need.

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

Load is handled by the application (for example via `python-dotenv` / `load_dotenv()` in `main.py`).

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
# Confirm ignored status (should list .env / .env.local as ignored if present)
git check-ignore -v .env .env.local saphira-app/.env.local

# Confirm example templates exist
ls -la .env.example saphira-app/.env.local.example

# Regenerate safely (no overwrite of existing secrets)
./scripts/generate_local_env.sh
```

See also: `docs/SAPHIRA_ENVIRONMENT_CONTRACT.md` for the full deployment variable contract.
