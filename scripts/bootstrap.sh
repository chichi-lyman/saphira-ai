#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

log() { printf '\n[saphira-bootstrap] %s\n' "$*"; }
fail() { printf '\n[saphira-bootstrap] ERROR: %s\n' "$*" >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || fail "python3 is required."
command -v docker >/dev/null 2>&1 || fail "Docker is required."
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required."

log "Creating Saphira runtime directories."
mkdir -p storage/logs storage/data storage/data/approvals storage/seeds docs

if [[ ! -f .env ]]; then
  [[ -f .env.example ]] || fail ".env.example is missing."
  cp .env.example .env
  sentinel="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
  python3 - "$sentinel" <<'PY'
from pathlib import Path
import sys
p = Path('.env')
s = p.read_text(encoding='utf-8')
s = s.replace('SAPHIRA_SENTINEL_SECRET=\n', f'SAPHIRA_SENTINEL_SECRET={sys.argv[1]}\n')
p.write_text(s, encoding='utf-8')
PY
  log "Created .env from template and generated a local sentinel secret."
else
  log ".env already exists; leaving credentials untouched."
fi

log "Installing Python dependencies."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

log "Starting PostgreSQL, Redis, FastAPI, and Celery worker containers."
docker compose up -d --build

log "Checking service state."
docker compose ps

log "Checking FastAPI health endpoint."
python3 - <<'PY'
import time
import urllib.request

url = 'http://127.0.0.1:8000/health'
for _ in range(30):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                print('[saphira-bootstrap] FastAPI health: OK')
                break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit('[saphira-bootstrap] FastAPI health check failed; inspect: docker compose logs saphira-core')
PY

log "Saphira infrastructure is online."
printf '%s\n' \
  'Next: open http://localhost:8000/health' \
  'Worker logs: docker compose logs -f saphira-worker' \
  'Core logs: docker compose logs -f saphira-core'
