# Lynx (Ubuntu + Groq)

A complete local system that replicates core high-performance dictation flows:
- speech-to-text dictation
- instant rewrite for email/chat/docs tone
- profile-aware output (dictionary + writing rules)
- Ubuntu helper script for clipboard/paste workflow

## 1) Prerequisites

- Ubuntu 22.04+ (or similar)
- Python 3.10+
- Groq API key
- Optional Ubuntu tools for system integration:
  - `arecord` (`alsa-utils`)
  - `jq`
  - `wl-copy` (Wayland) or `xclip` (X11)
  - `wtype` (Wayland auto-paste at cursor) or `xdotool` (X11 auto-paste at cursor)

## 2) Setup

```bash
cd /home/devsidd/willow-groq-clone
cp .env.example .env
# edit .env and set GROQ_API_KEY
./scripts/start.sh
```

Open:
- `http://127.0.0.1:18080`

## 2.2) Desktop application (native Ubuntu window)

Run:

```bash
cd /home/devsidd/willow-groq-clone
./scripts/bootstrap.sh
./scripts/run_desktop_app.sh
```

Install app launcher in Ubuntu app menu:

```bash
cd /home/devsidd/willow-groq-clone
./scripts/install_desktop_shortcut.sh
```

The desktop app provides:
- Start/stop local API + hotkey daemon
- Install/restart user services
- Edit and save `.env` settings
- Open web UI directly
- Live API health indicator

## 2.1) Production rollout (recommended)

```bash
cd /home/devsidd/willow-groq-clone
./scripts/bootstrap.sh
source .venv/bin/activate
pip install -r requirements-hotkey.txt
./scripts/install_user_service.sh
```

Verify services:

```bash
systemctl --user status willow-groq-clone-api.service willow-groq-clone-hotkey.service --no-pager
```

## 3) Key API routes

- `GET /api/health`
- `GET /api/profile`
- `PUT /api/profile`
- `POST /api/transcribe` (multipart audio)
- `POST /api/rewrite`
- `GET /api/history`
- `GET /api/export`

## 4) Ubuntu “works anywhere” flow

This script records, transcribes, rewrites, and copies result to your clipboard:

```bash
chmod +x scripts/ubuntu_hotkey_dictate.sh
./scripts/ubuntu_hotkey_dictate.sh
```

Bind it to a custom keyboard shortcut in Ubuntu settings for one-key dictation.

## 4.1) Real push-to-talk (press to start, release to stop)

This daemon gives high-performance Lynx behavior:
- Hold hotkey: recording starts
- Release hotkey: recording stops, transcribe + rewrite runs, text is copied and optionally pasted

```bash
cd /home/devsidd/willow-groq-clone
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-hotkey.txt
python scripts/hotkey_push_to_talk.py
```

Hotkey and behavior are configurable in `.env`:
- `WILLOW_HOTKEY=ctrl+space`
- `WILLOW_AUTO_PASTE=true`
- `WILLOW_INSERT_MODE=paste` (`paste` or `type`)
- `WILLOW_OVERLAY=true` (small rectangular live voice indicator during recording)
- `WILLOW_STYLE=professional`
- `WILLOW_CONTEXT=email`
- `WILLOW_LANGUAGE=en`

For true “insert at current cursor everywhere” behavior:
- On Wayland install: `wl-clipboard` and `wtype`
- On X11 install: `xclip` and `xdotool`

## 4.2) Run as user service (optional)

```bash
cd /home/devsidd/willow-groq-clone
./scripts/bootstrap.sh
source .venv/bin/activate
pip install -r requirements-hotkey.txt
./scripts/install_user_service.sh
```

## 5) Security and privacy notes

- Data is stored locally in SQLite: `data/willow_clone.db`.
- Your audio/text is sent to Groq APIs using your key.
- If you need zero retention/enterprise guarantees, configure that on your Groq account and infra side.

## 6) Troubleshooting

- `Rewrite failed` / `Transcription failed`: verify `GROQ_API_KEY` and model names in `.env`.
- Browser mic denied: allow microphone permissions for localhost.
- No clipboard integration: install `wl-copy` or `xclip`.
- Hotkey service not starting: install `requirements-hotkey.txt` in `.venv`.

## 7) Research basis

See `docs/research.md` for the product and API research used to shape this clone.
