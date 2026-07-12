from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_rag.schema import Interpretation


class ReviewTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_id: str = Field(default_factory=lambda: str(uuid4()))
    interpretation: Interpretation
    review_status: Literal["pending", "approved", "rejected", "not_required"] = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    reason: str | None = None
    reviewer: str | None = None


class ReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["approve", "reject"]
    reason: str
    reviewer: str
    role: str = "reviewer"


class AuditRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_id: str
    reviewer: str
    decision: str
    reason: str
    timestamp: str
