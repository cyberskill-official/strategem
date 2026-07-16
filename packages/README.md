# packages/

uv-managed Python packages for Tam Thuc Strategem.

Per DEC-2: the AI, RAG, orchestration, report, auth, and KB layers live here.

- `tamthuc_smoke/` - placeholder package (from PLAT-001) so the Python CI lane has something to lint/type/test. Replaced or removed by real packages (tamthuc_api, tamthuc_rag, etc.) owned by their tasks.

All packages:
- participate in `uv sync` (single lockfile from root)
- pass `ruff check`, `ruff format --check`, `mypy`, `pytest`

See root `pyproject.toml`.