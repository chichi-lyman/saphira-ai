#!/usr/bin/env bash
set -euo pipefail

API_URL="${SAPHIRA_API_URL:-https://saphira-ai.onrender.com/api}"
printf 'window.SAPHIRA_API_URL=%s;\n' "$(python -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$API_URL")" > public/runtime-config.js
printf 'Saphira Vercel production build configured for %s\n' "$API_URL"
