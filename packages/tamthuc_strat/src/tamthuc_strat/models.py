from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TimingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: datetime
    end: datetime
    granularity: str = "gio"  # gio | ngay
    loai_cau_hoi: str = "trach_thoi"
    tz: str = "+07:00"
    kinh_do: float = 106.7
    co_truong_phai: dict[str, Any] = Field(default_factory=dict)
    top_n: int = 5


class ScoredWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: datetime
    end: datetime
    score: float
    cat: list[dict[str, Any]] = Field(default_factory=list)
    hung: list[dict[str, Any]] = Field(default_factory=list)
    cast_ref: str


class TimingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    windows: list[ScoredWindow]
    request_echo: TimingRequest
