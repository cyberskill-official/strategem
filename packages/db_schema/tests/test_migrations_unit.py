"""Unit tests that do not require Postgres (migration file inventory)."""

from __future__ import annotations

from db_schema import list_migrations, migrations_dir


def test_migrations_dir_exists() -> None:
    d = migrations_dir()
    assert d.is_dir()
    assert d.name == "migrations"


def test_ordered_migration_files() -> None:
    """W2 added 0011_anon_user; list is apply order (lexicographic)."""
    files = list_migrations()
    names = [f.name for f in files]
    assert names == [
        "0001_init_extensions.sql",
        "0002_users.sql",
        "0003_queries.sql",
        "0004_charts.sql",
        "0005_knowledge_patterns.sql",
        "0006_reports.sql",
        "0007_audit_logs.sql",
        "0008_indexes_gin.sql",
        "0009_rls_policies.sql",
        "0010_app_query_store.sql",
        "0011_anon_user.sql",
    ]
    # Lexicographic order is apply order
    assert names == sorted(names)
    assert len(names) >= 11


def test_users_sql_has_soft_delete_and_bytea_birth() -> None:
    text = (migrations_dir() / "0002_users.sql").read_text(encoding="utf-8")
    assert "birth_data_encrypted" in text
    assert "bytea" in text
    assert "deleted_at" in text


def test_rls_sql_force_and_fail_closed_guc() -> None:
    text = (migrations_dir() / "0009_rls_policies.sql").read_text(encoding="utf-8")
    assert "FORCE ROW LEVEL SECURITY" in text
    assert "app.current_user_id" in text
    assert "app_admin" in text


def test_gin_indexes_present() -> None:
    text = (migrations_dir() / "0008_indexes_gin.sql").read_text(encoding="utf-8")
    assert "jsonb_path_ops" in text
    assert "charts_envelope_gin" in text
    assert "patterns_conditions_gin" in text
    assert "reports_interpretation_gin" in text
