from __future__ import annotations

import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from tamthuc_api.auth_deps import (
    optional_user,
    require_premium_capability,
    require_user,
    user_id_from,
)
from tamthuc_api.clients.engine import probe_cast_cli
from tamthuc_api.errors import error_envelope
from tamthuc_api.schemas import CalculateRequest

router = APIRouter(tags=["calculate"])


def _orch(request: Request) -> Any:
    return request.app.state.orch


def _calculate_system(
    system: str,
    body: CalculateRequest,
    request: Request,
    *,
    user: object | None,
) -> dict[str, Any]:
    orch = _orch(request)
    payload = body.model_dump()
    # Associate authenticated casts with the JWT subject; anonymous stays "anon".
    payload["user_id"] = user_id_from(user)
    if user is not None:
        payload["tier"] = str(getattr(user, "tier", payload.get("tier") or "free"))
    t0 = time.perf_counter()
    ok = True
    try:
        result: dict[str, Any] = orch.calculate(system, payload)
        if not result.get("ai_disclosure"):
            raise RuntimeError("AIDisclosure missing")
        return result
    except Exception:
        ok = False
        raise
    finally:
        # COV-021: cast latency by system + engine_mode
        metrics = getattr(request.app.state, "metrics", None)
        if metrics is not None:
            mode = str(probe_cast_cli().get("engine_mode") or "unknown")
            metrics.record_cast(time.perf_counter() - t0, system=system, engine_mode=mode, ok=ok)


@router.post("/calculate/qimen")
def calculate_qimen(
    body: CalculateRequest,
    request: Request,
    user: Annotated[object | None, Depends(optional_user)],
) -> dict[str, Any]:
    """Public free cast — JWT optional (anonymous allowed)."""
    return _calculate_system("qimen", body, request, user=user)


@router.post("/calculate/liuren")
def calculate_liuren(
    body: CalculateRequest,
    request: Request,
    user: Annotated[object | None, Depends(optional_user)],
) -> dict[str, Any]:
    """Public free cast — JWT optional (anonymous allowed)."""
    return _calculate_system("liuren", body, request, user=user)


@router.post("/calculate/taiyi")
def calculate_taiyi(
    body: CalculateRequest,
    request: Request,
    user: Annotated[object | None, Depends(optional_user)],
) -> dict[str, Any]:
    """Public free cast — JWT optional (anonymous allowed)."""
    return _calculate_system("taiyi", body, request, user=user)


@router.post("/calculate/all", response_model=None)
def calculate_all(
    body: CalculateRequest,
    request: Request,
    user: Annotated[object, Depends(require_user)],
) -> dict[str, Any] | JSONResponse:
    """Premium multi-system cast — requires JWT + calculate_all capability.

    Body ``tier`` is ignored for authorization (spoofable); JWT principal wins.
    """
    from fastapi import HTTPException

    try:
        require_premium_capability(user, capability="calculate_all")
    except HTTPException as e:
        err = e.detail.get("error") if isinstance(e.detail, dict) else None
        return JSONResponse(
            status_code=e.status_code,
            content={"error": err}
            if isinstance(err, dict)
            else error_envelope("FORBIDDEN_TIER", str(e.detail)),
        )

    payload = body.model_dump()
    payload["user_id"] = user_id_from(user)
    payload["tier"] = str(getattr(user, "tier", "premium"))
    result: dict[str, Any] = _orch(request).calculate_all(payload)
    return result
