# REPORT - report generation

Feature requests for report generation: the module that assembles the cast chart plus the cited interpretation into one structured, persisted report, then renders it to PDF. 3 FRs, ~26 engineering-hours, P1-P2. Rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (strategy 4.2 step 7, strategy 5). Primary sources: Grok 33 (report generation) and Grok 08 (sample reports). Language is Python (DEC-2); everything lives in one package, `tamthuc_report`. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

REPORT sits at the join point of the two branches: it reads the la so envelope the deterministic engine cast and the structured output the RAG interpretation produced, and it composes them into a single artifact - it never casts a chart and never re-computes an interpretation. Its output is what the report-view screen (WEB-005) and the PDF export (REPORT-002) render.

## Summary

Three FRs, ~26 engineering-hours. One (REPORT-001, structured report assembly) is authored in full here as the module exemplar; the other two are listed for the dependency picture and are planned (authored later). The spine is REPORT-001 (assemble + persist the structured report object) -> REPORT-002 (PDF export) with REPORT-003 (per-question sample templates) alongside.

## FR list

| FR | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [REPORT-001](FR-REPORT-001-structured-report.md) | MUST | P1 | 10 | Structured report assembly (chart + patterns + interpretation + citations) |
| REPORT-002 (planned, authored later) | SHOULD | P1 | 10 | PDF export (templated, branded, bilingual) |
| REPORT-003 (planned, authored later) | COULD | P2 | 6 | Sample report templates per question type |

Total: 26h. Only REPORT-001 is authored in full; the rest are planned (authored later).

## Cross-module dependencies

- Depends on RAG: all three FRs stand on FR-RAG-003 - its structured output (beginner / expert interpretation, recommendations, citations, confidence, AIDisclosure) is the interpretation half of the report. REPORT never re-prompts the LLM and never re-runs retrieval.
- Depends on PLAT: REPORT reads the FR-PLAT-002 la so envelope for the chart summary and detected patterns, and persists per FR-PLAT-003 (the `reports` table plus an audit row, strategy 4.2 step 9).
- Blocks WEB-005 (the report-view screen renders the REPORT-001 object) and is the base REPORT-002 (PDF) and REPORT-003 (templates) build on.

Internal spine: `RAG-003 -> REPORT-001 -> {REPORT-002, REPORT-003}`, with the chart half read from the PLAT-002 envelope.

## Module notes

- Package: `tamthuc_report` (Python). REPORT-001 owns the assembler and the persistence path; REPORT-002 adds the PDF renderer, REPORT-003 the per-question-type sample templates.
- It assembles chart + patterns + interpretation into a structured report with beginner, expert, and recommendation layers (Grok-33, Grok-08), then hands off to PDF. It reads the engine and RAG output and never re-computes: chart summary and detected patterns are copied from the la so envelope, interpretation and citations from the RAG output. This is the same read-only boundary the RAG branch obeys (strategy 4.3) - the moment REPORT re-derives a chart fact, determinism is gone.
- Every claim carries at least one citation and every report carries an AIDisclosure (strategy 4.4); REPORT enforces both at assembly time, so an uncited claim or a missing disclosure fails before persistence, not after.
- This is the P1 artifact where the deterministic chart and the cited interpretation become one durable, auditable object - persisted, referenced by `query_id`, and rendered downstream. Confidence is carried from RAG-003 unchanged, never recomputed.
