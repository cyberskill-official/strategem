"""Unit tests that do not require Postgres (migration file inventory)."""

from __future__ import annotations

from db_schema import list_migrations, migrations_dir


def test_migrations_dir_exists() -> None:
    d = migrations_dir()
    assert d.is_dir()
    assert d.name == "migrations"


def test_ordered_migration_files() -> None:
    """COV-010 added 0010_app_query_store; list is apply order (lexicographic)."""
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
        "0012_app_query_store_rls.sql",
        "0013_auth_users_columns.sql",
        "0014_refresh_token_revocations.sql",
        "0015_payment_fulfillments.sql",
        "0016_operator_llm_settings.sql",
        "0017_runtime_app_role.sql",
    ]
    # Lexicographic order is apply order
    assert names == sorted(names)
    assert len(names) >= 10


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


def test_app_query_store_rls_migration() -> None:
    text = (migrations_dir() / "0012_app_query_store_rls.sql").read_text(encoding="utf-8")
    assert "FORCE ROW LEVEL SECURITY" in text
    assert "app_query_store_owner" in text
    assert "app.current_user_id" in text


def test_runtime_app_role_migration() -> None:
    text = (migrations_dir() / "0017_runtime_app_role.sql").read_text(encoding="utf-8")
    assert "strategem_app" in text
    assert "NOSUPERUSER" in text
    assert "NOBYPASSRLS" in text
    assert "NOCREATEDB" in text


def test_gin_indexes_present() -> None:
    text = (migrations_dir() / "0008_indexes_gin.sql").read_text(encoding="utf-8")
    assert "jsonb_path_ops" in text
    assert "charts_envelope_gin" in text
    assert "patterns_conditions_gin" in text
    assert "reports_interpretation_gin" in text
