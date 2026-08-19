#!/usr/bin/env bash
set -euo pipefail

API_URL="${SAPHIRA_API_URL:-https://saphira-ai.onrender.com/api}"
node -e 'const fs=require("fs"); const u=process.env.SAPHIRA_API_URL || "https://saphira-ai.onrender.com/api"; fs.writeFileSync("public/runtime-config.js", `window.SAPHIRA_API_URL=${JSON.stringify(u)};\n`);'
printf 'Saphira Vercel production build configured for %s\n' "$API_URL"
