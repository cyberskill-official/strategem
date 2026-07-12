from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CitationCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    citation_id: str
    layers: dict[str, str] = Field(default_factory=dict)
    locator: str = ""


class AIDisclosure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_ai_generated: bool = True
    model: str
    prompt_version: str
    retrieved_citation_ids: list[str]
    fallback: bool = False
    degraded: bool = False
    limits: str = "Heritage education / decision support; not fortune-telling."


class Interpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    beginner: str
    expert: str
    recommendations: list[dict[str, Any]]
    citations: list[CitationCard]
    confidence: float = Field(ge=0.0, le=1.0)
    requires_human_review: bool
    ai_disclosure: AIDisclosure
