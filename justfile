# Tam Thuc Strategem - root justfile
# One entry point per gate. CI and devs run the identical recipes.
# See docs/feature-requests/README.md "Gates".

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

# ---------------- Web lane (apps/web, pnpm) ----------------
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

# ---------------- All ----------------
all: rust-gate py-gate web-gate
    @echo "✅ all gates passed (PLAT-001 skeleton)"

# Developer convenience
install: py-sync web-install
    @echo "deps installed for py + web (rust uses cargo)"