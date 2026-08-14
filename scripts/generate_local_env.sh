#!/usr/bin/env bash
# =============================================================================
# Saphira AI — Generate local environment files from committed templates
# =============================================================================
# Usage:
#   ./scripts/generate_local_env.sh              # create missing files only
#   ./scripts/generate_local_env.sh --force      # overwrite existing local env files
#   ./scripts/generate_local_env.sh --validate   # run validate_env.py after generation
#   ./scripts/generate_local_env.sh --force --validate
#   ./scripts/generate_local_env.sh --help
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORCE=0
VALIDATE=0

usage() {
  cat <<'EOF'
Saphira AI — local environment file generator

Usage:
  ./scripts/generate_local_env.sh [options]

Options:
  --force      Overwrite existing .env and saphira-app/.env.local
  --validate   Run scripts/validate_env.py after generation
  -h, --help   Show this help

Behavior:
  - Copies .env.example -> .env if missing (or with --force)
  - Copies saphira-app/.env.local.example -> saphira-app/.env.local if missing (or with --force)
  - Does not inject secrets; edit generated files locally
  - Generated files remain gitignored
  - With --validate, loads dotenv and reports type/presence status (non-strict)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=1
      shift
      ;;
    --validate)
      VALIDATE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

copy_template() {
  local src="$1"
  local dest="$2"
  local label="$3"

  if [[ ! -f "$src" ]]; then
    echo "ERROR: Template not found: $src" >&2
    return 1
  fi

  if [[ -f "$dest" && "$FORCE" -ne 1 ]]; then
    echo "SKIP  $label (already exists: $dest)"
    echo "      Use --force to overwrite."
    return 0
  fi

  if [[ -f "$dest" && "$FORCE" -eq 1 ]]; then
    local backup="${dest}.bak.$(date +%Y%m%d%H%M%S)"
    cp "$dest" "$backup"
    echo "BACKUP $dest -> $backup"
  fi

  cp "$src" "$dest"
  echo "CREATE $dest  (from $(basename "$src"))"
}

echo "Saphira AI — generating local environment files"
echo "Root: $ROOT_DIR"
echo

copy_template \
  "$ROOT_DIR/.env.example" \
  "$ROOT_DIR/.env" \
  "backend .env"

if [[ -d "$ROOT_DIR/saphira-app" ]]; then
  copy_template \
    "$ROOT_DIR/saphira-app/.env.local.example" \
    "$ROOT_DIR/saphira-app/.env.local" \
    "frontend .env.local"
else
  echo "SKIP  saphira-app/ not present; frontend env not generated"
fi

echo
if [[ "$VALIDATE" -eq 1 ]]; then
  echo "Running environment validation..."
  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT_DIR/scripts/validate_env.py" || {
      echo "Validation reported issues (see above). Edit .env and re-run with --validate." >&2
      exit 1
    }
  else
    echo "WARNING: python3 not found; skip validation" >&2
  fi
  echo
fi

echo "Next steps:"
echo "  1. Edit .env and set provider keys / local settings as needed."
echo "  2. Edit saphira-app/.env.local (VITE_* values) if using the web app."
echo "  3. Validate: python scripts/validate_env.py   (add --strict if required)"
echo "  4. Restart backend and 'npm run dev' in saphira-app after changes."
echo "  5. Confirm ignore: git check-ignore -v .env saphira-app/.env.local"
echo
echo "Done."
