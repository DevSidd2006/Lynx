#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Core bootstrap complete"
echo ""
echo "If you want global hotkey daemon:"
echo "  pip install -r requirements-hotkey.txt"
echo ""
echo "For system tray icon support on GNOME/Ubuntu:"
echo "  sudo apt install gir1.2-ayatanaappindicator3-0.1"
