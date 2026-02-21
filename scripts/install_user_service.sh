#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$HOME/.config/systemd/user"
API_SERVICE_FILE="$SERVICE_DIR/willow-groq-clone-api.service"
HOTKEY_SERVICE_FILE="$SERVICE_DIR/willow-groq-clone-hotkey.service"
ENABLE_HOTKEY_SERVICE="${ENABLE_HOTKEY_SERVICE:-true}"

if [ ! -f "$ROOT_DIR/.env" ]; then
  echo "Missing $ROOT_DIR/.env" >&2
  exit 1
fi

mkdir -p "$SERVICE_DIR"

cat > "$API_SERVICE_FILE" <<EOD
[Unit]
Description=Lynx API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ROOT_DIR
EnvironmentFile=$ROOT_DIR/.env
ExecStart=$ROOT_DIR/scripts/start_prod.sh
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
EOD

cat > "$HOTKEY_SERVICE_FILE" <<EOD
[Unit]
Description=Lynx Hotkey Daemon
After=willow-groq-clone-api.service graphical-session.target
Requires=willow-groq-clone-api.service
PartOf=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$ROOT_DIR
EnvironmentFile=$ROOT_DIR/.env
ExecStart=$ROOT_DIR/scripts/run_hotkey_daemon.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOD

HAS_PYNPUT=0
if "$ROOT_DIR/.venv/bin/python" -c "import pynput" >/dev/null 2>&1; then
  HAS_PYNPUT=1
fi

systemctl --user daemon-reload
systemctl --user enable willow-groq-clone-api.service
systemctl --user restart willow-groq-clone-api.service

if [ "$ENABLE_HOTKEY_SERVICE" = "true" ] && [ "$HAS_PYNPUT" -eq 1 ]; then
  systemctl --user enable willow-groq-clone-hotkey.service
  systemctl --user restart willow-groq-clone-hotkey.service
  HOTKEY_STATUS="enabled"
else
  systemctl --user disable willow-groq-clone-hotkey.service >/dev/null 2>&1 || true
  systemctl --user stop willow-groq-clone-hotkey.service >/dev/null 2>&1 || true
  HOTKEY_STATUS="skipped (install requirements-hotkey.txt to enable)"
fi

echo "Services installed and started."
echo "API service: enabled"
echo "Hotkey service: $HOTKEY_STATUS"
echo "Check: systemctl --user status willow-groq-clone-api.service --no-pager"
