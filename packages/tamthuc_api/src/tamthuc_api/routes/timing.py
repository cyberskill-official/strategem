from fastapi import APIRouter
from fastapi.responses import JSONResponse

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["timing"])


@router.post("/timing/optimize")
def timing_optimize() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content=error_envelope("NOT_IMPLEMENTED", "STRAT-001 not mounted"),
    )


@router.post("/scenario/compare")
def scenario_compare() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content=error_envelope("NOT_IMPLEMENTED", "STRAT-002 not mounted"),
    )
