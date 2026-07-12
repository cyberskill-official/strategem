"""Authorization helpers + FastAPI dependency factories (FR-AUTH-002)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any, Literal

from fastapi import Depends, HTTPException

from tamthuc_auth.deps import get_current_user
from tamthuc_auth.models import CurrentUser
from tamthuc_auth.rbac import ROLE_CAPABILITIES, Capability, Role, parse_role, role_rank
from tamthuc_auth.tiers import Principal, load_tier_configs


def quota_for(principal: Principal) -> int | Literal["unmetered"]:
    cfg = load_tier_configs()[principal.role]
    if principal.role == Role.admin:
        return "unmetered"
    if principal.role == Role.enterprise:
        if principal.enterprise_quota_override is not None:
            return principal.enterprise_quota_override
        return 0  # must configure custom override
    assert isinstance(cfg.requests_per_day, int)
    return cfg.requests_per_day


def has_capability(role: Role, cap: Capability) -> bool:
    return cap in ROLE_CAPABILITIES[role]


def principal_from_user(user: CurrentUser) -> Principal:
    return Principal(subject=str(user.id), role=parse_role(user.tier), kind="user")


def _forbidden(message: str = "forbidden") -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={"error": {"code": "forbidden", "message": message}},
    )


def require_role(*roles: Role) -> Callable[..., Any]:
    allowed = frozenset(roles)

    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        role = parse_role(user.tier)
        if role not in allowed:
            raise _forbidden()
        return user

    return _dep


def require_tier(min_tier: Role) -> Callable[..., Any]:
    min_rank = role_rank(min_tier)

    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        role = parse_role(user.tier)
        if role_rank(role) < min_rank:
            raise _forbidden()
        return user

    return _dep


def require_capability(cap: Capability) -> Callable[..., Any]:
    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        role = parse_role(user.tier)
        if not has_capability(role, cap):
            raise _forbidden()
        return user

    return _dep


def check_capability(principal: Principal, cap: Capability) -> None:
    """Non-FastAPI check used by unit tests and services."""
    if not has_capability(principal.role, cap):
        raise PermissionError("forbidden")
