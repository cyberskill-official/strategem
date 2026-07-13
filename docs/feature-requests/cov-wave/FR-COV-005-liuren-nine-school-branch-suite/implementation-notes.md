# COV-005 implementation notes

## Landed

| artefact | path |
|----------|------|
| Nine-branch tam truyen | `crates/cyberos-luchnham/src/tamtruyen.rs` (`NINE_PHAP`, empty-census Bat/Dao/Biet/Mao) |
| Engine khoa_the + flags | `crates/cyberos-luchnham/src/engine.rs` (`recognize_khoa_the`, truong_sinh stamp) |
| Branch + golden tests | `crates/cyberos-luchnham/tests/cov005_nine_branch.rs` |
| Golden key regen | `crates/cyberos-luchnham/examples/regen_cert_keys.rs` + updated `liuren_cert_v1.csv` |
| Web khoa_the section | `apps/web/src/components/chart/liuren-chart.tsx` |
| Vernacular glossary | `apps/web/src/lib/domain/glossary.ts` |
| i18n | `chart.liuren.khoaThe` vi/en/zh |

## §1 AC

1. Unit tests all nine branches incl. phuc/phan — **yes**
2. khoa_the array on ban + LN chart — **yes**
3. quy_nhan / truong_sinh flags stamped — **yes**
4. ≥30 goldens with tu_khoa + tam_truyen — **yes** (30-row fixture)

## Tests

`cargo test -p cyberos-luchnham --tests` green. Evidence: `{SCRATCH}/cov005-*.log`.

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
