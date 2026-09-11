"""D-MIG-001: checksum + advisory lock migrator behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg
import pytest
from db_schema.migrate import (
    MigrationDirtyError,
    apply_migrations,
    file_checksum,
)


def test_file_checksum_stable(tmp_path: Path) -> None:
    p = tmp_path / "a.sql"
    p.write_text("SELECT 1;\n", encoding="utf-8")
    assert file_checksum(p) == file_checksum(p)
    assert len(file_checksum(p)) == 64


def test_apply_migrations_inserts_checksum(tmp_path: Path) -> None:
    sql = tmp_path / "0001_noop.sql"
    sql.write_text("SELECT 1;", encoding="utf-8")
    checksum = file_checksum(sql)

    mock_conn = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_conn
    mock_cm.__exit__.return_value = False
    tx_cm = MagicMock()
    tx_cm.__enter__.return_value = None
    tx_cm.__exit__.return_value = False
    mock_conn.transaction.return_value = tx_cm

    ledger_miss = MagicMock()
    ledger_miss.fetchone.return_value = None
    mock_conn.execute.side_effect = [
        MagicMock(),  # ensure_ledger
        MagicMock(),  # advisory lock
        ledger_miss,  # SELECT ledger
        MagicMock(),  # apply sql
        MagicMock(),  # INSERT
        MagicMock(),  # unlock
    ]
    with patch.object(psycopg, "connect", return_value=mock_cm):
        n = apply_migrations("postgresql://x", migrations=[sql])
    assert n == 1
    insert_call = mock_conn.execute.call_args_list[-2]
    assert checksum in str(insert_call)


def test_apply_migrations_dirty_on_checksum_mismatch(tmp_path: Path) -> None:
    sql = tmp_path / "0001_noop.sql"
    sql.write_text("SELECT 1;", encoding="utf-8")

    mock_conn = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_conn
    mock_cm.__exit__.return_value = False

    ledger_hit = MagicMock()
    ledger_hit.fetchone.return_value = ("deadbeef" * 8, "applied")
    mock_conn.execute.side_effect = [
        MagicMock(),  # ensure_ledger
        MagicMock(),  # lock
        ledger_hit,  # SELECT
        MagicMock(),  # UPDATE dirty
        MagicMock(),  # unlock
    ]
    with (
        patch.object(psycopg, "connect", return_value=mock_cm),
        pytest.raises(MigrationDirtyError, match="checksum mismatch"),
    ):
        apply_migrations("postgresql://x", migrations=[sql])


def test_migrate_sh_delegates_to_python() -> None:
    # packages/db_schema/tests → repo root is parents[3]
    root = Path(__file__).resolve().parents[3]
    text = (root / "deploy" / "vps" / "migrate.sh").read_text(encoding="utf-8")
    assert "db_schema.migrate" in text
    assert "ON_ERROR_STOP" not in text  # no separate psql ledger path
