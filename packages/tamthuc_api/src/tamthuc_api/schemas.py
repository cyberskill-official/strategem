from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CalculateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    datetime: str
    tz: str = "+07:00"
    place: str | None = None
    longitude: float | None = None
    kinh_do: float | None = None
    question: str = ""
    question_type: str = "trach_thoi"
    systems: list[str] | None = None
    persona_level: str = "beginner"
    co_truong_phai: dict[str, object] | None = None
    # Deprecated client field — ignored for entitlement (TT-002). Kept optional for
    # backward-compatible request bodies; tier is derived from verified JWT only.
    tier: str | None = None


class CalculateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query_id: str
    charts: dict[str, Any]
    patterns: list[Any] = Field(default_factory=list)
    interpretation: dict[str, Any] | None = None
    ai_disclosure: dict[str, Any] | None = None
