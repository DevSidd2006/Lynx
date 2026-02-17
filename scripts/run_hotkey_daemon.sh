#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing dependencies. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

exec "$ROOT_DIR/.venv/bin/python" scripts/hotkey_push_to_talk.py
