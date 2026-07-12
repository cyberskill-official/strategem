from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str
    locator: str
    han: str | None = None
    bach_thoai: str | None = None
    dich: str | None = None


class ChartSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    he: str
    dau_vao: dict[str, Any]
    lich_phap_summary: str
    key_positions: list[str] = Field(default_factory=list)


class ReportPattern(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    polarity: str
    cung: int | None = None
    score: float | None = None
    citations: list[Citation] = Field(default_factory=list)


class Interpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    beginner: str
    expert: str
    recommendations: list[str] = Field(default_factory=list)


class AIDisclosure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str
    limits: str
    review_status: str


class StructuredReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_id: UUID
    query_id: UUID
    chart_summary: ChartSummary
    detected_patterns: list[ReportPattern]
    interpretation: Interpretation
    citations: list[Citation]
    confidence: float
    ai_disclosure: AIDisclosure
    created_at: datetime
