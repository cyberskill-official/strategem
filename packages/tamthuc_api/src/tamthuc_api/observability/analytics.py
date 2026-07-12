from __future__ import annotations

from typing import Any

from tamthuc_api.observability.logging import redact


def track(event: str, *, request_id: str, props: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"event": event, "request_id": request_id, "properties": redact(props or {})}
