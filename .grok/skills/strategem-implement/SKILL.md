---
name: strategem-implement
description: Implement a Tam Thuc Strategem feature request (FR) end to end - pick the next eligible backlog task (or a named one), build it to its acceptance criteria, run the language gates and engine oracle checks, record evidence in the ledger, and hand off for review. Use when working in the strategem repo and asked to implement an FR, take the next task, or continue the build (for example "implement TT task CORE-001", "build the next strategem task", "work the strategem backlog").
---

# Strategem - implement a feature request

Work one task to a reviewable state, then stop. Do not review your own work or set `done` - that is the operator's job (the `strategem-review` skill).

## 1. Load context first

1. `docs/strategy/tam-thuc-unified-plan-2026-07-08.md` - the rationale, architecture spine, module taxonomy, and invariants. Read the sections your task's FR cites in `refs`.
2. `docs/feature-requests/backlog.yaml` - task status and eligibility. `docs/feature-requests/IMPLEMENTATION_ORDER.md` - the human-readable order and the phase exit gates.
3. The task's FR under `docs/feature-requests/<module>/FR-<ID>-*.md` - this is your spec. Build to its section 4 (acceptance criteria) and section 5 (verification).
4. `docs/feature-requests/README.md` - conventions and gates, plus the two exemplar FRs (`FR-PLAT-002`, `FR-CORE-001`) if you need the shape.

## 2. Pick the task

- If given a task id, use it. Otherwise take the next eligible task in `IMPLEMENTATION_ORDER.md` order (phase, then dependency spine, then id). Eligible = the FR is `ready_to_implement`, status is not `done`, and every `depends_on` is `done`. At the current snapshot the single eligible root is PLAT-001; everything else unblocks as its dependencies close.
- If a task's `body` is `planned` (its FR is still a `draft`), author the FR body first: read the module README plus the cited primary source (the Claude volume or Grok doc in the strategy coverage map), follow the two exemplars exactly (frontmatter plus section 1-11), write the FR file, set its status to `ready_to_implement`, and stop for review before implementing - unless the operator told you to proceed through both authoring and implementation. (All 87 bodies are authored at this snapshot, so this branch is rare.)

## 3. Do the work

- One task = one branch `auto/tt-<id-lowercase>`. One task per commit where practical; commit message `<ID>: <title>`.
- Honor the safety invariants (README.md and strategy section 4.4). In particular:
  - Engines keep the la so JSON envelope (strategy 4.3) exact and stamp every school flag into `co_truong_phai`.
  - Interpretation code never writes `ban` / `cach_cuc` / `lich_phap` / `co_truong_phai`, and always keeps citation + AIDisclosure + HumanReviewGate.
  - Never log birth data or question text.
- Run the gates for your language:
  - Rust: `cargo fmt --check`, `cargo clippy -p <crate> -- -D warnings`, `cargo test -p <crate>`.
  - Python: `ruff check`, `mypy`, `python -m pytest packages/<pkg>`.
  - Web: `pnpm -C apps/web lint`, `pnpm -C apps/web typecheck`, `pnpm -C apps/web test`, `pnpm -C apps/web build`.
  - Engines additionally run the oracle cross-check (kinqimen / kinliuren / kintaiyi / sxwnl / tyme4py) per the FR. A calendar term off by more than 60 seconds is a stop-ship (RISK-1).

## 4. Record and hand off

- Update the task status in `docs/feature-requests/backlog.yaml` (and the row in `IMPLEMENTATION_ORDER.md`) to `implementing` when you start and `in_review` when every acceptance criterion passes with evidence. Do this in the same commit as the work.
- Append one entry to `docs/feature-requests/LEDGER.md` in the format defined there: branch, commits, status transition, gates run and results, evidence (test output, oracle-diff numbers, screenshot paths, measured numbers), sensitive paths, notes.
- Stop at the operator edges: do not push to main, deploy, rotate a secret, or run a destructive migration on shared data. Hand those to the operator with a clear note.
- If you cannot finish inside a reasonable budget (about 5 consecutive gate failures), set the task back to `ready_to_implement` with a `blocked_note`, record why in the ledger, and move on.

## 5. Report back

The task id, the branch, the commits, gate results, what a reviewer should check, and any follow-ups (file them as new tasks, do not scope-creep the current one). Then stop; the operator runs the `strategem-review` skill to approve or reject.
