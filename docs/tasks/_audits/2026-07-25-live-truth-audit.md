# Tam Thuc live truth audit — 2026-07-25

## Purpose and scope

This audit records the evidence used for Wave W0 truth-up. It reconciles task status and supersedes the formal “≥100%” documentation-coverage claims. It does not implement product fixes, certify classical correctness, or rerun the full end-to-end product suite.

The prior live audit reported green Rust/Python/web gates, including 262 Python tests passed and 9 skipped and a successful 23-route web build. Those results prove that the repository builds and its current tests pass; they do not prove that the default product journey or the classical acceptance criteria are complete.

## Executive finding

Tam Thuc is a broad, working MVP skeleton with real calculation pipelines and product routes, but its current state is **Partial**, not complete and not ≥100% against either the Claude or Grok source sets.

The highest-impact gaps observed on the live/default path are:

- All three engines execute, but known classical simplifications remain.
- `INTERPRET_MODE=rag` can still run with `StubLlm`, `HashEmbedder`, and chunks derived from pattern metadata rather than a genuine classical corpus.
- The audited report journey returns 404 for `GET /reports/{query_id}` and its PDF endpoint.
- The PDF exporter returns HTML with a `%PDF-1.4` prefix rather than a valid rendered PDF.
- `GET /api/v1/knowledge/patterns?system=X` ignores the requested system filter.
- Product-scale oracle goldens are generated from the current engines and `cast_cli`, so they are regression fixtures rather than independent kin* certification.

## Status reconciliation

`docs/tasks/backlog.yaml` is the canonical lifecycle-status source for the original 87-task plan.

| Decision | Result | Reason |
|----------|--------|--------|
| Preserve `done` | PLAT-001, PLAT-002 | These are the only original-plan tasks supported by the execution ledger’s implementation/review evidence |
| Downgrade unproven `done` | Remaining 85 tasks → `ready_to_implement` | Code presence and passing aggregate tests do not substitute for per-task acceptance evidence; the live audit also found material failures in claimed-complete areas |
| Remove lifecycle `blocked` | Dependency blocking is computed from `deps` | A task can be ready for implementation/rework while still ineligible until dependencies are accepted |
| Reconcile human-readable index | `IMPLEMENTATION_ORDER.md` mirrors the 2/85 split | It no longer independently claims all tasks are `done` |
| Handle later topology addendum | PLAT-011..015 → `not_in_backlog` in the index | These later specs are absent from the canonical 87-task backlog and therefore cannot claim a canonical lifecycle status or `done` |

`docs/tasks/LEDGER.md` remains append-only and was not rewritten. It is evidence, not a competing current-state index.

The downgrade does not assert that the 85 tasks have no implementation. It says their current implementations require review, repair, or fresh acceptance before the lifecycle can honestly advance.

## Technical findings

### Engine and calendar fidelity — Partial

- QiMen `crates/cyberos-qimen/src/dinh_cuc.rs` explicitly describes its 24×3 calculation as “Simplified but structured” and its method differences as stubs.
- LiuRen `crates/cyberos-luchnham/src/engine.rs` hard-codes `khong_vong` as `[Tuat, Hoi]` with a comment that CORE should fill it in the full stack. The thiep-hai surface exists, but the complete classical selection depth is not externally demonstrated.
- TaiYi emits a usable chart, but the full toán/classical acceptance set is not independently certified.
- `crates/cyberos-lichphap/src/solar.rs` and `eot.rs` identify their implementation as Meeus low-precision. The required jieqi error below one minute over the specified range was not established by this audit.

These are real pipelines, not empty stubs, but they do not justify “Full (100%).”

### Oracle evidence — Unproven externally

`docs/tasks/cov-wave/TASK-COV-001-oracle-certification-suite/implementation-notes.md` records:

> `oracle_source=engine_golden_v1+cast_cli`

That source is useful for deterministic regression testing. It is not an independent oracle because the expected outputs originate from the implementation under test. External kinqimen/kinliuren/kintaiyi fixtures remain incomplete relative to the stated sample sizes and flag combinations.

**W4 note (2026-07-25):** An external-oracle certification harness now exists under `oracle/` with committed `sample/` rows (classical / published-almanac pins) and `full/` drop slots. When real kin*/sxwnl dumps are absent, full-cert tests **SKIP** honestly; they do not fabricate data. Full external certification remains pending real dumps.

### RAG and interpretation — Stub–Partial

- `packages/tamthuc_rag/src/tamthuc_rag/llm.py` defaults `LLM_BACKEND` to `stub`.
- `StubLlm` emits generic fixed educational text, including “A cautious educational reading of the chart patterns.”
- Ingest/retrieval defaults to `HashEmbedder`.
- `packages/tamthuc_api/src/tamthuc_api/clients/rag.py` converts matched patterns into retrieval chunks. An OpenAI-compatible local client exists, but it is opt-in and does not make the default runtime a genuine bundled classical RAG system.

The anti-hallucination fallback behavior is useful, but the default path is not the “real LLM + real corpus” path claimed by the superseded benchmark.

### Report persistence and PDF — Broken

The live cast returned a query identifier, but the subsequent report and PDF GETs returned 404. This breaks the dashboard’s report-view/download journey and means report persistence is not reliable under the identifier used by the product flow.

`packages/tamthuc_report/src/tamthuc_report/pdf_export.py` labels its output “PDF-like packaging” and returns:

```python
header = b"%PDF-1.4\n% CyberSkill report export (HTML body follows)\n"
return header + body
```

Magic bytes do not make the following HTML a valid PDF document. The PDF acceptance claim is therefore broken even where an endpoint returns bytes.

### Rule and knowledge endpoint — Partial with defect

The pattern catalog and browse surface exist, but the live request `GET /api/v1/knowledge/patterns?system=X` returned the full 175-pattern set regardless of `system`. Per-system filtering is therefore not working on the audited path.

### Product and design — Partial

The web application has substantial route breadth and coherent VI-first presentation. However:

- the core cast → report → PDF journey dead-ends;
- several secondary surfaces are thin;
- the published `@cyberskill/design` package is not adopted;
- local TypeScript/CSS tokens drift;
- follow-up chat and runtime browser acceptance remain later-wave work.

Route existence and successful static build are not equivalent to end-to-end product completion.

## Benchmark disposition

The 2026-07-14 COV acceptance narrative is preserved for history, but it no longer controls the formal score.

- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`: current formal result **Partial**.
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`: current formal result **Partial**.

No replacement percentage is asserted. A numerical score would imply precision not supported by the present evidence.

## Deferred remediation

W0 changes documentation and status only. Product fixes are intentionally deferred:

- report identifier persistence and real PDF rendering;
- pattern endpoint filtering;
- genuine default RAG over a classical corpus;
- complete nine-step orchestration, auth enforcement, and Postgres default path;
- deeper engine/calendar fidelity and independent external oracle certification;
- published design-system adoption and full runtime E2E/a11y coverage.

