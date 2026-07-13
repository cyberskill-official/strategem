from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from tamthuc_api.clients.engine import probe_cast_cli
from tamthuc_api.errors import error_envelope
from tamthuc_api.schemas import CalculateRequest

router = APIRouter(tags=["calculate"])


def _orch(request: Request) -> Any:
    return request.app.state.orch


def _calculate_system(system: str, body: CalculateRequest, request: Request) -> dict[str, Any]:
    orch = _orch(request)
    t0 = time.perf_counter()
    ok = True
    try:
        result: dict[str, Any] = orch.calculate(system, body.model_dump())
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
    # Free tier cannot calculate_all (AUTH-002 capability)
    if body.tier.lower() == "free":
        return JSONResponse(
            status_code=403,
            content=error_envelope("FORBIDDEN_TIER", "calculate_all requires premium+"),
        )
    result: dict[str, Any] = _orch(request).calculate_all(body.model_dump())
    return result
