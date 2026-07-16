# COV-006 implementation notes

## Landed

| artefact | path |
|----------|------|
| Engine cach_cuc + chu_khach | `crates/cyberos-thaiat/src/engine.rs` |
| Tests | `crates/cyberos-thaiat/tests/cov006_patterns_victory.rs` |
| Story empty-state | `apps/web/src/lib/domain/readings.ts` |
| Glossary | `apps/web/src/lib/domain/glossary.ts` |

## Behaviour

- `nhan_dien_cach_cuc` → envelope `cach_cuc` (facts + citations, no victory verdict).
- `cac_toan` / `chu_khach` always stamped with chu/khach toan + truong_doan.
- Story uses TA long-rhythm metaphor + dedicated empty-state when no patterns.

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
