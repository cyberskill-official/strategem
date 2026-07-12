"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tamthuc_auth.errors import AuthError
from tamthuc_auth.models import CurrentUser
from tamthuc_auth.service import AuthService

_bearer = HTTPBearer(auto_error=False)


def get_auth_service(request: Request) -> AuthService:
    svc = getattr(request.app.state, "auth_service", None)
    if svc is None:
        raise RuntimeError("auth_service not configured on app.state")
    return svc  # type: ignore[no-any-return]


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> CurrentUser:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "authentication failed"}},
        )
    try:
        return svc.current_user(creds.credentials)
    except AuthError as e:
        raise HTTPException(status_code=e.http_status, detail=e.to_envelope()) from e
