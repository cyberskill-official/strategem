"""JWT auth helpers for API routes — free cast stays open; premium/history gated.

Public (optional JWT):
  POST /calculate/{qimen|liuren|taiyi}  — anonymous cast allowed
  GET  /queries/{id}, GET /reports/{id} — cast-journey fetch by id
  POST /queries/{id}/follow-up          — cited follow-up chat on a cast
  POST /timing/optimize (anonymous)     — local smoke; free JWT still gated

Protected (require Bearer JWT):
  GET  /queries                 — manage history
  POST /calculate/all           — premium capability
  POST /payments/checkout       — account-bound checkout
  GET  /payments/tier/{user_id} — own tier only
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


def _unauthorized(message: str = "authentication required") -> HTTPException:
    # Match tamthuc_auth.deps shape: {"detail": {"error": {...}}}
    return HTTPException(
        status_code=401,
        detail={"error": {"code": "UNAUTHORIZED", "message": message}},
    )


def _forbidden_tier(message: str) -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={"error": {"code": "FORBIDDEN_TIER", "message": message}},
    )


async def optional_user(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> object | None:
    """Return CurrentUser when a valid Bearer token is present; else None.

    Invalid tokens on public routes are ignored (anonymous path) so free cast
    is not broken by a stale Authorization header.
    """
    if creds is None or creds.scheme.lower() != "bearer":
        return None
    svc = getattr(request.app.state, "auth_service", None)
    if svc is None:
        return None
    try:
        user: object = svc.current_user(creds.credentials)
        return user
    except Exception:
        return None


async def require_user(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> object:
    """Require a valid JWT. Used for history / manage / premium product paths."""
    if creds is None or creds.scheme.lower() != "bearer":
        raise _unauthorized()
    svc = getattr(request.app.state, "auth_service", None)
    if svc is None:
        raise _unauthorized("auth service not configured")
    try:
        user: object = svc.current_user(creds.credentials)
        return user
    except Exception as e:
        raise _unauthorized("authentication failed") from e


def require_premium_capability(user: object, *, capability: str = "calculate_all") -> None:
    """Raise 403 FORBIDDEN_TIER when the JWT principal lacks a premium capability."""
    from tamthuc_auth.rbac import Capability, parse_role
    from tamthuc_auth.scopes import has_capability

    tier = str(getattr(user, "tier", "free") or "free")
    try:
        role = parse_role(tier)
        cap = Capability(capability)
    except ValueError as e:
        raise _forbidden_tier(f"{capability} requires premium+") from e
    if not has_capability(role, cap):
        raise _forbidden_tier(f"{capability} requires premium+")


def user_id_from(user: object | None, *, fallback: str = "anon") -> str:
    if user is None:
        return fallback
    uid = getattr(user, "id", None)
    return str(uid) if uid is not None else fallback
