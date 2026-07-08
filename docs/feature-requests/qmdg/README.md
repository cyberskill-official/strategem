# QMDG - Ky Mon Don Giap engine

Feature requests for the Ky Mon Don Giap (奇門遁甲, QiMen) casting engine - the P0 flagship engine of Tam Thuc Strategem. Rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (strategy 3.4 makes QiMen the first engine; strategy 5 defines the module). Primary source: `../../Claude/Markdown/Tam-Thuc-03-Ky-Mon-Don-Giap.md`. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

QiMen chu Dia (主地): it answers questions of direction and timing - which way, what to do when, how to arrange for advantage. The engine casts the four-plate chart (dia ban, thien ban, nhan ban, than ban over the nine Luoshu palaces), finds truc phu / truc su, and detects cach cuc. It is the most school-variant-heavy of the three Tam Thuc engines, so the discipline throughout is: configure by flag, never hardcode, and stamp the full flag set into every chart.

## Summary

Seven FRs. Six (QMDG-001..006) are the P0 casting pipeline and are authored in full here; QMDG-007 (dung than by question type, P1) is authored. The pipeline is a straight chain - dinh cuc -> bo dia ban -> truc phu / truc su -> sao / mon / than -> cach cuc -> assembly - and QMDG-006 emits the la so JSON envelope (FR-PLAT-002, `he = "ky_mon"`) and gates the whole engine 100% against the kinqimen oracle for every flag combination.

## FR list

| FR | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [QMDG-001](FR-QMDG-001-dinh-cuc.md) | MUST | P0 | 18 | Dinh cuc (24-jieqi x 3-nguyen table, duong/am don, sieu than tiep khi, 3-method flag) |
| [QMDG-002](FR-QMDG-002-bo-dia-ban.md) | MUST | P0 | 8 | Bo dia ban (luc nghi tam ky placement, directional fill) |
| [QMDG-003](FR-QMDG-003-truc-phu-truc-su.md) | MUST | P0 | 14 | Truc phu / truc su + thien ban rotation (chuyen/phi ban flag, ky cung) |
| [QMDG-004](FR-QMDG-004-sao-mon-than.md) | MUST | P0 | 12 | Cuu tinh / bat mon / bat than placement (am/duong ban than swap) |
| [QMDG-005](FR-QMDG-005-cach-cuc.md) | MUST | P0 | 16 | Cach cuc detection (thap can khac ung, cat/hung, nhap mo / khong vong / phan-phuc ngam) |
| [QMDG-006](FR-QMDG-006-engine-assembly.md) | MUST | P0 | 12 | Engine assembly + JSON envelope + full flag set + kinqimen oracle gate |
| QMDG-007 | SHOULD | P1 | 6 | Dung than by question type (mapping table) |

Total P0: 80h across QMDG-001..006. QMDG-007 adds 6h in P1.

## Cross-module dependencies

- Depends on CORE: every FR stands on FR-CORE-005 (calendar module API - tiet khi, tam nguyen, four pillars) and QMDG-006 additionally on FR-CORE-006 (the oracle harness must be green before QiMen inherits the context). CORE-004 derived states (tuan khong, tomb, hinh) feed cach cuc.
- Depends on RULE: FR-QMDG-005 runs its cat / hung / special-state patterns as data through FR-RULE-002 (the condition DSL and evaluator).
- Depends on PLAT: every engine FR emits the FR-PLAT-002 la so envelope and stamps `co_truong_phai`; QMDG-006 owns the assembly and the cache key.
- Blocks CHART-001 (the interactive 9-palace chart renders the QMDG-006 envelope) and STRAT-001 (the Timing Optimizer scans this engine over a date range).
- Feeds RAG: the interpretation branch reads the envelope (`he`, `ban`, `cach_cuc`, `co_truong_phai`) to produce cited interpretation; it never writes those fields.

Internal chain: `CORE-005 -> QMDG-001 -> 002 -> 003 -> 004 -> 005 -> 006`, with `RULE-002 -> QMDG-005` and `CORE-006 -> QMDG-006`.

## Module notes

- Crate: `cyberos-qimen` (Rust). FR-QMDG-001 owns the crate birth; FR-QMDG-002..006 extend it, so the engine is one cargo-testable unit. `QiMenFlags` lives in `flags.rs` as the single home of the flag set.
- QiMen is the most school-variant-heavy engine, with three orthogonal flag axes - `dingju_method` (dinh cuc method: chaibu / zhirun / maoshan), `pan_method` (chuyen / phi ban), and `yin_yang_pan` (duong / am lineage) - plus two smaller flags (`zhong_gong_ky`, `chan_thai_duong_thoi`). The three axes are independent, so the chart space is their product.
- Default config: thoi-gia duong-ban chaibu chuyen-ban (`dingju_method = chaibu`, `pan_method = zhuan`, `yin_yang_pan = duong`, `zhong_gong_ky = khon2`, `chan_thai_duong_thoi = true`). This is the most common practice but not the only tested one.
- Oracle: kinqimen. The per-flag test matrix is mandatory - acceptance is 100% match for EVERY flag combination, not just the default (strategy RISK-2 and RISK-7). Dedicated edge tests cover sieu than tiep khi, tri nhuan, and the center palace.
- Boundary: the engine produces facts only (four plates, truc phu / truc su, detected cach cuc), all matched to kinqimen; meaning (dung than selection and reading) is the AI layer's job, cited and school-named (Claude-03 s7.3).
