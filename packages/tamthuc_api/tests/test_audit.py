from __future__ import annotations

import pytest
from tamthuc_api.audit import AuditAction, AuditLog


def test_audit_redacts_sensitive() -> None:
    log = AuditLog()
    log.audit(
        "u1",
        AuditAction.chart_cast,
        {"question": "secret q", "birth_data": "raw", "system": "qimen"},
    )
    row = log.rows[0]
    assert row["action"] == "chart_cast"
    assert row["details"]["question"] == "[redacted]"
    assert row["details"]["birth_data"] == "[redacted]"
    assert row["details"]["system"] == "qimen"


def test_append_only() -> None:
    log = AuditLog()
    rid = log.audit(None, AuditAction.abuse_action, {"signal": "probing"})
    with pytest.raises(PermissionError):
        log.update(rid, action="x")
    with pytest.raises(PermissionError):
        log.delete(rid)
    assert len(log.rows) == 1


def test_one_row_per_action() -> None:
    log = AuditLog()
    for a in (
        AuditAction.auth_login,
        AuditAction.chart_cast,
        AuditAction.report_generate,
    ):
        log.audit("u", a, {})
    assert [r["action"] for r in log.rows] == [
        "auth_login",
        "chart_cast",
        "report_generate",
    ]
