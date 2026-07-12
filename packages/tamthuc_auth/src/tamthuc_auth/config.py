"""Auth settings. Master key and JWT secret never come from the database."""

from __future__ import annotations

import base64
import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TAMTHUC_AUTH_", extra="ignore")

    jwt_secret: str = Field(default="dev-only-change-me-jwt-secret-min-32-bytes!!")
    jwt_algorithm: str = "HS256"
    access_ttl_seconds: int = 15 * 60
    refresh_ttl_seconds: int = 14 * 24 * 3600
    # 32-byte master key as urlsafe base64 (or raw 32-byte via env helper)
    master_key_b64: str = Field(default=base64.urlsafe_b64encode(b"0" * 32).decode("ascii"))
    google_audience: str = "tamthuc-google-client"
    apple_audience: str = "tamthuc-apple-client"
    issuer: str = "tamthuc-auth"

    def master_key(self) -> bytes:
        raw = base64.urlsafe_b64decode(self.master_key_b64.encode("ascii"))
        if len(raw) != 32:
            raise ValueError("master key must decode to 32 bytes")
        return raw


@lru_cache
def get_settings() -> AuthSettings:
    return AuthSettings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()


def master_key_from_env() -> bytes:
    """Optional override: TAMTHUC_AUTH_MASTER_KEY_B64."""
    return get_settings().master_key()


def jwt_secret_from_env() -> str:
    return os.environ.get("TAMTHUC_AUTH_JWT_SECRET", get_settings().jwt_secret)
