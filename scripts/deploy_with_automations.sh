#!/usr/bin/env bash
# Copyright (c) 2026 Chelsea Megan Woods.
# Deploy Saphira AI backend to a cloud host and print automation wiring steps.
#
# Usage:
#   ./scripts/deploy_with_automations.sh railway   # default
#   ./scripts/deploy_with_automations.sh docker
#
# This script does NOT store secrets. It only documents and validates structure.

set -euo pipefail

TARGET="${1:-railway}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Saphira AI — Deploy + Automation wiring ==="
echo "Target: $TARGET"
echo "Repo root: $ROOT"
echo

check_file() {
  if [[ ! -f "$1" ]]; then
    echo "MISSING: $1"
    exit 1
  fi
  echo "OK: $1"
}

echo "-- Preflight --"
check_file "Dockerfile"
check_file "main.py"
check_file "src/services/webhook_bridge.py"
check_file "src/api/webhook_router.py"
check_file "src/resilience/circuit_breaker.py"
check_file "docs/INTEGRATION_WORKFLOWS.md"
echo

if [[ "$TARGET" == "railway" ]]; then
  echo "-- Railway path --"
  echo "1. Ensure railway CLI is logged in: railway login"
  echo "2. Link project: railway link"
  echo "3. Set variables (never commit real values):"
  cat <<'EOF'
     ENVIRONMENT=production
     PORT=8000
     SAPHIRA_ALLOWED_ORIGINS=https://YOUR-VERCEL-DOMAIN
     SAPHIRA_AUTOMATION_WEBHOOK_SECRET=generate-a-long-random-string
     ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/...
     MAKE_WEBHOOK_URL=https://hook.eu1.make.com/...
     N8N_CROSS_POST_WEBHOOK=https://...
     N8N_ONBOARDING_WEBHOOK=https://...
     N8N_REVENUE_WEBHOOK=https://...
     # plus existing provider / DB / Stripe keys from DEPLOY.md
EOF
  echo "4. Deploy: railway up  (or push to the connected GitHub branch)"
  echo "5. Verify:"
  echo "     curl https://YOUR-RAILWAY.up.railway.app/health"
  echo "     curl https://YOUR-RAILWAY.up.railway.app/api/webhooks/health"
  echo
elif [[ "$TARGET" == "docker" ]]; then
  echo "-- Local / VPS Docker path --"
  echo "Build:  docker build -t saphira-ai:latest -f Dockerfile ."
  echo "Run:    docker run --env-file .env -p 8000:8000 saphira-ai:latest"
  echo "Health: curl http://localhost:8000/health"
  echo
else
  echo "Unknown target: $TARGET (use railway|docker)"
  exit 1
fi

echo "-- Automation wiring (after backend is live) --"
cat <<'EOF'
Zapier:
  1. Create Zap → Webhooks by Zapier "Catch Hook" → copy URL into ZAPIER_WEBHOOK_URL
  2. Action: Google Sheets "Create Spreadsheet Row" for revenue tracker
  3. Optional reverse Zap: New Sheet Row → POST to /api/webhooks/inbound/revenue
     Header X-Saphira-Automation-Key = SAPHIRA_AUTOMATION_WEBHOOK_SECRET

Make.com:
  1. Custom webhook module → URL into MAKE_WEBHOOK_URL
  2. Map JSON fields → Google Sheets / Data store

n8n:
  1. Webhook node (production URL) → N8N_*_WEBHOOK vars
  2. Function / Set nodes to normalize payload
  3. Google Sheets or HTTP Request nodes as needed

See docs/INTEGRATION_WORKFLOWS.md for full payload shapes and security notes.
EOF

echo
echo "Done. Cloud server = where Saphira lives; integration workflows = bridges to other apps."
