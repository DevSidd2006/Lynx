#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing dependencies. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

# Ensure display environment variables are set for both X11 and Wayland.
# This matters when the daemon is started from a systemd service or
# a background shell that may not inherit the desktop session env.

# DISPLAY: required by pynput (via Xlib) and Tkinter overlay
if [ -z "${DISPLAY:-}" ]; then
  # Try to find an active X/XWayland socket
  for _sock in /tmp/.X11-unix/X*; do
    if [ -S "$_sock" ]; then
      _disp=":${_sock##*X}"
      export DISPLAY="$_disp"
      break
    fi
  done
fi

# WAYLAND_DISPLAY: required by wl-copy, wtype, and Wayland clipboard tools
if [ -z "${WAYLAND_DISPLAY:-}" ] && [ -d "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}" ]; then
  _runtime="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
  for _ws in "$_runtime"/wayland-*; do
    if [ -S "$_ws" ]; then
      export WAYLAND_DISPLAY="$(basename "$_ws")"
      break
    fi
  done
fi

# XDG_RUNTIME_DIR is needed by wl-copy / wl-paste
if [ -z "${XDG_RUNTIME_DIR:-}" ]; then
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
fi

exec "$ROOT_DIR/.venv/bin/python" scripts/hotkey_push_to_talk.py
