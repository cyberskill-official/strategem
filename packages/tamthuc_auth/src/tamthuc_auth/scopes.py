"""Authorization helpers + FastAPI dependency factories (TASK-AUTH-002)."""

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


def assert_role_allowed(user: CurrentUser, *roles: Role) -> CurrentUser:
    role = parse_role(user.tier)
    if role not in frozenset(roles):
        raise _forbidden()
    return user


def assert_min_tier(user: CurrentUser, min_tier: Role) -> CurrentUser:
    if role_rank(parse_role(user.tier)) < role_rank(min_tier):
        raise _forbidden()
    return user


def assert_has_capability(user: CurrentUser, cap: Capability) -> CurrentUser:
    if not has_capability(parse_role(user.tier), cap):
        raise _forbidden()
    return user


def require_role(*roles: Role) -> Callable[..., Any]:
    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        return assert_role_allowed(user, *roles)

    return _dep


def require_tier(min_tier: Role) -> Callable[..., Any]:
    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        return assert_min_tier(user, min_tier)

    return _dep


def require_capability(cap: Capability) -> Callable[..., Any]:
    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        return assert_has_capability(user, cap)

    return _dep


def check_capability(principal: Principal, cap: Capability) -> None:
    """Non-FastAPI check used by unit tests and services."""
    if not has_capability(principal.role, cap):
        raise PermissionError("forbidden")
