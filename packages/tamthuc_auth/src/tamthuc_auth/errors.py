"""Typed auth errors and the generic API error envelope shape (TASK-API-001 preview)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class AuthError(Exception):
    """Base typed auth failure."""

    code: str = "auth_error"
    http_status: int = 401

    def __init__(self, message: str = "authentication failed") -> None:
        super().__init__(message)
        self.message = message

    def to_envelope(self) -> dict[str, Any]:
        # Generic message — no account enumeration (AC §4.6).
        return {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }


class InvalidCredentials(AuthError):
    code = "invalid_credentials"
    http_status = 401

    def __init__(self) -> None:
        super().__init__("authentication failed")


class TokenInvalid(AuthError):
    code = "token_invalid"
    http_status = 401

    def __init__(self, message: str = "token invalid") -> None:
        super().__init__(message)


class TokenExpired(TokenInvalid):
    code = "token_expired"

    def __init__(self) -> None:
        super().__init__("token expired")


class TokenRevoked(TokenInvalid):
    code = "token_revoked"

    def __init__(self) -> None:
        super().__init__("token revoked")


class SocialTokenInvalid(AuthError):
    code = "social_token_invalid"
    http_status = 401

    def __init__(self) -> None:
        super().__init__("authentication failed")


class ConflictError(AuthError):
    code = "conflict"
    http_status = 409

    def __init__(self, message: str = "conflict") -> None:
        super().__init__(message)


@dataclass
class ErrorEnvelope:
    code: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {"error": {"code": self.code, "message": self.message}}
