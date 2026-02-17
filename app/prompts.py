from __future__ import annotations

from typing import Iterable


def _bullet_lines(items: Iterable[str]) -> str:
    clean = [item.strip() for item in items if item.strip()]
    if not clean:
        return "- None"
    return "\n".join(f"- {item}" for item in clean)


def rewrite_system_prompt(profile: dict, style: str, context: str, language: str, history: list[dict] | None = None) -> str:
    dictionary_terms = _bullet_lines(profile.get("custom_dictionary", []))
    writing_rules = _bullet_lines(profile.get("writing_rules", []))
    working_context = profile.get("working_context", "").strip()
    
    history_str = ""
    if history:
        history_lines = []
        for entry in reversed(history):  # Oldest to newest
            dictated = entry.get("source_text", "")
            polished = entry.get("rewritten_text", "")
            history_lines.append(f"[dictated]: {dictated}\n[polished]: {polished}")
        history_str = (
            "\nSession Memory (recent dictations in this context, oldest first):\n"
            + "\n---\n".join(history_lines)
            + "\n"
        )

    working_context_str = f"Current Working Context:\n{working_context}\n" if working_context else ""

    return f"""
You are Lynx, a writing assistant focused on dictation cleanup.

Rules:
1) Keep user intent unchanged.
2) Preserve names and terms in Custom Dictionary exactly as provided.
3) Apply clean punctuation, sentence boundaries, and readability.
4) Never invent facts.
5) Output only rewritten text in {language}.
6) The Session Memory below contains recent dictations from this session. Use it to:
   - Maintain consistent tone and vocabulary across the session.
   - Resolve ambiguous pronouns (e.g. "he", "that project") from prior context.
   - Avoid repeating greetings or sign-offs if the user already dictated one.
   - Recognise when the user is continuing a thought vs starting a new one.

User profile:
- Name: {profile.get("full_name", "")}
- Role: {profile.get("role", "")}
- Preferred tone: {profile.get("preferred_tone", "professional")}

Custom Dictionary:
{dictionary_terms}

Additional writing rules:
{writing_rules}

Target style: {style}
Target context: {context}
{working_context_str}
{history_str}
""".strip()


def rewrite_user_prompt(text: str) -> str:
    return f"Rewrite this dictated text:\n\n{text.strip()}"
