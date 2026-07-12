from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError


class ValidationError(Exception):
    def __init__(self, message: str = "invalid input") -> None:
        super().__init__(message)
        self.message = message

    def to_envelope(self) -> dict[str, Any]:
        return {"error": {"code": "validation_error", "message": self.message}}


class QueryInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    datetime: str = Field(min_length=8, max_length=64)
    question: str = Field(min_length=1, max_length=2000)
    longitude: float = Field(ge=-180, le=180)


_INJECTION = re.compile(r"(?i)(union\s+select|drop\s+table|<script|javascript:)")


def validate_query_input(raw: dict[str, Any]) -> QueryInput:
    try:
        q = QueryInput.model_validate(raw)
    except PydanticValidationError as e:
        raise ValidationError("invalid input") from e
    if len(q.question.encode("utf-8")) > 8000:
        raise ValidationError("payload too large")
    if _INJECTION.search(q.question):
        raise ValidationError("invalid input")
    return q
