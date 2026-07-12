"""Append-only audit log — FR-API-004."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class AuditAction(str, Enum):
    birth_data_read = "birth_data_read"
    birth_data_write = "birth_data_write"
    chart_cast = "chart_cast"
    report_generate = "report_generate"
    report_download = "report_download"
    tier_change = "tier_change"
    auth_login = "auth_login"
    auth_refresh = "auth_refresh"
    dsar_export = "dsar_export"
    dsar_erase = "dsar_erase"
    abuse_action = "abuse_action"


_SENSITIVE_KEYS = frozenset({"birth_data", "question", "password", "token", "ciphertext"})


def _redact(details: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in details.items():
        if k in _SENSITIVE_KEYS:
            out[k] = "[redacted]"
        elif isinstance(v, dict):
            out[k] = _redact(v)
        else:
            out[k] = v
    return out


@dataclass
class AuditLog:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def audit(
        self, user_id: str | None, action: AuditAction, details: dict[str, Any]
    ) -> str:
        row_id = str(uuid4())
        self.rows.append(
            {
                "id": row_id,
                "user_id": user_id,
                "action": action.value,
                "details": _redact(details),
            }
        )
        return row_id

    def update(self, row_id: str, **_: Any) -> None:
        raise PermissionError("audit_logs are append-only")

    def delete(self, row_id: str) -> None:
        raise PermissionError("audit_logs are append-only")
