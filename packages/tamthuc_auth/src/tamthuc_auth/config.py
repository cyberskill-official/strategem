"""Auth settings. Master key and JWT secret never come from the database.

Outside explicit development/test, JWT secret and AES master key are required
and must not equal the known development placeholders (TT-003).
"""

from __future__ import annotations

import base64
import os
from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Known development placeholders — never usable outside ENV/APP_ENV=development|dev|test.
_DEV_JWT_SECRET = "dev-only-change-me-jwt-secret-min-32-bytes!!"
_DEV_MASTER_KEY_B64 = base64.urlsafe_b64encode(b"0" * 32).decode("ascii")


def is_dev_or_test_env() -> bool:
    env = (os.environ.get("ENV") or os.environ.get("APP_ENV") or "").strip().lower()
    return env in {"development", "dev", "test"}


def is_local_or_test_env() -> bool:
    """True for empty ENV (local convenience), development, and test.

    Staging and production must set APP_ENV/ENV explicitly. Used to keep
    test-only social login and payment mock rails off public surfaces (SEC-001).
    """
    env = (os.environ.get("ENV") or os.environ.get("APP_ENV") or "").strip().lower()
    return env in {"", "development", "dev", "test"}


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TAMTHUC_AUTH_", extra="ignore")

    jwt_secret: str = Field(default="")
    jwt_algorithm: str = "HS256"
    access_ttl_seconds: int = 15 * 60
    refresh_ttl_seconds: int = 14 * 24 * 3600
    # 32-byte master key as urlsafe base64
    master_key_b64: str = Field(default="")
    google_audience: str = "tamthuc-google-client"
    apple_audience: str = "tamthuc-apple-client"
    issuer: str = "tamthuc-auth"

    @model_validator(mode="after")
    def _require_secrets(self) -> AuthSettings:
        jwt = (self.jwt_secret or "").strip()
        mk = (self.master_key_b64 or "").strip()
        dev = is_dev_or_test_env()

        if not jwt or not mk:
            if not dev:
                raise ValueError(
                    "TAMTHUC_AUTH_JWT_SECRET and TAMTHUC_AUTH_MASTER_KEY_B64 are required "
                    "when ENV/APP_ENV is not development|dev|test"
                )
            if not jwt:
                jwt = _DEV_JWT_SECRET
            if not mk:
                mk = _DEV_MASTER_KEY_B64
            self.jwt_secret = jwt
            self.master_key_b64 = mk
            return self

        if not dev and (jwt == _DEV_JWT_SECRET or mk == _DEV_MASTER_KEY_B64):
            raise ValueError(
                "refusing known development JWT secret or AES master key outside "
                "ENV/APP_ENV=development|dev|test"
            )
        self.jwt_secret = jwt
        self.master_key_b64 = mk
        return self

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
    return os.environ.get("TAMTHUC_AUTH_JWT_SECRET") or get_settings().jwt_secret
