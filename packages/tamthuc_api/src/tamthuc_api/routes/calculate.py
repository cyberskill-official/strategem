from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from tamthuc_api.clients.engine import LocalEngineClient, probe_cast_cli
from tamthuc_api.errors import error_envelope
from tamthuc_api.schemas import CalculateRequest

router = APIRouter(tags=["calculate"])


def _orch(request: Request) -> Any:
    return request.app.state.orch


def _calculate_system(system: str, body: CalculateRequest, request: Request) -> dict[str, Any]:
    orch = _orch(request)
    t0 = time.perf_counter()
    ok = True
    payload = body.model_dump()
    payload.pop("user_id", None)
    user = getattr(request.state, "current_user", None)
    if user is not None:
        payload["user_id"] = str(user.id)
    try:
        result: dict[str, Any] = orch.calculate(system, payload)
        if not result.get("ai_disclosure"):
            raise RuntimeError("AIDisclosure missing")
        return result
    except Exception:
        ok = False
        raise
    finally:
        # COV-021: cast latency by actual engine_source (TT-022), not filesystem probe.
        metrics = getattr(request.app.state, "metrics", None)
        if metrics is not None:
            eng = getattr(orch, "engine", None)
            mode = "unknown"
            if isinstance(eng, LocalEngineClient):
                mode = eng.last_engine_source
            else:
                mode = str(probe_cast_cli().get("engine_mode") or "unknown")
            metrics.record_cast(time.perf_counter() - t0, system=system, engine_mode=mode, ok=ok)


def _tier_from_request(request: Request) -> str:
    user = getattr(request.state, "current_user", None)
    if user is not None:
        return str(user.tier or "free").lower()
    return "free"


@router.post("/calculate/qimen")
def calculate_qimen(body: CalculateRequest, request: Request) -> dict[str, Any]:
    return _calculate_system("qimen", body, request)


@router.post("/calculate/liuren")
def calculate_liuren(body: CalculateRequest, request: Request) -> dict[str, Any]:
    return _calculate_system("liuren", body, request)


@router.post("/calculate/taiyi")
def calculate_taiyi(body: CalculateRequest, request: Request) -> dict[str, Any]:
    return _calculate_system("taiyi", body, request)


@router.post("/calculate/all", response_model=None)
def calculate_all(body: CalculateRequest, request: Request) -> dict[str, Any] | JSONResponse:
    # Entitlement from verified JWT only — never from request body (TT-002).
    user = getattr(request.state, "current_user", None)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )
    tier = _tier_from_request(request)
    if tier in {"free", ""}:
        return JSONResponse(
            status_code=403,
            content=error_envelope("FORBIDDEN_TIER", "calculate_all requires premium+"),
        )
    result: dict[str, Any] = _orch(request).calculate_all(
        {**body.model_dump(), "user_id": str(user.id)}
    )
    return result
