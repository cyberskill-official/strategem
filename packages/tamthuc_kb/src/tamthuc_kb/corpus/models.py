from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UnitType(StrEnum):
    dieu = "dieu"
    phap = "phap"
    khoa = "khoa"
    cau = "cau"


class LayerText(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nguyen_van_han: str | None = None
    bach_thoai: str | None = None
    dich: str | None = None

    def any_present(self) -> bool:
        return bool(
            (self.nguyen_van_han and self.nguyen_van_han.strip())
            or (self.bach_thoai and self.bach_thoai.strip())
            or (self.dich and self.dich.strip())
        )


class ClassicalUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unit_id: str
    source_id: str
    citation_id: str
    unit_type: UnitType
    ordinal: int = Field(ge=0)
    system: str
    layers: LayerText

    @model_validator(mode="after")
    def _at_least_one_layer(self) -> ClassicalUnit:
        if not self.layers.any_present():
            raise ValueError("at least one layer must be non-empty")
        return self


class ClassicalSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str
    title: str
    system: str
    citation_prefix: str
    language: str = "zh-vi"


class CorpusFile(BaseModel):
    """On-disk source document before segmentation."""

    model_config = ConfigDict(extra="forbid")
    source: ClassicalSource
    units: list[dict[str, Any]]
