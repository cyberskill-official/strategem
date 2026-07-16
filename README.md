# Tam Thuc Strategem

> "Hien Thuc Hoa Y Chi" — Turn Your Will Into Real.

Decision-support platform digitizing the Tam Thuc (三式) classical East Asian divination systems: Dai Luc Nham (LiuRen), Ky Mon Don Giap (QiMen), Thai At Than So (TaiYi). Deterministic chart engines + cited AI interpretation, framed as heritage education and structured decision analysis.

## Architecture (high level)

- **Deterministic engines** (Rust, `crates/`): CORE calendar/ganzhi, QMDG (QiMen), LN (LiuRen), TAT (TaiYi), RULE pattern detection. Emit the canonical `la so` JSON envelope.
- **Interpretation & orchestration** (Python + FastAPI, `packages/`): RAG over classical text, LLM structured output, report assembly. Never mutate engine fields.
- **Frontend** (Next.js, `apps/web`): query input, interactive charts, cited results, learning surfaces. CyberSkill Design System.

See `docs/strategy/tam-thuc-unified-plan-2026-07-08.md` and the task catalog under `docs/tasks/`.

## Getting started (dev)

Requires:

- **Node 24** (see `.node-version`)
- **pnpm 9+** (used for all web / frontend work; declared via `packageManager`)
- Rust (via `rust-toolchain.toml`)
- Python 3.12+ + uv

```bash
# after clone
just install   # or: uv sync ; pnpm install
just all       # runs the three gates exactly as CI
```

Gates (must stay green on every change):
- Rust: fmt, clippy -D warnings, test
- Python: ruff, format, mypy, pytest
- Web: pnpm build, pnpm lint, pnpm test (typecheck)

## Layout

```
Cargo.toml
pyproject.toml
justfile
crates/          # Rust workspace members (engines + envelope + rule)
packages/        # uv Python workspace (api, rag, kb, auth, ...)
apps/web/        # Next.js app
docs/
  strategy/
  tasks/   # the living spec + IMPLEMENTATION_ORDER.md + backlog.yaml
  contracts/          # cross-language schemas (envelope etc.)
.github/workflows/ci.yml
```

## Safety & invariants

See strategy §4.4 and docs/tasks/README.md. Key:
- Engines stamp every school flag; never hardcode variants.
- Interpretation never writes `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`; always cites + AIDisclosure.
- CORE accuracy: solar term <60s error is stop-ship.
- Personal data never logged; AES-256 at rest for birth data.

## Phases

P0+P1 = MVP (QiMen flagship + LiuRen + strategic tools + cited reports).

This is the initial monorepo skeleton (TASK-PLAT-001).

## License

UNLICENSED (internal / CyberSkill).
