from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileModel(BaseModel):
    full_name: str = ""
    role: str = ""
    preferred_tone: str = "professional"
    default_language: str = "en"
    writing_rules: list[str] = Field(default_factory=list)
    custom_dictionary: list[str] = Field(default_factory=list)
    working_context: str = ""


class RewriteRequest(BaseModel):
    text: str
    style: str = "professional"
    context: str = "email"
    language: str = "en"


class RewriteResponse(BaseModel):
    original_text: str
    rewritten_text: str
    style: str
    context: str
    language: str


class DictateResponse(BaseModel):
    transcript: str
    rewritten_text: str
    style: str
    context: str
    language: str


class AppSettingModel(BaseModel):
    key: str
    value: str
