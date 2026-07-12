from __future__ import annotations

from typing import Any

from tamthuc_api.observability.logging import redact


def capture_exception(
    exc: BaseException, *, request_id: str, extra: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Sentry-shaped event dict (no SDK required in unit tests)."""
    return {
        "request_id": request_id,
        "exception": type(exc).__name__,
        "message": str(exc)[:200],
        "extra": redact(extra or {}),
    }
