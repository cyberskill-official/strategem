# TAT - Thai At Than So engine

Feature requests for the Thai At Than So (太乙神數, TaiYi) casting engine - the P2 third engine of Tam Thuc Strategem. 6 tasks, ~68 engineering-hours, all P2. Rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (strategy 3.4 sequences TaiYi third; strategy 5 defines the module). Primary source: `../../Claude/Markdown/Tam-Thuc-04-Thai-At-Than-So.md`. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

TaiYi chu Thien (主天): it is the macro, long-cycle system - the fate of a state, long waves of rise and fall, the multi-year backdrop - as against QiMen's direction-and-timing (Dia) and LiuRen's concrete affair (Nhan). Its base is not the ganzhi of a chosen instant but tich nien, a continuous count of years from an epoch; that number, through remainder reductions, fixes Thai At's palace and the whole chart. Because sources use different epochs (some 60 years apart, enough to re-cast the chart), the epoch is a mandatory, stamped flag - as load-bearing here as dinh cuc method is in QiMen.

## Summary

Six tasks, all P2, ~68 engineering-hours. One (TAT-001, tich nien + ky nguyen) is authored; the other five are authored. The pipeline runs tich nien -> an Thai At + 16 than -> bat tuong + cac toan -> {bon phep, cach cuc + chu-khach} -> assembly, and TAT-006 emits the la so JSON envelope (TASK-PLAT-002, he = "thai_at") and gates the whole engine 100% against the kintaiyi oracle, per epoch and per time level.

## task list

| task | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [TAT-001](TASK-TAT-001-tich-nien/spec.md) | MUST | P2 | 12 | Tich nien + ky nguyen (3 reduction methods, flag) |
| TAT-002 | MUST | P2 | 12 | An Thai At qua cuu cung + 16 than (chinh cung / gian than) |
| TAT-003 | MUST | P2 | 14 | Bat tuong + cac toan (Van Xuong, Thuy Kich, ke than, chu/khach toan) |
| TAT-004 | SHOULD | P2 | 8 | Bon phep (nien/nguyet/nhat/thoi ke) |
| TAT-005 | SHOULD | P2 | 10 | Cach cuc + chu-khach thang bai (tam tai, truong/doan toan) |
| TAT-006 | MUST | P2 | 12 | Engine assembly + JSON + flags + kintaiyi oracle gate |

Total P2: 68h. Only TAT-001 is authored in full; the rest are authored.

## Cross-module dependencies

- Depends on CORE: every task stands on TASK-CORE-005 (the calendar module API), and TAT-006 additionally on TASK-CORE-006 (the oracle harness). Nien ke needs only the civil year, but the duong/am don direction keys off the Dong Chi and Ha Chi instants, and the nhat/thoi ke tich (TAT-004) anchor on Dong Chi - both come from CORE-001, so TaiYi and the calendar core must agree on the solstice instants.
- Depends on PLAT: every engine task emits the TASK-PLAT-002 la so envelope and stamps `co_truong_phai`; TAT-006 owns the assembly and the cache key.
- Blocks CHART-003 (the TaiYi chart view renders the TAT-006 envelope: cuu cung, 16 than, tuong) and EDU-002 (auto-graded practice uses the TaiYi engine as grader at curriculum level 3). Cross-system validate (STRAT-004) can add TaiYi as a third opinion once TAT-006 lands.
- Feeds RAG: the interpretation branch reads the envelope; it never writes those fields. Because TaiYi speaks to large matters (national fortune), the interpretation layer must be especially cautious and explicit about limits (Claude-04 s6.3).

Internal chain: `CORE-005 -> TAT-001 -> TAT-002 -> TAT-003 -> TAT-005`, with `TAT-002 -> TAT-004` and `{TAT-003, CORE-006} -> TAT-006`.

## Module notes

- Crate: `cyberos-thaiat` (Rust). TASK-TAT-001 owns the crate birth; TASK-TAT-002..006 extend it, so the engine is one cargo-testable unit.
- TaiYi is the macro / long-cycle system: its determinism starts from tich nien, so the arithmetic (mod 360, mod 72, mod 60 on a count near 10^7) must use integer types with no overflow or rounding - the most common TaiYi coding bug after the chinh cung vs gian than counting rule. Thai At skips the center palace (5) and lodges in Khon (2); the 16-than ring distinguishes chinh cung from gian than, and mixing the two counting rules is the second classic error.
- Flag: the tich-nien epoch and reduction method (`epoch`, default `kim_kinh` = 10,153,917 + CE; `co_dien` alternative at 724 CE) plus the `dem_toan` rule (count stops before vs after the Thai At palace, default before per the classical Thong Tong). Both are stamped on every chart; a 60-year epoch gap re-casts the whole chart, so an unstamped epoch is a reproduction defect.
- Oracle: kintaiyi (supports all four time levels nien/nguyet/nhat/thoi ke). Acceptance is 100% match per epoch AND per time level, with dedicated boundary tests around the don-switch (Dong Chi / Ha Chi) and the cuc wrap (72 -> 1), and overflow tests on the large tich nien (strategy RISK-2, Claude-04 s7.2).
- Boundary: the engine produces facts only (Thai At palace, 16 than, 8 tuong, the toan, cach cuc, tam tai, truong/doan); the chu-khach victory reading is the AI layer's job, cited from Kim Kinh Thuc Kinh / Thong Tong Bao Giam and AIDisclosure-labeled.
