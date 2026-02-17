# Research Notes (Feb 14, 2026)

This clone is based on public Willow product positioning and Groq API capabilities as of February 14, 2026.

## Willow-style behavior to replicate

Observed public positioning:
- Fast dictation that turns raw speech into polished text.
- Context-aware rewrites for email/chat/docs.
- Voice commands and formatting cleanup.
- Works across apps and languages.
- Custom dictionary for names/jargon.

Implementation mapping in this project:
- `POST /api/transcribe`: low-latency STT + optional auto rewrite.
- `POST /api/rewrite`: style/context-based polishing.
- Profile memory: preferred tone, writing rules, custom dictionary.
- Ubuntu helper script to copy/paste dictated output into any app.

## Groq APIs used

- Speech-to-Text endpoint: `/openai/v1/audio/transcriptions`
- STT models: `whisper-large-v3-turbo` (default), `whisper-large-v3`
- Text-to-Speech endpoint: `/openai/v1/audio/speech`
- TTS model default: `canopylabs/orpheus-v1-english`
- Chat endpoint: `/openai/v1/chat/completions`

## Constraints and design decisions

- TTS text is capped to 200 chars for Orpheus compatibility.
- Persistent storage is SQLite for simple local deployment.
- Browser app is used for microphone capture and fast iteration.
- Ubuntu system integration is done with helper scripts (`arecord` + clipboard tools).

## Source links

- https://willowvoice.com/
- https://apps.apple.com/us/app/willow-ai-voice-dictation/id6753057525
- https://console.groq.com/docs/speech-to-text
- https://console.groq.com/docs/text-to-speech
- https://console.groq.com/docs/api-reference
