"""tamthuc_auth — TASK-AUTH-001 identity, tokens, social hooks, birth_data crypto."""

from tamthuc_auth.crypto import decrypt_birth_data, encrypt_birth_data, rewrap_dek
from tamthuc_auth.errors import AuthError, InvalidCredentials, TokenExpired, TokenInvalid
from tamthuc_auth.models import CurrentUser, MeResponse, TokenPair
from tamthuc_auth.passwords import hash_password, verify_password
from tamthuc_auth.service import AuthService
from tamthuc_auth.tokens import (
    AccessClaims,
    issue_access,
    issue_refresh,
    revoke_refresh,
    verify_access,
)

__all__ = [
    "AccessClaims",
    "AuthError",
    "AuthService",
    "CurrentUser",
    "InvalidCredentials",
    "MeResponse",
    "TokenExpired",
    "TokenInvalid",
    "TokenPair",
    "decrypt_birth_data",
    "encrypt_birth_data",
    "hash_password",
    "issue_access",
    "issue_refresh",
    "revoke_refresh",
    "rewrap_dek",
    "verify_access",
    "verify_password",
]
