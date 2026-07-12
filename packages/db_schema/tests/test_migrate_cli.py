"""Coverage for migrate CLI paths and error branches (FR-PLAT-003 ≥90% gate)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import db_schema
import db_schema.migrate as migrate_mod
from db_schema.migrate import _redact_dsn, main


def test_redact_dsn_with_credentials() -> None:
    assert (
        _redact_dsn("postgresql://user:secret@localhost:5432/db")
        == "postgresql://***@localhost:5432/db"
    )


def test_redact_dsn_without_at() -> None:
    assert _redact_dsn("postgresql://localhost/db") == "postgresql://***"


def test_main_requires_database_url(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    code = main()
    assert code == 2
    err = capsys.readouterr().err
    assert "DATABASE_URL" in err


def test_main_applies_when_url_set(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    with patch.object(migrate_mod, "apply_migrations", return_value=9) as apply:
        code = main()
    assert code == 0
    apply.assert_called_once_with("postgresql://u:p@h/db")
    assert "applied 9" in capsys.readouterr().out


def test_list_migrations_empty_raises(tmp_path: Path, monkeypatch: Any) -> None:
    empty = tmp_path / "migrations"
    empty.mkdir()
    monkeypatch.setattr(db_schema, "migrations_dir", lambda: empty)
    try:
        db_schema.list_migrations()
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError as e:
        assert "no *.sql" in str(e)


def test_migrations_dir_missing_raises(monkeypatch: Any) -> None:
    monkeypatch.setattr(Path, "is_dir", lambda self: False)
    try:
        db_schema.migrations_dir()
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError as e:
        assert "db/migrations not found" in str(e)


def test_apply_migrations_uses_explicit_file_list(tmp_path: Path) -> None:
    import psycopg

    sql = tmp_path / "0001_noop.sql"
    sql.write_text("SELECT 1;", encoding="utf-8")
    mock_conn = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_conn
    mock_cm.__exit__.return_value = False
    with patch.object(psycopg, "connect", return_value=mock_cm) as connect:
        n = migrate_mod.apply_migrations("postgresql://x", migrations=[sql])
    assert n == 1
    connect.assert_called_once()
    mock_conn.execute.assert_called_once_with("SELECT 1;")
