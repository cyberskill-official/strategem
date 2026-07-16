"""Curation review models — TASK-KB-004."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewObjectType(StrEnum):
    pattern = "pattern"
    classical_unit = "classical_unit"


class ReviewState(StrEnum):
    in_review = "in_review"
    accepted = "accepted"
    rejected = "rejected"


class ReviewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    object_type: ReviewObjectType
    object_id: str
    object_version: int
    state: ReviewState
    submitted_by: str
    submitted_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class ReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: str
    object_type: ReviewObjectType
    object_id: str
    reviewer_id: str
    decision: Literal["accept", "reject"]
    reason: str
    decided_at: datetime
    result_version: int | None = None

    @field_validator("reason")
    @classmethod
    def reason_nonempty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("reason is required for both accept and reject")
        return v
