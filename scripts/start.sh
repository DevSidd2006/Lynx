#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

exec uvicorn app.main:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8080}" --reload
