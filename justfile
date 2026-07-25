# Tam Thuc Strategem - root justfile
# One entry point per gate. CI and devs run the identical recipes.
# See docs/tasks/README.md "Gates".
#
# Frontend / web work ALWAYS uses pnpm (never npm).
# Runtime: Node 24 (see .node-version), pnpm 9+.

set shell := ["bash", "-cu"]

default:
    @just --list

# ---------------- Rust lane (PLAT-001 + all crates) ----------------
rust-fmt:
    cargo fmt --check

rust-clippy:
    cargo clippy --workspace -- -D warnings

rust-test:
    cargo test --workspace

rust-gate: rust-fmt rust-clippy rust-test
    @echo "✅ rust-gate passed"

# ---------------- Python lane (uv workspace) ----------------
# Local `just py-gate` mirrors CI pytest but skips Postgres integration when
# DATABASE_URL is unset (db_schema / auth PG tests soft-skip). To match CI's
# python job (services.postgres + DATABASE_URL), export DATABASE_URL first, then:
#   just db-migrate && just py-gate
# Or run the DB lane alone: just db-gate
# Full local+DB parity: just py-gate-with-db
py-sync:
    uv sync --all-packages

py-ruff:
    uv run ruff check

py-ruff-format:
    uv run ruff format --check

py-mypy:
    uv run mypy packages/

py-test:
    uv run pytest -q

py-gate: py-sync py-ruff py-ruff-format py-mypy py-test
    @echo "✅ py-gate passed"

# ---------------- Web lane (apps/web) — ALWAYS pnpm ----------------
# pnpm is the only allowed package manager for the frontend (see root package.json + pnpm-workspace.yaml).
web-install:
    pnpm --filter web install --ignore-scripts

web-build:
    pnpm --filter web build

web-lint:
    pnpm --filter web lint

web-test:
    pnpm --filter web test

web-gate: web-install web-build web-lint web-test
    @echo "✅ web-gate passed"

# ---------------- DB lane (TASK-PLAT-003) ----------------
# Requires DATABASE_URL pointing at Postgres 16+ (CI service or local).
# CI python job always sets DATABASE_URL; local py-gate does not unless you export it.
db-migrate:
    uv run python -m db_schema.migrate

db-test:
    uv run pytest -q packages/db_schema

db-gate: db-test
    @echo "✅ db-gate passed"

# Full python+db parity with CI when DATABASE_URL is available.
py-gate-with-db: py-gate db-gate
    @echo "✅ py-gate-with-db passed (requires DATABASE_URL)"

# ---------------- All ----------------
all: rust-gate py-gate web-gate
    @echo "✅ all gates passed (PLAT-001 skeleton; DB lane is separate — just db-gate)"

# Developer convenience
install: py-sync web-install
    @echo "deps installed for py + web (pnpm for frontend; rust uses cargo)"
