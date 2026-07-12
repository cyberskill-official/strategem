from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

Layer = Literal["han", "bach_thoai", "dich"]


class Chunk(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunk_id: str
    unit_id: str
    layer: Layer
    text: str
    system: str
    unit_type: str
    citation_id: str
    model: str
    dim: int


class UnitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unit_id: str
    system: str
    unit_type: str
    citation_id: str
    nguyen_van_han: str | None = None
    bach_thoai: str | None = None
    dich: str | None = None
