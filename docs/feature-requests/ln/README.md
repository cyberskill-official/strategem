# LN - Dai Luc Nham engine

Feature requests for the Dai Luc Nham (大六壬, LiuRen) casting engine - the P1 second engine of Tam Thuc Strategem, built after CORE and the QiMen flagship. 6 FRs, ~70 engineering-hours, all P1. Rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (strategy 3.4 sequences LiuRen as the second engine; strategy 5 defines the module). Primary source: `../../Claude/Markdown/Tam-Thuc-02-Dai-Luc-Nham.md`. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

LiuRen chu Nhan (主人): it answers concrete questions about a single human affair - will this succeed, is the trip smooth, when does the absent person return. Of the three engines it has the most explicit, least school-contested rules: the nine tong mon are a tight if/else decision tree and the khoa the are predicates over the cast board. That is why the Claude source calls it the natural first engine after the calendar core. Here it is the second engine (QiMen leads per DEC-4), but it remains the base system whose shared concepts - thien dia ban, tu khoa, tam truyen, thien tuong - the learner and the platform reuse first.

## Summary

Six FRs, all P1, ~70 engineering-hours. One (LN-001, thien dia ban + nguyet tuong) is authored in full here as the module exemplar; the other five are listed for the dependency picture and are planned (authored later). The pipeline is a straight chain - thien dia ban -> tu khoa -> {tam truyen, thien tuong} -> khoa the / luc than -> assembly - and LN-006 emits the la so JSON envelope (FR-PLAT-002, he = "luc_nham") and gates the whole engine 100% against the kinliuren oracle for every flag combination.

## FR list

| FR | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [LN-001](FR-LN-001-thien-dia-ban-nguyet-tuong.md) | MUST | P1 | 12 | Thien dia ban + nguyet tuong (gia nguyet tuong, thien can ky cung) |
| LN-002 (planned, authored later) | MUST | P1 | 10 | Tu khoa (four lessons, thuong/ha khac) |
| LN-003 (planned, authored later) | MUST | P1 | 16 | Chin tong mon + tam truyen (nine-method decision tree, phuc/phan ngam) |
| LN-004 (planned, authored later) | MUST | P1 | 10 | Muoi hai thien tuong (khoi quy nhan, thuan/nghich bo, cat/hung) |
| LN-005 (planned, authored later) | SHOULD | P1 | 10 | Khoa the + luc than + dung than |
| LN-006 (planned, authored later) | MUST | P1 | 12 | Engine assembly + JSON + flags + kinliuren oracle gate |

Total P1: 70h. Only LN-001 is authored in full; the rest are planned (authored later).

## Cross-module dependencies

- Depends on CORE: every FR stands on FR-CORE-005 (the calendar module API - tu tru plus the current trung khi that sets nguyet tuong), and LN-006 additionally on FR-CORE-006 (the oracle harness must be green before LiuRen inherits the context). LN specifically consumes CORE-001's jie/trung split: nguyet tuong changes at trung khi, never at jie, so LN reads the TrungKhi-kind term, not the month-pillar jie.
- Depends on PLAT: every engine FR emits the FR-PLAT-002 la so envelope and stamps `co_truong_phai`; LN-006 owns the assembly and the cache key. CORE-007 ganzhi primitives (ngu hanh sinh/khac, chi relations) feed the khac/tac test in tu khoa and the luc than mapping.
- Blocks CHART-002 (the LiuRen chart view renders the LN-006 envelope: thien dia ban, tu khoa, tam truyen, thien tuong), STRAT-004 (cross-system validate reads LN-006 alongside QMDG-006), and EDU-002 (auto-graded practice uses the LN engine as grader at curriculum level 2).
- Feeds RAG: the interpretation branch reads the envelope (`he`, `ban`, `cach_cuc`, `co_truong_phai`) to produce cited interpretation; it never writes those fields.

Internal chain: `CORE-005 -> LN-001 -> LN-002 -> {LN-003, LN-004} -> LN-005`, with `{LN-003, LN-004, CORE-006} -> LN-006`.

## Module notes

- Crate: `cyberos-luchnham` (Rust). FR-LN-001 owns the crate birth; FR-LN-002..006 extend it, so the engine is one cargo-testable unit. The LN flag set lives in `flags.rs` as its single home.
- LiuRen is the base system: it shares the most common concepts of the three engines, so its Chi / Can primitives and the thien dia ban model are the ones the later slices (and the training curriculum) build on. An error in the thien dia ban propagates through tu khoa, tam truyen, and thien tuong exactly as a CORE error propagates across engines.
- Oracle: kinliuren. Acceptance is 100% match across at least 500 sample cases, with a dedicated unit test on every branch of the nine tong mon - the phuc ngam, phan ngam, and bat chuyen edges are the ones most prone to error (Claude-02 s8.2). kinliuren needs a lich library for tu tru; here the tu tru and nguyet tuong come from CORE, so both sides are fed the same instants.
- Flags (stamped on every chart into `co_truong_phai`): `khoi_quy_nhan` (day / night selection for tru quy vs da quy, default the Mao..Than window) and `truong_sinh_phai` (the truong sinh method, default `ngu_hanh` where Thuy and Tho share a palace). LiuRen has fewer school variants than QiMen, but these two are stamped whole from the first slice so the chart is reproducible even before the slices that branch on them (LN-004, LN-005) exist.
- Boundary: the engine produces facts only (thien dia ban, tu khoa, tam truyen, thien tuong, khoa the, luc than), all matched to kinliuren; meaning (reading the four lessons as self vs other, the three truyen as a timeline) is the AI layer's job, cited from Tat phap phu / Khoa kinh and AIDisclosure-labeled (Claude-02 s7).
