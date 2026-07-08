# Tam Thuc Strategem - execution ledger

Append-only. Every task run adds one entry (the agent appends during work; the reviewer appends the verdict). Never edit or delete a past entry; corrections are new entries referencing the old one.

Entry format:

```
## <YYYY-MM-DD> <TASK-ID> <short title> - <agent|operator>
- branch: auto/tt-<id-lowercase>
- commits: <hashes>
- status: <from> -> <to>            # draft->ready_to_implement | ready_to_implement->implementing | implementing->in_review | in_review->done | ->blocked (reason)
- gates: <commands run and results, one line each>     # cargo/ruff/pnpm + oracle diff where relevant
- evidence: <test output refs, oracle-diff numbers, screenshot paths, measured p95, commit hashes>
- sensitive paths: <none | list + justification>       # auth, RLS, birth data, secrets, deploy, envelope contract
- notes: <deviations from the FR spec, discovered follow-ups filed as new tasks, do not scope-creep>
```

Evidence expectations by task class:
- Engines: the oracle-diff result (sample size, mismatch count, which flag combos). CORE additionally the sxwnl term-max-error in seconds and the tyme4py pillar pass/fail.
- Contract (PLAT-002): the cross-language round-trip result and the schema-drift check.
- Data/auth: the no-GUC RLS probe row count (must be zero), proof birth data is encrypted and unlogged.
- Interpretation: citation-resolution check, AIDisclosure present, chart-field-write check (must be none).
- Frontend: screenshot path, diacritics clip-test result, accessibility note.

---

<!-- entries appended below -->

## 2026-07-08 PLAT-001 Monorepo + hybrid workspace + CI skeleton - agent
- branch: auto/tt-plat-001
- commits: 0810933de774a12a9ac75ea086e521c04e6eebbf
- status: ready_to_implement -> in_review
- gates: 
  - just rust-gate: PASS (fmt/clippy/test; 1 smoke test ok)
  - just py-gate: PASS (uv sync; ruff clean; format clean; mypy clean; pytest 1 passed)
  - just web-gate: PASS (pnpm install; next build ok; lint clean; tsc --noEmit test ok)
  - just all: PASS (all three lanes green)
- evidence: 
  - Rust smoke crate (crates/smoke) with 1 unit test passing under cargo test --workspace
  - Python smoke package (packages/tamthuc_smoke) with 1 test passing under pytest
  - Web app (apps/web) builds, lints, typechecks (tsc as test runner)
  - Full gate transcript in agent session; AC1-6 met (see FR §4,§5)
- sensitive paths: none (no auth, no birth data, no secrets, no envelope yet, no DB)
- notes: 
  - Added root package.json + pnpm-workspace.yaml to make pnpm --filter work for web lane (required for FR-specified commands and CI).
  - Placeholder smoke crates/packages will be superseded by real members (CORE-001 etc.); intentionally minimal.
  - No shadcn/ui components yet (per FR: that is WEB-001).
  - just installed via cargo for local repro; CI uses direct or setup steps.
  - Follow-ups (do not scope creep): file new task for "add real smoke tests or remove placeholder once first real crate lands".
