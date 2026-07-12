from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiError(Exception):
    code: str
    message: str
    http_status: int
    details: dict[str, Any] | None = None

    def to_envelope(self) -> dict[str, Any]:
        body: dict[str, Any] = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            body["error"]["details"] = self.details
        return body


def map_upstream_error(exc: BaseException) -> ApiError:
    msg = str(exc)
    if "circuit_open" in msg or "timeout" in msg.lower():
        return ApiError("UPSTREAM_UNAVAILABLE", "dependency unavailable", 503)
    return ApiError("UPSTREAM_ERROR", "upstream failure", 502)
