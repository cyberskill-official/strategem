"""COV-018 — calendar convert (Gregorian | Lunar | Bát tự) via CORE client."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from tamthuc_api.clients.core import CalendarConvertError, LocalCoreClient
from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["calendar"])


class ConvertBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    input_mode: str = "gregorian"
    datetime: str | None = None
    tz: str = "+07:00"
    kinh_do: float | None = None
    longitude: float | None = None
    # lunar
    lunar_year: int | None = None
    lunar_month: int | None = None
    lunar_day: int | None = None
    leap: bool = False
    hour: int | None = 12
    minute: int | None = 0
    # bazi
    nam: str | None = None
    thang: str | None = None
    ngay: str | None = None
    gio: str | None = None
    year_pillar: str | None = None
    month_pillar: str | None = None
    day_pillar: str | None = None
    hour_pillar: str | None = None
    anchor_datetime: str | None = None


@router.post("/calendar/convert", response_model=None)
def calendar_convert(body: ConvertBody, request: Request) -> dict[str, Any] | JSONResponse:
    orch = getattr(request.app.state, "orch", None)
    core = getattr(orch, "core", None) if orch is not None else None
    if core is None or not hasattr(core, "convert_input"):
        core = LocalCoreClient()
    payload = body.model_dump(exclude_none=True)
    if body.longitude is not None and body.kinh_do is None:
        payload["kinh_do"] = body.longitude
    try:
        return core.convert_input(payload)
    except CalendarConvertError as e:
        return JSONResponse(
            status_code=400,
            content=error_envelope(e.code, e.message),
        )
