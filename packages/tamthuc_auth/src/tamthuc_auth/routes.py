"""Auth HTTP routes (mounted by TASK-API-001).

AUTH-001 foundations: register/login/refresh/me plus verification, password reset,
logout revocation, and DSAR self-service. Email uses FakeEmailSender locally and
Resend when ``RESEND_*`` is set; production fails closed without a sender.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tamthuc_auth.config import is_local_or_test_env
from tamthuc_auth.deps import get_auth_service, get_current_user
from tamthuc_auth.dsar import DsarService, FreshAuthRequired
from tamthuc_auth.email import EmailNotConfigured, require_transactional_email
from tamthuc_auth.errors import AuthError, ConflictError
from tamthuc_auth.models import (
    CurrentUser,
    EmailRequest,
    LoginRequest,
    LogoutRequest,
    MeResponse,
    PasswordResetConfirmRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    SessionsResponse,
    SocialLoginRequest,
    TokenPair,
    VerifyConfirmRequest,
)
from tamthuc_auth.reset import ResetError, confirm_password_reset, request_password_reset
from tamthuc_auth.service import AuthService
from tamthuc_auth.tokens import verify_access
from tamthuc_auth.verification import (
    VerificationError,
    confirm_verification,
    request_verification_by_email,
)

log = logging.getLogger("tamthuc_auth.routes")

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


def _http_error(exc: AuthError) -> HTTPException:
    return HTTPException(status_code=exc.http_status, detail=exc.to_envelope())


def _social_login_disabled() -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": "social login disabled"}},
    )


def _dsar_service(request: Request, svc: AuthService) -> DsarService:
    existing = getattr(request.app.state, "dsar_service", None)
    if existing is not None:
        return existing  # type: ignore[no-any-return]
    dsar = DsarService(svc.store, svc.settings.master_key())
    request.app.state.dsar_service = dsar
    return dsar


@router.post("/register", response_model=RegisterResponse)
def register(
    body: RegisterRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponse:
    try:
        # Never log body.password
        return svc.register(str(body.email), body.password, body.birth_data)
    except EmailNotConfigured as e:
        raise _http_error(e) from e
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


@router.post("/login/google", response_model=None)
def login_google(
    body: SocialLoginRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair | JSONResponse:
    if not is_local_or_test_env():
        return _social_login_disabled()
    try:
        return svc.login_social("google", body.id_token)
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/login/apple", response_model=None)
def login_apple(
    body: SocialLoginRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair | JSONResponse:
    if not is_local_or_test_env():
        return _social_login_disabled()
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


@router.post("/logout")
def logout(
    body: LogoutRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, bool]:
    return svc.logout(body.refresh)


@router.get("/sessions", response_model=SessionsResponse)
def list_sessions(
    svc: Annotated[AuthService, Depends(get_auth_service)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> SessionsResponse:
    if creds is None:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "authentication failed"}},
        )
    try:
        sessions = svc.list_sessions(creds.credentials)
        return SessionsResponse(sessions=sessions)
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/sessions/{session_id}/revoke")
def revoke_session(
    session_id: str,
    svc: Annotated[AuthService, Depends(get_auth_service)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict[str, bool]:
    if creds is None:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "authentication failed"}},
        )
    try:
        return svc.revoke_session(creds.credentials, session_id)
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/sessions/revoke-all")
def revoke_all_sessions(
    svc: Annotated[AuthService, Depends(get_auth_service)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict[str, Any]:
    if creds is None:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "authentication failed"}},
        )
    try:
        return svc.revoke_all_sessions(creds.credentials)
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


@router.post("/verify/request")
def verify_request(
    body: EmailRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, Any]:
    try:
        mail = svc.mail or require_transactional_email()
        return request_verification_by_email(
            str(body.email),
            store=svc.store,
            tokens=svc.email_tokens,
            mail=mail,
        )
    except EmailNotConfigured as e:
        raise _http_error(e) from e
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/verify/confirm")
def verify_confirm(
    body: VerifyConfirmRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, Any]:
    try:
        return confirm_verification(
            body.token,
            store=svc.store,
            tokens=svc.email_tokens,
        )
    except VerificationError as e:
        raise _http_error(e) from e
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/password-reset/request")
def password_reset_request(
    body: EmailRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, Any]:
    try:
        mail = svc.mail or require_transactional_email()
        return request_password_reset(
            str(body.email),
            store=svc.store,
            tokens=svc.email_tokens,
            mail=mail,
        )
    except EmailNotConfigured as e:
        raise _http_error(e) from e
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/password-reset/confirm")
def password_reset_confirm(
    body: PasswordResetConfirmRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, Any]:
    try:
        return confirm_password_reset(
            body.token,
            body.new_password,
            store=svc.store,
            tokens=svc.email_tokens,
            revocation=svc.revocation,
            sessions=svc.sessions,
        )
    except ResetError as e:
        raise _http_error(e) from e
    except AuthError as e:
        raise _http_error(e) from e


@router.post("/dsar/export")
def dsar_export(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[AuthService, Depends(get_auth_service)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict[str, Any]:
    if creds is None:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "authentication failed"}},
        )
    try:
        claims = verify_access(creds.credentials, settings=svc.settings)
        delivery, _archive = _dsar_service(request, svc).export(
            str(user.id),
            auth_iat=float(claims.iat),
        )
        return delivery.model_dump()
    except FreshAuthRequired as e:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "FRESH_AUTH_REQUIRED",
                    "message": "re-authentication required for DSAR",
                }
            },
        ) from e


@router.post("/dsar/erase")
def dsar_erase(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    svc: Annotated[AuthService, Depends(get_auth_service)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict[str, Any]:
    if creds is None:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "unauthorized", "message": "authentication failed"}},
        )
    try:
        claims = verify_access(creds.credentials, settings=svc.settings)
        result = _dsar_service(request, svc).erase(
            str(user.id),
            auth_iat=float(claims.iat),
        )
        return {
            "status": "ok",
            "crypto_shredded": result.crypto_shredded,
            "subject_id": result.subject_id,
        }
    except FreshAuthRequired as e:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "FRESH_AUTH_REQUIRED",
                    "message": "re-authentication required for DSAR",
                }
            },
        ) from e


def create_auth_app(service: AuthService | None = None) -> Any:
    """Build a minimal FastAPI app with auth routes (for tests / local)."""
    from fastapi import FastAPI

    app = FastAPI(title="tamthuc-auth")
    svc = service or AuthService()
    app.state.auth_service = svc
    app.include_router(router)
    return app
