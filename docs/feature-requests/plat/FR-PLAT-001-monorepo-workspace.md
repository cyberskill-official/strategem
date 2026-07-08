---
id: FR-PLAT-001
title: "Monorepo + hybrid workspace - one repo holding a Rust cargo workspace (crates/), uv-managed Python packages (packages/), and a Next.js app (apps/web), with a root CI skeleton that gates all three toolchains"
module: PLAT
priority: MUST
status: ready_to_implement
phase: P0
slice: 1
lang: iac
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.2, strategy 4.1, Grok-27]
related_frs: [FR-PLAT-002, FR-PLAT-003, FR-PLAT-004, FR-CORE-001, FR-AUTH-001, FR-WEB-001]
depends_on: []
blocks: [FR-PLAT-002, FR-PLAT-003, FR-PLAT-004, FR-CORE-001, FR-CORE-007, FR-KB-001, FR-KB-003, FR-RAG-001, FR-AUTH-001, FR-WEB-001]
new_paths:
  - Cargo.toml
  - rust-toolchain.toml
  - clippy.toml
  - crates/README.md
  - pyproject.toml
  - packages/README.md
  - apps/web/package.json
  - apps/web/next.config.mjs
  - apps/web/tsconfig.json
  - apps/web/tailwind.config.ts
  - .github/workflows/ci.yml
  - .gitignore
  - justfile
  - docs/contracts/.gitkeep
---

## §1 - Description (BCP-14 normative)

This FR creates the Tam Thuc Strategem monorepo and the hybrid workspace that hosts all three toolchains (strategy 3.2, DEC-2). It is the first FR built: every other FR's `new_paths` land inside the tree this FR establishes, so it MUST exist before any engine, package, or screen. Nothing here casts a chart or serves a request - it fixes where code lives, how the three languages coexist, and how the root CI gates the lot.

The repository SHALL be a single monorepo containing three coordinated workspaces:

- a Rust cargo workspace rooted at `Cargo.toml`, with member crates under `crates/` - the calendar core `cyberos-lichphap` (FR-CORE-001), the engines `cyberos-qimen` (and later `cyberos-luc-nham`, `cyberos-thai-at`), the rule engine `cyberos-rule` (FR-RULE-002), the shared boundary crate `laso-envelope` (FR-PLAT-002), and the engine service binary crate(s) that expose the engines over the la so envelope to the Python branch;
- Python packages under `packages/`, managed by `uv` as a workspace - `tamthuc_api` (FR-API-001), `tamthuc_rag` (FR-RAG-001), `tamthuc_kb` (FR-KB-001), and `tamthuc_auth` (FR-AUTH-001);
- a Next.js 14+ application under `apps/web` (FR-WEB-001) using Tailwind and shadcn/ui, styled later by the CyberSkill Design System v1.3.0.

The root CI SHALL run, on every push and pull request, the complete gate for all three toolchains and SHALL fail the build if any lane fails: for Rust, `cargo fmt --check`, `cargo clippy --workspace -- -D warnings`, `cargo test --workspace`; for Python, `ruff check`, `ruff format --check`, `mypy`, `pytest` across all packages; for web, the `apps/web` build and test (`next build`, `next lint`, and the unit test runner). The three lanes SHALL run independently (a Rust failure MUST NOT hide a Python failure) and each SHALL be reproducible locally through the `justfile`.

The Rust engine crates compile to a service the Python API calls; the boundary between the deterministic branch and the interpretation branch is the FR-PLAT-002 envelope (strategy 4.3). This FR fixes the two branches' homes (`crates/` and `packages/`) and the seam between them; it does NOT define the envelope shape (FR-PLAT-002), the DB (FR-PLAT-003), or the deploy pipeline (FR-PLAT-004), though it establishes the CI skeleton those extend.

## §2 - Why this design (rationale for humans)

The stack is deliberately hybrid, not uniform (strategy 3.2, DEC-2). The engines must match reference oracles to the digit and be cargo-testable like the rest of CyberSkill, so they are Rust; the AI, RAG, orchestration, and report layers live where the LLM and embedding ecosystem is and where iteration is fastest, so they are Python; the frontend is Next.js. A single monorepo is chosen over three repos because the three toolchains share one contract (the la so envelope) and one release train: a monorepo makes a cross-language contract change - Rust type plus Python model plus a TypeScript view - one reviewable pull request with one CI run, instead of three repos drifting out of lock-step. That is exactly the drift the envelope contract test (FR-PLAT-002) is built to catch, and it can only catch it if both sides live and build together (RISK-8).

The root CI gating all three lanes from day one is the point of this FR, not an afterthought. If the three-toolchain gate is added later, code accretes that was never held to `-D warnings`, `mypy`, or `next lint`, and retrofitting the gate becomes its own project. Establishing the skeleton now, while the tree is empty, means every subsequent FR is born under the gate. The workspace layout mirrors the cyberos convention (DEC-1) so a later absorption into cyberos is mechanical rather than a port.

## §3 - Contract (layout / manifests / CI)

### Repository layout

```
strategem/
  Cargo.toml                 # [workspace] members = ["crates/*"]
  rust-toolchain.toml        # pinned stable channel + rustfmt, clippy components
  clippy.toml                # workspace lint config
  crates/                    # Rust: engines + rule + laso-envelope + service bins
  pyproject.toml             # uv workspace root; [tool.uv.workspace] members = ["packages/*"]
  packages/                  # Python: tamthuc_api, tamthuc_rag, tamthuc_kb, tamthuc_auth
  apps/
    web/                     # Next.js 14+ (Tailwind + shadcn/ui)
  docs/
    contracts/               # cross-language JSON Schemas (envelope, error, interpretation)
    feature-requests/        # this catalog
    strategy/                # the unified plan
  .github/workflows/ci.yml   # the three-lane gate
  justfile                   # one entry point per gate, runnable locally and in CI
```

### Rust workspace root (`Cargo.toml`)

```toml
[workspace]
resolver = "2"
members = ["crates/*"]

[workspace.package]
edition = "2021"
license = "UNLICENSED"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
chrono = { version = "0.4", features = ["serde"] }
```

Member crates are added by their owning FR (FR-CORE-001 births `cyberos-lichphap`, FR-PLAT-002 births `laso-envelope`, etc.); this FR ships the workspace manifest, `rust-toolchain.toml`, and `clippy.toml` so the first crate lands under the gate.

### Python workspace root (`pyproject.toml`)

```toml
[tool.uv.workspace]
members = ["packages/*"]

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
```

Each package under `packages/` carries its own `pyproject.toml` (owned by its FR) and is a uv workspace member; `uv sync` resolves the whole set from one lockfile.

### Web app (`apps/web`)

Next.js 14+ App Router, TypeScript strict, Tailwind, shadcn/ui. This FR scaffolds the app and its config (`next.config.mjs`, `tsconfig.json` with `strict: true`, `tailwind.config.ts`); FR-WEB-001 installs the Design System v1.3.0 tokens and the component library on top.

### Root CI (`.github/workflows/ci.yml`) - the three lanes

| Lane | Steps (all must pass) |
|---|---|
| rust | `cargo fmt --check`; `cargo clippy --workspace -- -D warnings`; `cargo test --workspace` |
| python | `uv sync`; `ruff check`; `ruff format --check`; `mypy`; `pytest` |
| web | `pnpm install`; `pnpm --filter web build`; `pnpm --filter web lint`; `pnpm --filter web test` |

The lanes run as independent jobs so one lane's failure does not mask another's. Each step has a one-line `just` recipe (`just rust-gate`, `just py-gate`, `just web-gate`) so CI and a developer run the identical command.

## §4 - Acceptance criteria

1. `cargo build --workspace` succeeds against an empty `crates/*` member set (or a single placeholder crate), and `cargo fmt --check` / `cargo clippy --workspace -- -D warnings` pass.
2. `uv sync` resolves the `packages/*` workspace from one lockfile, and `ruff check` / `ruff format --check` / `mypy` / `pytest` pass against the initial package set.
3. `apps/web` builds (`next build`), lints clean (`next lint`), and its test runner passes on the scaffolded app.
4. The CI workflow runs all three lanes as independent jobs on push and pull request; a forced failure in any one lane fails the overall check while the others still report.
5. Every gate is reproducible locally via a single `just` recipe, and the recipe CI runs is byte-identical to the local one.
6. `docs/contracts/` exists and is the agreed home for cross-language JSON Schemas (the envelope schema FR-PLAT-002 lands here).

## §5 - Verification

- A smoke crate, a smoke package, and the scaffolded web app each carry one trivial passing test, so all three lanes exercise `test`, not only `build`.
- A deliberately mis-formatted Rust file, a `mypy` type error, and a `next lint` violation are each shown (in a throwaway branch) to fail the correct lane and only that lane - proof the gate bites and the lanes are independent.
- `just --list` enumerates the gate recipes; running each locally reproduces the CI result.
- Gates (this FR is the gate skeleton): the three lanes above; FR-PLAT-004 extends this workflow with docker build, security scan, and the staging -> prod deploy gate.

## §6 - Implementation skeleton

1. `git init` the monorepo; add `.gitignore` (Rust `target/`, Python `.venv/`/`__pycache__/`, Node `node_modules/`/`.next/`).
2. Author `Cargo.toml` (workspace), `rust-toolchain.toml`, `clippy.toml`; add a placeholder crate so the lane has something to compile and test.
3. Author `pyproject.toml` (uv workspace, ruff, mypy strict); add a placeholder package with one test.
4. Scaffold `apps/web` (Next.js 14+, TS strict, Tailwind, shadcn/ui init) with one component test.
5. Author `justfile` with `rust-gate`, `py-gate`, `web-gate`, and an `all` recipe.
6. Author `.github/workflows/ci.yml` with the three independent jobs calling the `just` recipes; create `docs/contracts/`.

## §7 - Dependencies

Depends on nothing - this is the root FR of the whole program. Blocks FR-PLAT-002 (the envelope crate + package live in this workspace), FR-PLAT-003 (migrations run against this repo's tooling), FR-PLAT-004 (the deploy pipeline extends this CI skeleton), FR-CORE-001 and FR-CORE-007 (the first Rust crates), FR-KB-001 / FR-KB-003 / FR-RAG-001 (the first Python packages), FR-AUTH-001 (`tamthuc_auth`), and FR-WEB-001 (`apps/web`). Effectively every FR in the catalog roots here transitively; the `blocks` list names the direct dependents.

## §8 - Example payloads

Not an API FR - no request/response payload. The "payload" is the layout and the CI matrix in §3. A developer's first interaction:

```
git clone ... && cd strategem
just all          # runs rust-gate, py-gate, web-gate exactly as CI does
```

## §9 - Open questions

- Node package manager: pnpm vs npm vs bun for `apps/web`. Default: pnpm (workspace-friendly, fast); the choice is local to the web lane and does not affect the Rust/Python halves. Revisit only if the deploy image (FR-PLAT-004) argues otherwise.
- Whether the Rust engine reaches Python as an HTTP service, a PyO3 binding, or WASM (strategy 4.1, DEC-2). Default: an out-of-process service behind a thin Python client (see FR-API-001 §9), so the boundary stays a network contract the read-only-envelope assertion can guard; the binding is a later optimization. This FR only reserves the service bin crate's home under `crates/`.
- Monorepo tooling (bare cargo+uv+pnpm vs a task runner like Nx/Turborepo). Default: keep it to `just` + native toolchains at MVP; add a task graph only if build times demand it.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Gate added late | CI skeleton deferred past first code | forbidden; this FR ships the three-lane gate before any engine/package/screen lands |
| Lane masking | one job's failure hides another's | lanes run as independent jobs; a red Rust lane must not green the check while Python is red |
| Local/CI drift | CI runs commands a dev cannot reproduce | every gate is a `just` recipe; CI calls the same recipe |
| Toolchain unpinned | floating Rust/Python/Node versions | `rust-toolchain.toml`, `uv` lockfile, and a pinned Node version fix the versions |
| Contract home missing | schemas scattered per language | `docs/contracts/` is the single home for cross-language JSON Schemas |

## §11 - Notes

This FR is the floor the whole catalog stands on; keep it minimal and strict. It ships an empty-but-gated tree, not features - the value is that the three languages coexist in one repo under one CI train from the first commit, which is what makes the la so envelope contract test (FR-PLAT-002) and the hybrid-stack decision (DEC-2) safe to execute. The layout mirrors the cyberos convention (DEC-1) so a later absorption is mechanical. Do not let a second crate, package, or app land before the corresponding lane is green.
