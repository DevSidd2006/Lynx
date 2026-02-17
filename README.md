# Lynx — AI Voice Dictation Assistant

A fast, privacy-first voice dictation system that turns speech into polished text. Powered by Groq's Whisper STT and LLaMA for instant transcription and context-aware rewriting.

**Hold a hotkey, speak, release — polished text appears at your cursor.**

## Features

- **Push-to-Talk Hotkey** — Global hotkey (default `Ctrl+Space`) records while held, transcribes on release
- **AI Rewriting** — Automatically rewrites raw transcription for tone and context (email, Slack, notes, docs)
- **Session Memory** — Maintains context across dictations within a session for consistent output
- **User Profile** — Custom dictionary, writing rules, preferred tone — the LLM adapts to your style
- **Web Dashboard** — Record, transcribe, rewrite, and manage history from the browser
- **Desktop App** — Tkinter GUI to manage services, edit config, and monitor health
- **System Tray** — Live recording indicator with state-aware icon
- **Voice Activity Detection** — Auto-stops recording after sustained silence
- **Visual Overlay** — Animated audio level bar during recording
- **Works Everywhere** — Types text directly into any focused app (Wayland + X11)

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│  Web UI     │───>│  FastAPI Backend  │───>│  Groq API   │
│  (browser)  │    │  (localhost)      │    │  (STT+LLM)  │
└─────────────┘    └──────────────────┘    └─────────────┘
                          ^
┌─────────────┐           │
│  Hotkey     │───────────┘
│  Daemon     │
│  (pynput)   │
└─────────────┘
```

| Component | Path | Purpose |
|-----------|------|---------|
| API Server | `app/` | FastAPI backend — transcription, rewriting, history, profile |
| Web UI | `web/` | Browser dashboard for recording and management |
| Hotkey Daemon | `scripts/lynx_daemon/` | Push-to-talk with overlay, tray, VAD |
| Desktop App | `desktop/` | Tkinter GUI for service management |
| Scripts | `scripts/` | Bootstrap, service install, launchers |

## Prerequisites

- **Python 3.10+**
- **Groq API key** — [Get one here](https://console.groq.com/)
- **Ubuntu 22.04+** (or similar Linux distro)
- System tools:
  - `arecord` (from `alsa-utils`) — audio recording
  - `wl-copy` + `wtype` (Wayland) **or** `xclip` + `xdotool` (X11) — clipboard & typing
  - `notify-send` — desktop notifications (optional)

```bash
# Ubuntu/Debian
sudo apt install alsa-utils wl-clipboard wtype libnotify-bin
# For X11 instead of Wayland:
# sudo apt install alsa-utils xclip xdotool libnotify-bin
```

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/lynx.git
cd lynx

# Setup
cp .env.example .env
# Edit .env and set your GROQ_API_KEY

./scripts/bootstrap.sh

# Start everything (API + hotkey daemon)
./scripts/start_all.sh
```

Open the web dashboard at **http://127.0.0.1:8080**

### Hotkey Daemon Only

```bash
source .venv/bin/activate
pip install -r requirements-hotkey.txt
python scripts/hotkey_push_to_talk.py
```

Hold `Ctrl+Space` to record, release to transcribe and paste.

### Run as systemd Service

```bash
./scripts/bootstrap.sh
source .venv/bin/activate
pip install -r requirements-hotkey.txt
./scripts/install_user_service.sh
```

Verify:
```bash
systemctl --user status lynx-api.service lynx-hotkey.service --no-pager
```

## Configuration

All settings are in `.env` (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Your Groq API key (required) |
| `GROQ_STT_MODEL` | `whisper-large-v3-turbo` | Speech-to-text model |
| `GROQ_TEXT_MODEL` | `llama-3.3-70b-versatile` | LLM for rewriting |
| `PORT` | `8080` | API server port |
| `WILLOW_HOTKEY` | `ctrl+space` | Global hotkey binding |
| `WILLOW_STYLE` | `professional` | Default writing style |
| `WILLOW_CONTEXT` | `email` | Default context (email/slack/notes/docs) |
| `WILLOW_LANGUAGE` | `en` | Transcription language |
| `WILLOW_AUTO_PASTE` | `true` | Auto-type text into active window |
| `WILLOW_INSERT_MODE` | `type` | How to insert text (`type` or `paste`) |
| `WILLOW_OVERLAY` | `true` | Show recording overlay |
| `WILLOW_VAD_ENABLED` | `true` | Auto-stop on silence |
| `WILLOW_VAD_SILENCE_TIMEOUT` | `3` | Seconds of silence before auto-stop |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/profile` | Get user profile |
| `PUT` | `/api/profile` | Update profile |
| `POST` | `/api/transcribe` | Upload audio, get transcription + rewrite |
| `POST` | `/api/rewrite` | Rewrite plain text |
| `GET` | `/api/history` | List transcription history |
| `GET` | `/api/settings` | Get app settings |
| `PUT` | `/api/settings` | Update a setting |
| `GET` | `/api/export` | Export all data as JSON |

## How Session Memory Works

Lynx feeds the last 5 dictations (from the same context, within 30 minutes) to the LLM as context. This means:

- Pronouns like "he" or "that project" resolve correctly across dictations
- Tone stays consistent when dictating a long email in parts
- Greetings and sign-offs aren't repeated
- Different contexts (email vs Slack) have separate memory

## Privacy

- All data is stored locally in SQLite (`data/lynx.db`)
- Audio and text are sent to Groq APIs using **your** API key
- No telemetry, no third-party tracking
- Configure data retention on your Groq account if needed

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Rewrite failed` / `Transcription failed` | Check `GROQ_API_KEY` and model names in `.env` |
| Browser mic denied | Allow microphone permissions for localhost |
| No clipboard integration | Install `wl-copy`/`wtype` (Wayland) or `xclip`/`xdotool` (X11) |
| Hotkey not working | Install `requirements-hotkey.txt` in `.venv` |
| Old clipboard text pasted | Ensure `WILLOW_INSERT_MODE=type` in `.env` |

## License

MIT
