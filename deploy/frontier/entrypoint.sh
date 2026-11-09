#!/usr/bin/env bash
# © 2026 Chelsea Megan Woods · Nova Umbrella
set -eo pipefail

echo "=========================================================="
echo " Booting Saphira AI Memory & Formal Verification Server"
echo " Node ID: ${SAPHIRA_NODE_ID:-saphira-core-prod-01}"
echo " System Time: $(date -u)"
echo "=========================================================="

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export WORKERS="${WORKERS:-2}"
export LOG_LEVEL="${LOG_LEVEL:-info}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"

if [ "${WAIT_FOR_PG:-}" = "true" ]; then
  echo "[+] Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
  while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do sleep 0.5; done
  echo "[+] PostgreSQL ready."
fi

echo "[+] Pre-flight imports..."
python -c "
import sympy as sp
from z3 import Solver
print('SymPy + Z3 OK')
" || echo "Warning: optional solvers missing"

echo "[+] Launching on ${HOST}:${PORT} workers=${WORKERS}"
# Module path when image copies src/frontier layout
if python -c "import src.frontier.memory.saphira_olora_memory" 2>/dev/null; then
  APP_MODULE="src.frontier.memory.saphira_olora_memory:app"
elif python -c "import saphira_olora_memory" 2>/dev/null; then
  APP_MODULE="saphira_olora_memory:app"
else
  echo "Cannot locate saphira_olora_memory app module" >&2
  exit 1
fi

exec gunicorn "$APP_MODULE" \
  --workers "${WORKERS}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "${HOST}:${PORT}" \
  --log-level "${LOG_LEVEL}" \
  --access-logfile - \
  --error-logfile - \
  --keep-alive 65 \
  --graceful-timeout 30
