#!/usr/bin/env bash
# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# One-step setup for Saphira AI (dev / local).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "==> Saphira AI setup"
echo "    Architect: Chelsea Megan Woods"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required." >&2
  exit 1
fi

PYTHON="${PYTHON:-python3}"

echo "==> Creating virtualenv (.venv)"
if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing requirements"
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "No requirements.txt found" >&2
  exit 1
fi

echo "==> Environment file"
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "    Created .env from .env.example — fill in API keys."
  else
    echo "    Warning: no .env.example"
  fi
else
  echo "    .env already exists (left unchanged)"
fi

mkdir -p models/wakeword

echo ""
echo "==> Done"
echo "    Activate:  source .venv/bin/activate"
echo "    Run API:   uvicorn main:app --reload"
echo "    Docs:      http://localhost:8000/docs"
echo "    Wake API:  POST /presence/wake"
echo "    Architecture: docs/ARCHITECTURE.md"
