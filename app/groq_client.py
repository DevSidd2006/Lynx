from __future__ import annotations

from groq import Groq

from .config import settings
from .prompts import rewrite_system_prompt, rewrite_user_prompt


class GroqService:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        self.client = Groq(api_key=settings.groq_api_key)

    def transcribe_audio(self, filename: str, content: bytes, language: str, prompt: str = "") -> str:
        response = self.client.audio.transcriptions.create(
            file=(filename, content),
            model=settings.stt_model,
            language=language if language else None,
            prompt=prompt or None,
            response_format="json",
            temperature=0,
        )
        text = getattr(response, "text", "")
        return text.strip()

    def rewrite_text(
        self,
        text: str,
        profile: dict,
        style: str,
        context: str,
        language: str,
        history: list[dict] | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=settings.text_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": rewrite_system_prompt(profile, style, context, language, history)},
                {"role": "user", "content": rewrite_user_prompt(text)},
            ],
        )
        content = response.choices[0].message.content or ""
        return content.strip()
