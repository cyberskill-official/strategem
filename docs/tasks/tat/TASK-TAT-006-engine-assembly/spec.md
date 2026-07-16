---
id: TASK-TAT-006
title: "Engine assembly + JSON envelope + full flag set + kintaiyi oracle gate - run the pipeline tich nien -> an Thai At + 16 than -> bat tuong + toan -> cach cuc + chu-khach, emit the s7.1 engine JSON mapped into the PLAT-002 envelope for he=thai_at, stamp co_truong_phai (epoch / dem_toan / cap / than-variant), cache by year+cap+epoch; acceptance is 100% match to kintaiyi per epoch AND per time level"
module: TAT
priority: MUST
status: done
phase: P2
slice: 5
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-04 s7, Claude-04 s7.1, Claude-04 s7.2, Grok-30]
related_frs: [TASK-TAT-001, TASK-TAT-002, TASK-TAT-003, TASK-TAT-004, TASK-TAT-005, TASK-PLAT-002, TASK-CORE-006, TASK-CHART-003]
depends_on: [TASK-TAT-003, TASK-CORE-006]
blocks: [TASK-CHART-003]
new_paths:
  - crates/cyberos-thaiat/src/engine.rs
  - crates/cyberos-thaiat/src/ban.rs
  - crates/cyberos-thaiat/tests/engine_kintaiyi.rs
  - crates/cyberos-thaiat/tests/fixtures/engine_kintaiyi_all_flags.csv
---

## §1 - Description (BCP-14 normative)

This task assembles the whole Thai At engine from the slices TASK-TAT-001..005 into one deterministic pipeline, emits the la so envelope for `he = "thai_at"`, stamps the full flag set, and gates the engine 100% against the kintaiyi oracle. It is the terminal MUST of the TAT module and the culmination of the `cyberos-thaiat` crate.

The module SHALL run the pipeline in order (Claude-04 s7.1): compute the tich for the chosen level and reduce to the cuc (TASK-TAT-001, and TASK-TAT-004 for nguyet / nhat / thoi ke), seat Thai At and lay the sixteen than (TASK-TAT-002), place the eight tuong and compute the toan (TASK-TAT-003), then recognize the cach and compute tam tai and the four criteria (TASK-TAT-005). Every step is deterministic, so the assembled chart SHALL be reproducible from `dau_vao` plus the stamped flags alone.

The module SHALL emit the s7.1 engine JSON mapped into the TASK-PLAT-002 envelope: `he = "thai_at"` at the top level; `dau_vao`; `lich_phap` from TASK-CORE-005; the engine plates (`tich`, `thai_at_cung`, `thai_at_ring`, `thap_luc_than`, `bat_tuong`, `cac_toan`, `tam_tai`) inside `ban`; each recognized cach as an envelope-level `cach_cuc` entry; and the flag set in `co_truong_phai`. The module SHALL NOT invent an engine-local envelope shape - it fills the shared PLAT-002 envelope.

The module SHALL stamp the full flag set into `co_truong_phai` (Claude-04 s7.2): `epoch` (default `kim_kinh`, the ~60-year-gap school flag from TASK-TAT-001), `dem_toan` (default `truoc_thai_at`, the count-stop flag from TASK-TAT-003), the time-level `cap` (nien / nguyet / nhat / thoi), and the than-name variant handling flag (TASK-TAT-002). Every flag that changed the chart SHALL be stamped, or it is a reproduction defect (RISK-2). The module SHALL compute the chart cache key per TASK-PLAT-002 (a stable hash keyed by year + cap + epoch and the sorted flag set), since the whole pipeline is deterministic and cacheable (Claude-04 s7.1).

Acceptance SHALL be a 100% match to the kintaiyi oracle per epoch AND per time level, with dedicated boundary tests around the don switch (Dong Chi / Ha Chi) and the cuc wrap (72 -> 1), and overflow tests on the large tich (Claude-04 s7.2). This gate SHALL run in CI and is a stop-ship if it fails.

## §2 - Why this design (rationale for humans)

The assembly is where the la so envelope contract (TASK-PLAT-002) and the flag discipline (RISK-2) become real for TaiYi. Every prior TAT slice emitted a fragment into `ban`; this task wires them into the one envelope shape the interpretation branch reads, so the AI layer sees a Thai At chart in exactly the same frame as a QiMen or LiuRen chart, distinguished only by the `he` tag. Filling the shared envelope rather than a bespoke shape is what keeps the deterministic-engine / AI-layer boundary a hard, typed contract instead of a per-engine special case (strategy 4.3, RISK-8).

The flag stamp is the load-bearing correctness property here. TaiYi's epoch flag re-casts the entire chart across a ~60-year gap, the `dem_toan` flag shifts both toan by a mark, the `cap` selects among four whole plates, and the than-variant flag changes displayed names; a chart that does not stamp every one of these cannot be reproduced or defended, and two schools cannot tell under which conventions it was cast (Claude-04 s7.2, strategy 4.4). Stamping them all, and deriving the cache key from them, is the technical expression of the cultural-fairness rule (strategy section 7) and the thing that makes the oracle gate meaningful - you can only claim a 100% match if you also say against which flags.

The oracle gate is the whole point of building the engine in Rust to the digit. TaiYi is the most calculation-heavy of the three systems and its base is a count near ten million reduced mod seventy-two, so the failure modes are silent arithmetic drift and mis-transcribed counting rules, not crashes. The only defense that scales is an exact match to kintaiyi across every flag combination and every time level, backed by the boundary and overflow tests the source explicitly calls for (Claude-04 s7.2). This is TaiYi's equivalent of the kinqimen gate for QiMen and the kinliuren gate for LiuRen.

## §3 - Contract (pipeline, envelope, flags)

### The engine pipeline (Claude-04 s7.1)

```
def cast_thai_at(dau_vao, flags, lich):            # lich = TASK-CORE-005 output (Dong Chi / Ha Chi anchor)
    tich  = tich_theo_cap(flags.cap, dau_vao, flags.epoch, lich)     # TASK-TAT-001 / TASK-TAT-004
    seat  = an_thai_at(tich.nhap_cuc, tich.duong_don)                # TASK-TAT-002
    ring  = THAP_LUC_THAN                                            # TASK-TAT-002
    tuong = bat_tuong(tich, seat, dau_vao.nam_chi, flags.dem_toan)   # TASK-TAT-003
    toan  = cac_toan(tuong, seat, flags.dem_toan)                    # TASK-TAT-003
    cach  = nhan_dien_cach_cuc(tuong, seat.thai_at_ring)             # TASK-TAT-005 (SHOULD; else empty)
    tt    = tinh_tam_tai(ban)                                        # TASK-TAT-005 (SHOULD; else None)
    ban   = ThaiAtBan { tich, seat, ring, tuong, toan, tam_tai: tt }
    return to_envelope(dau_vao, lich, ban, cach, flags)             # map into TASK-PLAT-002
```

### The s7.1 engine JSON (reproduced faithfully)

```json
{
  "he": "thai_at",
  "dau_vao": { "nam_ce": 2004, "cap": "nien_ke", "epoch": "kim_kinh" },
  "tich": { "tich_nien": 10155921, "nhap_cuc": 33, "can_chi": "甲申", "duong_don": true },
  "thai_at_cung": 1,
  "thap_luc_than": { },
  "bat_tuong": {
    "van_xuong":"...", "thuy_kich":"...",
    "chu_dai_tuong":"...", "khach_dai_tuong":"...",
    "chu_tham_tuong":"...", "khach_tham_tuong":"...",
    "ke_than":"..."
  },
  "cac_toan": {
    "chu_toan":0, "khach_toan":0,
    "chu_truong_doan":"truong", "khach_truong_doan":"doan"
  },
  "cach_cuc": ["掩", "格"],
  "tam_tai": "du",
  "co_truong_phai": {
    "epoch": "kim_kinh",
    "dem_toan": "truoc_thai_at"
  }
}
```

### Mapping into the PLAT-002 envelope

The flat s7.1 shape maps into the shared envelope thus: `he`, `dau_vao`, `lich_phap` (TASK-CORE-005), and `provenance` at the top level; `tich`, `thai_at_cung`, `thai_at_ring`, `thap_luc_than`, `bat_tuong`, `cac_toan`, `tam_tai` inside `ban`; the s7.1 `cach_cuc` string list becomes the envelope-level `cach_cuc` array of TASK-PLAT-002 `CachCuc` objects (TASK-TAT-005); `co_truong_phai` is the full flag set below.

### The flag set (Claude-04 s7.2)

```rust
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CoTruongPhaiTat {
    pub epoch: Epoch,                    // default KimKinh (TASK-TAT-001); re-casts the whole chart
    pub dem_toan: DemToan,               // default TruocThaiAt (TASK-TAT-003); shifts both toan by a mark
    pub cap: Cap,                        // nien / nguyet / nhat / thoi (TASK-TAT-004)
    pub bien_the_ten_than: BienTheTenThan,   // than-name variant handling (TASK-TAT-002)
}
// stamped whole into co_truong_phai as a sorted map, so the cache key is stable across languages
```

### Public types (`crates/cyberos-thaiat/src/`)

```rust
pub struct ThaiAtBan {
    pub tich: TichCap, pub thai_at_cung: u8, pub thai_at_ring: u8,
    pub thap_luc_than: [Than; 16], pub bat_tuong: BatTuong, pub cac_toan: CacToan,
    pub tam_tai: Option<TamTai>,         // filled by TASK-TAT-005; None if that SHOULD is not built
}

pub fn cast_thai_at(dau_vao: &DauVaoTat, flags: &CoTruongPhaiTat, lich: &LichPhap) -> LaSo;
pub fn cache_key(dau_vao: &DauVaoTat, flags: &CoTruongPhaiTat) -> String;   // year + cap + epoch + sorted flags
```

## §4 - Acceptance criteria

1. `cast_thai_at` runs the full pipeline and emits a valid TASK-PLAT-002 envelope with `he = "thai_at"`; the golden 2004 nien ke chart matches the s5.1 / s7.1 numbers (tich 10,155,921, cuc 33, Giap Than, duong don) and round-trips through the envelope.
2. The oracle gate passes 100% against kintaiyi per epoch (`kim_kinh`, `co_dien`) AND per time level (nien / nguyet / nhat / thoi ke); the fixture covers both dons and both `dem_toan` values.
3. `co_truong_phai` stamps `epoch`, `dem_toan`, `cap`, and the than-variant flag on every chart; a reproduction test recasts from the stamp alone and reproduces the chart byte-for-byte; an unstamped flag fails it.
4. `cache_key` is a stable hash of year + cap + epoch + the sorted flag set (TASK-PLAT-002); two casts with identical inputs and flags produce identical keys, and changing any stamped flag changes the key.
5. Boundary tests pass: the don switch at Dong Chi and Ha Chi, the cuc wrap (72 -> 1), and overflow tests on the large tich (nhat / thoi ke) all match kintaiyi.
6. The envelope's `ban` is opaque to non-`thai_at` readers (TASK-PLAT-002) and the interpretation branch never writes `ban` / `cach_cuc` / `lich_phap` / `co_truong_phai`.

## §5 - Verification

- Unit: the golden 2004 nien ke chart end to end; the flag-stamp reproduction test; the cache-key stability / sensitivity test.
- Oracle: `tests/engine_kintaiyi.rs` loads `fixtures/engine_kintaiyi_all_flags.csv` (generated once from kintaiyi across the epoch x cap x dem_toan product, many years, both dons, with day / hour probes) and asserts the whole chart - tich, cuc, Thai At seat, sixteen than, eight tuong, both toan, the cach set, tam tai - matches exactly. This is the TaiYi stop-ship gate (RISK-2), and it MUST run in CI. It composes the TASK-TAT-001..005 oracle fixtures into one engine-level gate and stands on TASK-CORE-006's harness for the shared solstice anchors.
- Property: over a wide year span and the full flag product, `cast_thai_at` is total and deterministic (same input + flags -> byte-identical chart); the cache key round-trips.
- Boundary: the don switch (both solstices), the cuc wrap, and the large-tich overflow (nhat / thoi ke) each have a dedicated case vs kintaiyi.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-thaiat -- -D warnings`, `cargo test -p cyberos-thaiat`, plus the kintaiyi oracle gate in CI.

## §6 - Implementation skeleton

1. `ban.rs`: the `ThaiAtBan` type and its serialization into the TASK-PLAT-002 `ban` slot for `he = "thai_at"`; the s7.1 -> envelope mapping.
2. `engine.rs`: `cast_thai_at` running the TASK-TAT-001..005 pipeline in order; the `CoTruongPhaiTat` flag set with the s7.2 defaults; `cache_key` per TASK-PLAT-002 (year + cap + epoch + sorted flags).
3. Wire `lich_phap` from TASK-CORE-005 (the Dong Chi / Ha Chi anchor, shared with QiMen / LiuRen) into the envelope and into TASK-TAT-004's nhat / thoi ke.
4. Fill the envelope `cach_cuc` array from TASK-TAT-005's `map_to_envelope_cach_cuc`; set `tam_tai` in `ban`; leave both empty / None if the SHOULD TASK-TAT-005 / TASK-TAT-004 levels are not yet built (the MUST nien ke path still emits a valid envelope).
5. Generate the all-flags kintaiyi fixture once (documented script, not run in CI) across the epoch x cap x dem_toan product and commit; wire the engine oracle, reproduction, cache-key, boundary, and overflow tests.

## §7 - Dependencies

Hard depends on TASK-TAT-003 (the tuong and toan - the MUST spine that makes a chart meaningful) and TASK-CORE-006 (the oracle cross-check harness and the shared solstice anchors). Soft-consumes TASK-TAT-004 (the nguyet / nhat / thoi ke levels - without them the assembly still emits and gates nien ke; with them the gate extends to all four levels) and TASK-TAT-005 (the cach set and tam tai - without them the envelope `cach_cuc` is empty and `tam_tai` is None, still valid). Transitively stands on TASK-TAT-001 (tich / reductions / epoch), TASK-TAT-002 (ring / seat), and TASK-PLAT-002 (the envelope, the version rule, the cache-key rule). Blocks TASK-CHART-003 (the TaiYi chart view renders this envelope: cuu cung, sixteen than, tuong). Soft-feeds STRAT-004 (cross-system validate can add TaiYi as a third opinion once this lands) and EDU-002 (the TaiYi engine as an auto-grader at curriculum level 3).

## §8 - Example payloads

Full envelope for the 2004 nien ke golden chart (engine plates illustrative except the pinned s5.1 tich; the rest is asserted against kintaiyi):

```json
{ "envelope_version": 1, "he": "thai_at",
  "dau_vao": { "nam_ce": 2004, "cap": "nien_ke", "epoch": "kim_kinh" },
  "lich_phap": { "...": "from TASK-CORE-005; supplies the Dong Chi / Ha Chi anchor for the don" },
  "ban": {
    "tich": { "tich_nien": 10155921, "nhap_cuc": 33, "can_chi": "甲申", "duong_don": true },
    "thai_at_cung": 1, "thai_at_ring": 14,
    "thap_luc_than": { "...": "the 16-than ring, TASK-TAT-002" },
    "bat_tuong": { "van_xuong": 8, "thuy_kich": 3, "ke_than": 5,
                   "chu_dai_tuong": 4, "khach_dai_tuong": 12,
                   "chu_tham_tuong": 6, "khach_tham_tuong": 2 },
    "cac_toan": { "chu_toan": 15, "khach_toan": 8,
                  "chu_truong_doan": "truong", "khach_truong_doan": "doan" },
    "tam_tai": "du"
  },
  "cach_cuc": [
    { "id": "taiyi_yem", "name": "掩", "cung": 1, "polarity": "hung", "citations": ["Thong Tong Bao Giam q6"] },
    { "id": "taiyi_cach", "name": "格", "cung": 5, "polarity": "trung", "citations": ["Kim Kinh Thuc Kinh"] }
  ],
  "co_truong_phai": { "epoch": "kim_kinh", "dem_toan": "truoc_thai_at",
                      "cap": "nien_ke", "bien_the_ten_than": "chuan" },
  "provenance": { "engine": "tat", "engine_version": "0.1.0", "cast_at": "...", "cache_key": "..." } }
```

## §9 - Open questions

- Whether `ban` should become a tagged union in the shared `laso-envelope` crate now that all three engines exist (the deferral in TASK-PLAT-002 §9 named TAT-006 as the revisit point). Default: keep `ban` opaque (`serde_json::Value` in the shared crate, strongly typed `ThaiAtBan` in this crate); revisit only if the interpretation branch needs a cross-engine typed reader.
- The cache-key granularity for nhat / thoi ke: nien / nguyet key cleanly by year + cap + epoch, but hour-level casts vary within a day. Default: include the casting instant at the cap's granularity in the key (per TASK-PLAT-002's "dau_vao rounded to the casting granularity"); confirm the rounding with PLAT-006.
- Whether kintaiyi implements both `dem_toan` conventions and both epochs identically to our reading; if it covers only one, the other flag combination is gated against a second source or documented as flagged-but-unverified, never silently shipped as matched.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Bespoke envelope shape | engine invents its own JSON instead of PLAT-002 | envelope schema validation fails; assembly must fill the shared shape |
| Unstamped flag | chart cast under one flag, stamped as another (or not at all) | reproduction test recasts from the stamp and diverges -> fail (RISK-2) |
| Oracle drift on a flag combo | a cuc / tuong / toan off under some epoch x cap | the all-flags kintaiyi gate fails per combo; stop-ship |
| Non-deterministic cache key | flags hashed in map order | cross-language key-equality test fails (TASK-PLAT-002) |
| AI writes to ban / cach_cuc | interpretation branch mutates the chart | forbidden by read-only consumers; no setter exposed |
| Large-tich overflow at hour level | nhat / thoi ke tich in a narrow int | overflow test on the large tich fails; use u64 per TASK-TAT-004 |

## §11 - Notes

This task closes the TaiYi engine: it is the third and last of the three casting engines (QiMen QMDG-006, LiuRen LN-006, TaiYi TAT-006), each ending in the same shape - assemble the slices, fill the PLAT-002 envelope, stamp every flag, gate 100% against its oracle (kinqimen / kinliuren / kintaiyi). TaiYi's acceptance is uniquely two-dimensional - per epoch AND per time level - because it carries both the epoch school split and the four-plate structure, so the all-flags fixture is larger than the other two engines' (Claude-04 s7.2). Keep the engine one cargo-testable crate: TASK-TAT-001 owned the birth, TASK-TAT-002..005 extended it, and this task only assembles and gates - it adds no new casting rule, so any oracle divergence points back into an upstream slice, not here. Because TaiYi speaks to the largest matters, the deterministic facts stop at this envelope; the cited, cautious, human-gated reading is TASK-RAG-003's, and it never writes these fields (strategy 4.4, section 7, tat module notes).
