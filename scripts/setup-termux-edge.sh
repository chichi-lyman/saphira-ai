#!/usr/bin/env bash
# Saphira AI Edge Setup — Termux / Debian-on-Android
# © 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella
set -euo pipefail

echo "=========================================================="
echo " Saphira AI & Nova Umbrella Edge Deployment"
echo " Target: Android / Termux"
echo "=========================================================="

echo "[+] Step 1/5: Packages..."
pkg update -y && pkg upgrade -y
pkg install -y python python-pip git clang make cmake \
  libjpeg-turbo libpng postgresql libxml2 libxslt 2>/dev/null || true

export SAPHIRA_HOME="${SAPHIRA_HOME:-$HOME/saphira-ai}"
mkdir -p "$SAPHIRA_HOME"/{config,logs,models,src/edge}
cd "$SAPHIRA_HOME"

echo "[+] Step 2/5: Virtualenv..."
python -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pydantic numpy asyncpg requests redis websockets sympy 2>/dev/null || \
  pip install fastapi uvicorn pydantic numpy requests

echo "[+] Step 3/5: Optional local Postgres / pgvector..."
if command -v initdb >/dev/null 2>&1; then
  if [ ! -d "$HOME/postgres_data" ]; then
    initdb "$HOME/postgres_data" || true
  fi
  if ! pg_ctl -D "$HOME/postgres_data" status >/dev/null 2>&1; then
    pg_ctl -D "$HOME/postgres_data" -l "$HOME/postgres_data/server.log" start || true
    sleep 2
  fi
  createdb saphira_edge_db 2>/dev/null || true
  psql -d saphira_edge_db -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
else
  echo "  (postgres not available — skipping local ledger)"
fi

echo "[+] Step 4/5: Edge runner..."
cat > "$SAPHIRA_HOME/run_edge.sh" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
source "$HOME/saphira-ai/venv/bin/activate"
export PYTHONPATH="${PYTHONPATH:-}:$HOME/saphira-ai"
echo "Starting Saphira Edge on 127.0.0.1:8000..."
# Prefer monorepo module path when present
if [ -f "$HOME/saphira-ai/src/frontier/memory/saphira_olora_memory.py" ]; then
  uvicorn src.frontier.memory.saphira_olora_memory:app --host 127.0.0.1 --port 8000 --log-level info &
elif [ -f "$HOME/saphira-ai/saphira_olora_memory.py" ]; then
  uvicorn saphira_olora_memory:app --host 127.0.0.1 --port 8000 --log-level info &
else
  echo "No saphira_olora_memory module found — clone monorepo into $HOME/saphira-ai"
  exit 1
fi
if command -v termux-wake-lock >/dev/null 2>&1; then
  termux-wake-lock
  echo "Termux wake-lock acquired."
fi
wait
EOF
chmod +x "$SAPHIRA_HOME/run_edge.sh"

echo "[+] Step 5/5: Done."
echo "=========================================================="
echo " Run:  $SAPHIRA_HOME/run_edge.sh"
echo "=========================================================="
