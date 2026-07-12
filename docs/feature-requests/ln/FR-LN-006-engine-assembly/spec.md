---
id: FR-LN-006
title: "Engine assembly - thien dia ban -> tu khoa -> tam truyen -> thien tuong -> khoa the, full la so envelope for he=luc_nham, co_truong_phai flag set, kinliuren 100% oracle gate + cache key"
module: LN
priority: MUST
status: ready_to_implement
phase: P1
slice: 6
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-02 s8, Claude-02 s1.2, Grok-29]
related_frs: [FR-LN-001, FR-LN-002, FR-LN-003, FR-LN-004, FR-LN-005, FR-CORE-005, FR-CORE-006, FR-PLAT-002, FR-CHART-002]
depends_on: [FR-LN-003, FR-LN-004, FR-CORE-006]
blocks: [FR-CHART-002, FR-STRAT-004, FR-EDU-002]
new_paths:
  - crates/cyberos-luchnham/src/engine.rs
  - crates/cyberos-luchnham/src/ban.rs
  - crates/cyberos-luchnham/tests/engine_oracle.rs
  - crates/cyberos-luchnham/tests/fixtures/engine_kinliuren.csv
---

## §1 - Description (BCP-14 normative)

This FR assembles the whole LiuRen engine: it runs the five casting steps in order, emits the complete la so envelope for `he = "luc_nham"`, stamps the full LN school-flag set, and gates the crate against kinliuren at 100 percent across flag combinations. It is the terminal LN slice and the second casting engine on the platform (strategy 3.4).

The module SHALL run the deterministic pipeline in the fixed order (Claude-02 s1.2, s8.1): gia nguyet tuong to build the thien dia ban (FR-LN-001) -> lap tu khoa, the four lessons and the khac/tac census (FR-LN-002) -> chin tong mon to draw the tam truyen (FR-LN-003) -> an muoi hai thien tuong, the twelve generals (FR-LN-004) -> nhan dien khoa the, luc than, dung than (FR-LN-005, when present). It SHALL take its calendar context (tu tru, the current trung khi that fixes nguyet tuong, tuan khong, vuong/suy) from the FR-CORE-005 calendar object and MUST NOT recompute any calendar value.

The module SHALL emit the la so JSON envelope defined by FR-PLAT-002, filling `ban` with the LiuRen plates (thien_dia_ban, tu_khoa, tam_truyen, thien_tuong, luc_than, khoa_the, khong_vong), promoting khoa the into `cach_cuc`, and stamping `co_truong_phai` with the full LN flag set (khoi_quy_nhan, quy_nhan_variant, truong_sinh_phai) per Claude-02 s8.2. A chart MUST be fully reproducible from `dau_vao` plus `co_truong_phai` plus `lich_phap` flags; any input that changed the board that is not stamped is a contract defect (strategy 4.4). The module SHALL compute the chart cache key by the FR-PLAT-002 rule.

The oracle is kinliuren. The module SHALL match kinliuren on all of tu khoa, tam truyen, and thien tuong across at least 500 sample cases spanning the flag combinations, and every branch of the chin tong mon (all nine methods, the five bat chuyen days, phuc ngam, and phan ngam) SHALL have its own unit case. This 100 percent match across flags is the phase-transition gate for LiuRen (Claude-02 s8.2) and the LN half of the FR-CORE-006 oracle harness.

## §2 - Why this design (rationale for humans)

The five steps are a strict chain in which an early error propagates to everything after it (Claude-02 s1.2): nguyet tuong and gio chiem fix the thien ban, the thien ban fixes the four lessons, the four lessons through the nine methods fix the three truyen, and the generals ride on top. That is precisely why each step was built and oracle-tested as its own slice, and why assembly is a distinct final slice whose job is to wire the tested pieces to the shared calendar and the shared envelope, not to re-derive anything. Assembly owns exactly two new responsibilities: the envelope mapping and the whole-chart oracle gate across flags.

The whole-chart gate exists because per-slice oracles can each pass while the composition still drifts - a flag consumed in FR-LN-004 but stamped inconsistently, or a calendar term read at the wrong instant, shows up only when the full chart is compared to kinliuren end to end. Running the gate across flag combinations, not just the default, is the direct mitigation of the school-mixing risk (strategy RISK-2): a chart cast under giap_mau_canh must match kinliuren configured the same way, and a chart under tach_giap must match kinliuren configured that way, so the stamp is provably faithful.

The cache key is load-bearing for the platform, not a local optimization. Because casting is fully deterministic, an identical `(he, dau_vao, co_truong_phai, lich_phap flags)` must yield an identical chart, so the chart is cacheable by a stable hash of exactly those inputs (FR-PLAT-002, FR-PLAT-006). Getting the key right here is what lets the LiuRen engine sit behind the same 24-hour chart cache as QiMen without either engine leaking a flag out of the key.

## §3 - Contract (algorithm and types)

### The engine JSON (Claude-02 s8.1, reproduced verbatim)

This is the native engine object the assembly produces, before it is placed into the FR-PLAT-002 envelope:

```json
{
  "he": "luc_nham",
  "dau_vao": {
    "datetime": "...", "tz": "+07:00",
    "kinh_do": 106.7, "chan_thai_duong_thoi": true
  },
  "tu_tru": { "nam":"甲辰", "thang":"丙寅",
              "ngay":"甲子", "gio":"甲子" },
  "nguyet_tuong": "亥",
  "gio_chiem": "子",
  "tu_khoa": [
    ["丑", "甲"],
    ["子", "丑"],
    ["亥", "子"],
    ["戌", "亥"]
  ],
  "tam_truyen": {
    "so":"...", "trung":"...", "mat":"...",
    "phep":"賊克/元首"
  },
  "thien_tuong": [ ],
  "luc_than": [ ],
  "khoa_the": ["元首"],
  "khong_vong": ["戌", "亥"],
  "co_truong_phai": {
    "quy_nhan_variant": "giap_mau_canh",
    "chan_thai_duong_thoi": true
  }
}
```

### Mapping the engine object into the FR-PLAT-002 envelope

The s8.1 object is the LiuRen-native view; the envelope is the cross-engine contract. The mapping:

| s8.1 engine field | Envelope location |
|---|---|
| he | `he` (= "luc_nham") |
| dau_vao | `dau_vao` (datetime, tz, kinh_do, loai_cau_hoi) |
| tu_tru, khong_vong | `lich_phap` (from FR-CORE-005; not re-emitted in `ban`) |
| nguyet_tuong, gio_chiem, tu_khoa, tam_truyen, thien_tuong, luc_than, khoa_the | `ban.*` (the LiuRen plates) |
| khoa_the | also promoted into `cach_cuc` (FR-LN-005) |
| co_truong_phai | `co_truong_phai` (full LN flag set) |
| (new) | `provenance` (engine "ln", engine_version, cast_at, cache_key) |

The `tu_khoa` array keeps the s8.1 `[thuong_than, ha_than]` pair order. `nguyet_tuong` and `gio_chiem` are echoed into `ban` for the LiuRen view even though nguyet_tuong derives from `lich_phap.tiet_khi` (the current trung khi). The engine object's `chan_thai_duong_thoi` lives under `dau_vao`/`lich_phap` in the envelope, not `co_truong_phai`.

### LN school flags (Claude-02 s8.2, reproduced)

Three flags, all stamped in `co_truong_phai`:

- `quy_nhan_variant`: the Quy Nhan rule - giap_mau_canh (default, Giap grouped with Mau Canh) or tach_giap (Giap split to Mui). (FR-LN-004)
- `khoi_quy_nhan`: the resolved day/night noble (tru_quy or da_quy) under the day/night threshold. (FR-LN-004)
- `truong_sinh_phai`: the truong sinh cycle method - ngu_hanh (default, Thuy and Tho share a palace) or am_duong (yin-yang forward/reverse). (FR-LN-001, consumed by FR-LN-005)

Every emitted chart stamps all three so the result is reproducible and defensible under oracle diff (Claude-02 s8.2).

### Public types (`crates/cyberos-luchnham/src/ban.rs`, `engine.rs`)

```rust
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BanLucNham {
    pub thien_dia_ban: ThienDiaBan,   // FR-LN-001
    pub tu_khoa: TuKhoa,              // FR-LN-002
    pub tam_truyen: TamTruyen,        // FR-LN-003
    pub thien_tuong: AnThienTuong,    // FR-LN-004
    pub khoa_the: Vec<KhoaThe>,       // FR-LN-005 (layer one always; layer two when present)
    pub luc_than: Vec<(Chi, LucThan)>,
    pub dung_than: Option<(LucThan, Chi)>,
    pub khong_vong: [Chi; 2],         // from FR-CORE-004 via lich_phap
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LnFlags {
    pub khoi_quy_nhan: TruDa,
    pub quy_nhan_variant: QuyNhanVariant,
    pub truong_sinh_phai: TruongSinhPhai,
}

/// Run the five steps and emit the FR-PLAT-002 envelope for he = "luc_nham".
pub fn cast(lich_phap: &LichPhap, dau_vao: &DauVao, flags: &LnFlags) -> LaSo;
pub fn cache_key(dau_vao: &DauVao, flags: &LnFlags, lich_phap: &LichPhap) -> String; // FR-PLAT-002 rule
```

## §4 - Acceptance criteria

1. `cast` runs the five steps in order and emits a valid FR-PLAT-002 envelope with `he = "luc_nham"`, `ban` carrying thien_dia_ban / tu_khoa / tam_truyen / thien_tuong / luc_than / khoa_the / khong_vong, and `provenance.engine = "ln"`.
2. The envelope validates against `docs/contracts/laso-envelope.schema.json` and round-trips (Rust serialize -> Python parse -> Rust parse) byte-stable for a golden fixture, reusing the FR-PLAT-002 harness.
3. Oracle, default flags: over >= 500 sample cases, the computed tu khoa, tam truyen, and thien tuong are identical to kinliuren. A term-boundary case (a probe between a jie and the following trung khi) still uses the trung khi's nguyet tuong (FR-LN-001) and matches.
4. Oracle, across flags: the sample is re-run under tach_giap and (where it affects the board) truong_sinh_phai = am_duong, each against kinliuren configured the same way, and each matches; a chart cast under one flag set does not match kinliuren configured under the other (proving the flag actually bites and is stamped).
5. Branch coverage: every one of the nine methods, each of the five bat chuyen days, and both ngam cases has a dedicated unit case that matches kinliuren to the digit.
6. Two charts cast from identical `dau_vao` + `co_truong_phai` + `lich_phap` flags produce identical `cache_key` values, and any change to a stamped flag changes the key (per FR-PLAT-002).

## §5 - Verification

- `tests/engine_oracle.rs` loads `fixtures/engine_kinliuren.csv` (>= 500 whole-chart cases with tu tru, nguyet tuong, flags, and the expected tu khoa / tam truyen / thien tuong, generated once from kinliuren + a calendar lib and committed) and asserts full-chart identity per case. This is the LiuRen phase-transition gate and MUST run in CI as part of the FR-CORE-006 harness.
- Flag-combination matrix: the property test iterates the closed flag product (quy_nhan_variant x truong_sinh_phai x day/night) over a case subset and asserts each combination matches kinliuren configured identically, and that mismatched configurations diverge.
- Reproduction: recast each fixture chart from its stamped `dau_vao` + `co_truong_phai` + `lich_phap` alone and assert an identical envelope (the strategy 4.4 determinism invariant).
- Cache key: equal-input charts hash equal; a flipped flag changes the hash; keys are identical to the FR-PLAT-002 Python implementation on the same inputs.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-luchnham -- -D warnings`, `cargo test -p cyberos-luchnham`, plus the oracle gate.

## §6 - Implementation skeleton

1. `ban.rs`: `BanLucNham`, `LnFlags`; the `ban` (de)serialization into the FR-PLAT-002 `serde_json::Value` slot.
2. `engine.rs`: `cast` wiring FR-LN-001..005 in order off the FR-CORE-005 `LichPhap`; assemble `BanLucNham`; promote khoa the into `cach_cuc`; stamp `co_truong_phai` with all three flags.
3. `cache_key`: implement the FR-PLAT-002 stable-hash rule (he, dau_vao rounded to casting granularity, co_truong_phai sorted, lich_phap.co_lich_phap sorted).
4. Build the s8.1 engine object and the envelope mapping (§3); keep the `[thuong_than, ha_than]` pair order.
5. Generate the kinliuren whole-chart fixture once (documented script, not run in CI), forcing nine-method + five-bat-chuyen + both-ngam + both-variant coverage, and commit.
6. Wire the oracle gate, the flag matrix, the reproduction test, and the cross-language cache-key test.

## §7 - Dependencies

Depends on FR-LN-003 (tam truyen) and FR-LN-004 (thien tuong) for the board, and on FR-CORE-006 (the oracle harness this gate plugs into) and FR-CORE-005 (the calendar object supplying tu tru, the trung khi, tuan khong, and vuong/suy). Consumes FR-LN-001/002 transitively and FR-LN-005 when present (layer-two khoa the, luc than, dung than). Emits the FR-PLAT-002 envelope. Blocks FR-CHART-002 (the LiuRen chart view renders this envelope), FR-STRAT-004 (cross-system validate consumes it), and FR-EDU-002 (auto-graded practice uses the engine as grader).

## §8 - Example payloads

Full LiuRen envelope (day Giap Ty, gio Ty, nguyet tuong Hoi), the s8.1 engine object mapped into FR-PLAT-002:

```json
{
  "envelope_version": 1,
  "he": "luc_nham",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "hon_nhan" },
  "lich_phap": {
    "tu_tru": { "nam": "甲辰", "thang": "丙寅", "ngay": "甲子", "gio": "甲子" },
    "tiet_khi": { "hien_hanh": "雨水", "bat_dau": "...", "tam_nguyen": "..." },
    "phai_sinh": { "tuan_khong": ["戌", "亥"] }
  },
  "ban": {
    "thien_dia_ban": { "nguyet_tuong": "亥", "gio_chiem": "子", "trang_thai": "Thuong", "...": "from FR-LN-001" },
    "tu_khoa": [ ["丑","甲"], ["子","丑"], ["亥","子"], ["戌","亥"] ],
    "tam_truyen": { "so": "...", "trung": "...", "mat": "...", "phep": "賊克/元首" },
    "thien_tuong": { "...": "from FR-LN-004" },
    "luc_than": [ ], "khoa_the": ["元首"], "khong_vong": ["戌", "亥"]
  },
  "cach_cuc": [ { "id": "nguyen_thu", "name": "元首", "cung": null, "polarity": "cat", "score": null, "citations": ["Luc Nham Dai Toan"] } ],
  "co_truong_phai": { "khoi_quy_nhan": "tru_quy", "quy_nhan_variant": "giap_mau_canh", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "...", "cache_key": "..." }
}
```

`tu_tru` and `khong_vong` come from `lich_phap` (FR-CORE-005) and are echoed into `ban.khong_vong` for the LiuRen view; nguyet_tuong derives from `lich_phap.tiet_khi.hien_hanh` (a TrungKhi term, here 雨水 -> Hoi). The `tam_truyen` values are the s8.1 placeholders; a concrete chart's chain and fired method are pinned by kinliuren.

## §9 - Open questions

- Binding form to Python: does the orchestrator call the LN engine as a service or via a PyO3 binding (strategy 3.2)? Either way Python never recomputes the chart; the envelope is the only boundary. Default to the same transport QMDG-006 uses; align when that is decided.
- Flag axes in the cache key: the key includes quy_nhan_variant, truong_sinh_phai, and the day/night threshold policy. Confirm the day/night policy (fixed Mao..Than vs sunrise/sunset) is represented in the key, since it changes the generals.
- kinliuren calendar coupling: kinliuren does not compute tu tru; the fixture feeds it the same tu tru and nguyet tuong FR-CORE-005 produces (FR-LN-001 open question). Confirm the fixture generator uses CORE's trung khi instant so LiuRen and the calendar core stay on one clock (strategy RISK-1).
- Layer-two khoa the absent: when FR-LN-005 is not yet done, `ban.khoa_the` carries only the method-tied name from FR-LN-003. Confirm CHART-002 and the report tolerate the reduced set.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Composition drift | per-slice oracles pass but the whole chart diverges | whole-chart oracle gate fails; do not ship |
| Flag not stamped | a school variant used but absent from co_truong_phai | reproduction-from-stamp diverges; envelope CI fails |
| Flag doesn't bite | tach_giap chart still matches giap_mau_canh oracle | the cross-flag divergence assertion fails (flag is inert) |
| Calendar recomputed | engine re-derives nguyet tuong instead of reading lich_phap | term-boundary case diverges from CORE / kinliuren |
| Cache key leaks a flag | a stamped flag omitted from the key | equal keys for charts that differ; key-stability test fails |
| Pair order flipped | `ban.tu_khoa` emitted as `[ha, thuong]` | golden envelope vs s8.1 diverges; CHART-002 mis-draws |

## §11 - Notes

This is the terminal LiuRen slice and the platform's second casting engine (strategy 3.4). Its whole value is composition plus proof: it wires five separately-tested slices to the shared calendar (FR-CORE-005) and the shared envelope (FR-PLAT-002), then proves the composition against kinliuren across the closed flag product. Treat the across-flags gate as non-negotiable - matching only the default configuration would let a school-mixing bug ship (strategy RISK-2). The crate `cyberos-luchnham` is now one cargo-testable unit from thien dia ban to envelope; LiuRen's Chi/Can primitives and this envelope are what CHART-002, STRAT-004, and the EDU grader build on. Oracle kinliuren; this gate is the LiuRen half of the FR-CORE-006 harness and the phase-transition condition for the engine.
