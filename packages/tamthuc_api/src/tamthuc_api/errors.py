from __future__ import annotations

from typing import Any
from uuid import uuid4


def error_envelope(
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id or str(uuid4()),
        }
    }
    if details:
        body["error"]["details"] = details
    return body


STATUS_BY_CODE = {
    "VALIDATION_ERROR": 400,
    "FORBIDDEN_TIER": 403,
    "NOT_FOUND": 404,
    "RATE_LIMITED": 429,
    "NOT_IMPLEMENTED": 501,
    "UPSTREAM_ENGINE": 502,
    "UPSTREAM_UNAVAILABLE": 503,
}
