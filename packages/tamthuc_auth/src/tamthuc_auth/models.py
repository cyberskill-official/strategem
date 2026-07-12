"""User / profile / token response models. birth_data never appears on public responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class BirthData(BaseModel):
    """Plaintext birth data — only in memory / crypto boundary, never in responses."""

    model_config = ConfigDict(extra="forbid")
    date: str
    time: str | None = None
    place: str | None = None
    tz: str | None = None
    kinh_do: float | None = None


class UserRecord(BaseModel):
    """Internal user row (may hold encrypted birth envelope)."""

    model_config = ConfigDict(extra="forbid")
    id: UUID
    email: str
    password_hash: str | None = None
    birth_data_envelope: dict[str, Any] | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    email_verified: bool = False
    tier: str = "free"
    created_at: datetime
    updated_at: datetime
    social_provider: str | None = None
    social_subject: str | None = None


class CurrentUser(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    email: str
    tier: str
    email_verified: bool
    preferences: dict[str, Any] = Field(default_factory=dict)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    birth_data: BirthData | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str


class SocialLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_token: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh: str = Field(min_length=1)


class TokenPair(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access: str
    refresh: str


class RegisterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    email_verified: bool = False


class MeResponse(BaseModel):
    """Public profile — MUST NOT include birth_data."""

    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    email: str
    tier: str
    preferences: dict[str, Any] = Field(default_factory=dict)
    email_verified: bool

    @field_validator("email")
    @classmethod
    def _email_ok(cls, v: str) -> str:
        return v
