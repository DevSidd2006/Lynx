#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x ".venv/bin/uvicorn" ]; then
  echo "Missing dependencies. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.env"
exec "$ROOT_DIR/.venv/bin/uvicorn" app.main:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8080}"
