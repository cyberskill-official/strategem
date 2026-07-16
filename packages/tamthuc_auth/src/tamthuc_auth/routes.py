"""Auth HTTP routes (mounted by TASK-API-001)."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from tamthuc_auth.deps import get_auth_service, get_current_user
from tamthuc_auth.errors import AuthError, ConflictError
from tamthuc_auth.models import (
    CurrentUser,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    SocialLoginRequest,
    TokenPair,
)
from tamthuc_auth.service import AuthService

log = logging.getLogger("tamthuc_auth.routes")

router = APIRouter(prefix="/auth", tags=["auth"])


def _http_error(exc: AuthError) -> HTTPException:
    return HTTPException(status_code=exc.http_status, detail=exc.to_envelope())


@router.post("/register", response_model=RegisterResponse)
def register(
    body: RegisterRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponse:
    try:
        # Never log body.password
        return svc.register(str(body.email), body.password, body.birth_data)
    except ConflictError as e:
        raise _http_error(e) from e
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/login", response_model=TokenPair)
def login(
    body: LoginRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair:
    try:
        return svc.login(str(body.email), body.password)
    except AuthError as e:
        # Generic envelope for unknown email and wrong password alike
        raise _http_error(e) from e


@router.post("/login/google", response_model=TokenPair)
def login_google(
    body: SocialLoginRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair:
    try:
        return svc.login_social("google", body.id_token)
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/login/apple", response_model=TokenPair)
def login_apple(
    body: SocialLoginRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair:
    try:
        return svc.login_social("apple", body.id_token)
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/refresh", response_model=TokenPair)
def refresh(
    body: RefreshRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair:
    try:
        return svc.refresh(body.refresh)
    except AuthError as e:
        raise _http_error(e) from e


@router.get("/me", response_model=MeResponse)
def me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> MeResponse:
    return MeResponse(
        user_id=user.id,
        email=user.email,
        tier=user.tier,
        preferences=user.preferences,
        email_verified=user.email_verified,
    )


def create_auth_app(service: AuthService | None = None) -> Any:
    """Build a minimal FastAPI app with auth routes (for tests / local)."""
    from fastapi import FastAPI

    app = FastAPI(title="tamthuc-auth")
    svc = service or AuthService()
    app.state.auth_service = svc
    app.include_router(router)
    return app
