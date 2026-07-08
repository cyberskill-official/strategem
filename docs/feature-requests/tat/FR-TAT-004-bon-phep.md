---
id: FR-TAT-004
title: "Bon phep - the four time-level calculations nien / nguyet / nhat / thoi ke, each with its own tich formula reduced mod 72 into a cuc (nien = 10,153,917 + CE; nguyet = tich nien x 12 with leap-month handling; nhat anchored on Dong Chi via 365.2425; thoi = tich nhat x 12), one hour = one cuc, six days = one 72-cuc circuit; reuses FR-TAT-001 reductions and FR-TAT-002 seating; extends the ban for he=thai_at"
module: TAT
priority: SHOULD
status: ready_to_implement
phase: P2
slice: 3
lang: rust
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-04 s5, Claude-04 s5.1, Grok-30]
related_frs: [FR-TAT-001, FR-TAT-002, FR-TAT-003, FR-TAT-006, FR-CORE-001, FR-CORE-005, FR-PLAT-002]
depends_on: [FR-TAT-002]
blocks: [FR-TAT-006]
new_paths:
  - crates/cyberos-thaiat/src/bonphep.rs
  - crates/cyberos-thaiat/tests/bonphep_oracle.rs
  - crates/cyberos-thaiat/tests/fixtures/bonphep_kintaiyi.csv
---

## §1 - Description (BCP-14 normative)

This FR generalizes the Thai At chart from one plate per year to four plates keyed to four time granularities: nien ke (year), nguyet ke (month), nhat ke (day), thoi ke (hour). It extends the `cyberos-thaiat` crate, reusing the epoch / reduction machinery of FR-TAT-001 and the ring seating of FR-TAT-002; only the tich formula and the don anchor differ per level.

The module SHALL compute a tich for each of the four levels and reduce it mod seventy-two into a cuc (Claude-04 s5): nien ke tich = 10,153,917 + CE, cuc = tich nien mod 72 (the FR-TAT-001 formula, identical); nguyet ke tich = tich nien times twelve with its own leap-month handling, cuc = tich nguyet mod 72; nhat ke anchored on Dong Chi with tich nhat = accumulated-days-from-the-Giap-Ty-anchor times 365.2425, cuc = (tich nhat mod 72) + 1 then advanced by day; thoi ke tich = tich nhat times twelve, cuc = (tich thoi mod 72) + 1 then advanced by hour. One hour SHALL be one cuc and six days SHALL close one seventy-two-cuc circuit.

The module SHALL take the don direction for nhat ke and thoi ke from the Dong Chi / Ha Chi anchor (Claude-04 s5.2): after Dong Chi duong don runs forward (thuan), after Ha Chi am don runs backward (nghich). The Dong Chi and Ha Chi instants SHALL come from the calendar core (FR-CORE-001 via FR-CORE-005), the same solstice instants FR-TAT-001 keys its don off, so TaiYi and the calendar core MUST agree on the solstice to the second. The nguyet ke leap-month handling SHALL use a dedicated tich nguyet solve, not a naive month multiply.

Each level SHALL reduce to the same 1..=72 cuc contract as FR-TAT-001 (a tich divisible by seventy-two maps to 72, not 0, before the level-specific "+1" where the source calls for it). The module SHALL feed the resulting cuc and don into FR-TAT-002 seating (and, in the assembly, FR-TAT-003 tuong) so that any of the four levels produces a full chart. The module SHALL extend the `dau_vao.cap` selector and stamp the chosen level; the oracle is kintaiyi, which supports all four levels.

## §2 - Why this design (rationale for humans)

Thai At is not a single yearly plate: the same machine casts at four resolutions so a reading can range from the multi-year backdrop (nien ke) down to the hour (thoi ke), and the user picks the level that matches the scope of the question (Claude-04 s5.2). Because all four reduce to a cuc mod seventy-two and then seat Thai At the same way, the right design is to reuse FR-TAT-001's reduction and FR-TAT-002's seating unchanged and vary only the tich formula and the don anchor - which is why this FR is small (SHOULD, 8h) despite adding three whole new plates.

The nhat ke and thoi ke anchors are the reason this FR touches the calendar core. Their tich is measured from Dong Chi, and the don flips at Dong Chi (forward) and Ha Chi (backward), so the solstice instant has to be the exact same instant FR-TAT-001 and FR-CORE-001 use; a disagreement of even a day at the anchor shifts the cuc and re-casts the plate (RISK-1 propagation). Stating the shared-anchor requirement here keeps the four levels consistent with the yearly plate and with QiMen / LiuRen, which read the same solstices.

Nguyet ke gets a dedicated leap-month solve rather than a flat times-twelve because the lunisolar calendar inserts leap months unevenly; a naive multiply would drift the month tich and the cuc with it. The "+1 then advance" on nhat ke and thoi ke is transcribed verbatim from the s5.2 table rather than rationalized, and pinned to kintaiyi, because the small constant is exactly the kind of detail that is easy to drop and hard to notice without the oracle.

## §3 - Contract (algorithm and types)

### The four calculations (Claude-04 s5.2, reproduced faithfully)

| Phep | Tich | So cuc |
|---|---|---|
| Nien ke 年計 | Tich nien = 10.153.917 + nam CE | Tich nien mod 72 |
| Nguyet ke 月計 | Tich nguyet = tich nien x 12 (chinh thang nhuan rieng) | Tich nguyet mod 72 |
| Nhat ke 日計 | Lay Dong Chi lam moc; tich nhat = nam tich Giap Ty x 365,2425 | Tich nhat mod 72 cong 1, roi tien theo ngay |
| Thoi ke 時計 | Tich thoi = tich nhat x 12 | Tich thoi mod 72 cong 1, roi tien theo gio |

One hour is one cuc; six days is seventy-two cuc, closing a circuit. Nhat ke and thoi ke anchor on Dong Chi: after Dong Chi duong don thuan, after Ha Chi am don nghich. Nguyet ke handles the leap month through its own tich nguyet solve.

### Nien ke worked example (Claude-04 s5.1, ties to FR-TAT-001)

Year 2004: tich nien = 10,153,917 + 2,004 = 10,155,921; mod 60 = 21 (Giap Than); mod 72 = 33 (duong don, cuc 33). Identical to the FR-TAT-001 golden numbers - nien ke IS FR-TAT-001's path, listed here as the first of the four levels.

### Pseudocode

```
def tich_theo_cap(cap, dau_vao, epoch, lich):     # lich supplies Dong Chi / Ha Chi (FR-CORE-005)
    if cap == "nien_ke":
        tich = tich_nien(dau_vao.nam_ce, epoch)                      # FR-TAT-001
        cuc  = map_1_72(tich % 72)
        don  = duong_don_from_solstice(dau_vao, lich)
    elif cap == "nguyet_ke":
        tich = tich_nguyet(dau_vao, epoch)                           # tich nien x 12 + leap-month solve
        cuc  = map_1_72(tich % 72)
        don  = duong_don_from_solstice(dau_vao, lich)
    elif cap == "nhat_ke":
        tich = tich_nhat(dau_vao, lich.dong_chi_anchor)              # days-from-anchor x 365.2425
        cuc  = map_1_72(tich % 72) + 1                               # +1, then advance by day
        don  = after_dong_chi(dau_vao, lich)                         # thuan after Dong Chi, nghich after Ha Chi
    elif cap == "thoi_ke":
        tich = tich_nhat(dau_vao, lich.dong_chi_anchor) * 12
        cuc  = map_1_72(tich % 72) + 1                               # +1, then advance by hour
        don  = after_dong_chi(dau_vao, lich)
    return TichCap(cap, tich, cuc, don)                              # cuc + don then feed FR-TAT-002 seating
```

### Public types (`crates/cyberos-thaiat/src/`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Cap { NienKe, NguyetKe, NhatKe, ThoiKe }

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TichCap {
    pub cap: Cap,
    pub tich: u64,          // tich nien / nguyet / nhat / thoi (u64: nhat/thoi are large)
    pub nhap_cuc: u8,       // 1..=72 (after the level-specific +1 where the source calls for it)
    pub duong_don: bool,    // from the Dong Chi / Ha Chi anchor
}

pub fn tich_theo_cap(cap: Cap, dau_vao: &DauVaoTat, epoch: Epoch, lich: &LichPhap) -> TichCap;
```

## §4 - Acceptance criteria

1. `tich_theo_cap(NienKe, 2004, KimKinh, ...)` reproduces the s5.1 numbers exactly: tich 10,155,921, cuc 33, Giap Than, duong don - identical to FR-TAT-001.
2. Nguyet ke tich is tich nien times twelve adjusted by the leap-month solve (not a flat multiply); a leap-month year and a common year are both checked against kintaiyi.
3. Nhat ke and thoi ke apply the `+1` after the mod-72 reduction and advance by day / hour respectively; a probe just after Dong Chi runs duong don and one just after Ha Chi runs am don, both matching kintaiyi.
4. All four tich use `u64`; nhat ke and thoi ke (the large ones, days x 365.2425 and x 12) neither overflow nor lose precision; a wide date range is checked.
5. The 1..=72 mapping holds at each level (a tich divisible by 72 maps to 72, not 0, before any level-specific `+1`).
6. The Dong Chi / Ha Chi instant used here is byte-identical to the one FR-TAT-001 and FR-CORE-001 use; a cross-check test asserts the same anchor.

## §5 - Verification

- Unit: the s5.1 nien ke numbers; a leap-month nguyet ke; a nhat ke and thoi ke probe on each side of Dong Chi and Ha Chi.
- Property: over a wide date span, all four tich are exact under `u64` (no overflow, no f64 rounding on the 365.2425 term beyond the documented tolerance); each cuc is 1..=72.
- Oracle: `tests/bonphep_oracle.rs` loads `fixtures/bonphep_kintaiyi.csv` (generated once from kintaiyi across all four levels and both epochs, spanning years and including day / hour probes) and asserts the tich, cuc, and don match exactly per level. This extends the FR-TAT-006 gate from per-epoch to per-epoch-and-per-level.
- Boundary: the don switch at Dong Chi and Ha Chi (nhat / thoi ke), the six-day / seventy-two-cuc circuit close, the cuc wrap (72 -> 1), and a leap-month boundary for nguyet ke.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-thaiat -- -D warnings`, `cargo test -p cyberos-thaiat`.

## §6 - Implementation skeleton

1. `bonphep.rs`: the `Cap` enum, the four tich formulas, and `tich_theo_cap` reusing FR-TAT-001's `tich_nien` and 1..=72 mapping.
2. Nguyet ke: the leap-month tich nguyet solve (consult FR-CORE for the lunisolar month index); do not flat-multiply.
3. Nhat ke / thoi ke: take the Dong Chi anchor from `lich` (FR-CORE-005), apply the `days x 365.2425` and `x 12` tich, the `+1` and advance-by-day / hour, and the after-Dong-Chi / after-Ha-Chi don.
4. Route the resulting `(cuc, don)` into FR-TAT-002 seating so any level yields a full chart; keep nien ke bit-identical to FR-TAT-001.
5. Generate the kintaiyi four-level fixture once (documented script, not run in CI) and commit; wire the oracle, property, and boundary tests.

## §7 - Dependencies

Depends on FR-TAT-002 (seating the cuc / don on the ring) and transitively on FR-TAT-001 (the tich nien formula, the 1..=72 mapping, the epoch flag). Needs the Dong Chi / Ha Chi instants and the lunisolar month index from the calendar core (FR-CORE-001 via FR-CORE-005), reached transitively through FR-TAT-001's CORE-005 dependency. Soft-feeds FR-TAT-006: the assembly's MUST path (nien ke) does not hard-require this FR, but the SHOULD extension of the oracle gate to all four levels does - so this FR blocks the per-level portion of the FR-TAT-006 gate, not the yearly assembly itself. Emits into the FR-PLAT-002 envelope via `dau_vao.cap`.

## §8 - Example payloads

`dau_vao` + `tich` fragment for a thoi ke (hour-level) cast (values illustrative; pinned to kintaiyi):

```json
{ "dau_vao": { "nam_ce": 2004, "cap": "thoi_ke", "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "epoch": "kim_kinh" },
  "ban": {
    "tich": { "cap": "thoi_ke", "tich": 44476835160, "nhap_cuc": 12, "duong_don": true },
    "thai_at_cung": 3, "thai_at_ring": 2,
    "thap_luc_than": { "...": "from FR-TAT-002" },
    "bat_tuong": { "...": "from FR-TAT-003, cast at this level's cuc" },
    "cac_toan": { "...": "from FR-TAT-003" }
  },
  "lich_phap": { "...": "supplies the Dong Chi / Ha Chi anchor (FR-CORE-005)" } }
```

## §9 - Open questions

- The nhat ke "nam tich Giap Ty x 365,2425" term (s5.2) mixes a whole-day accumulation with a mean-tropical-year constant; whether tich nhat should be integer days from the anchor or the 365.2425-scaled figure is resolved against kintaiyi before lock, since it drives the mod-72 cuc.
- Nguyet ke leap-month handling is stated only as "chinh thang nhuan rieng" (its own leap-month solve); the exact rule (which leap months count, how the month index maps to tich nguyet) is taken from FR-CORE's lunisolar month module and confirmed against kintaiyi.
- Whether the `+1` on nhat / thoi ke applies before or after the 1..=72 remap is transcribed as "mod 72, then +1"; a boundary case at a tich divisible by 72 pins the order against the oracle.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Nhat / thoi ke tich overflow | days x 365.2425 x 12 in a narrow int or f32 | use u64 and the documented precision path; wide-range test asserts exact cuc |
| Wrong don at a solstice probe | Dong Chi / Ha Chi anchor swapped or off by a day | boundary test on each side of both solstices vs kintaiyi |
| Nguyet ke leap-month drift | flat times-twelve without the leap solve | leap-year nguyet ke test diverges from kintaiyi |
| Missing +1 on nhat / thoi ke | s5.2 constant dropped | per-level oracle fixture diverges |
| Solstice anchor disagrees with CORE | TaiYi computes its own solstice | cross-check test asserts the same instant as FR-TAT-001 / FR-CORE-001 |

## §11 - Notes

This FR is small because it reuses everything: FR-TAT-001's reduction and 1..=72 mapping, FR-TAT-002's seating, and (in the assembly) FR-TAT-003's tuong. It varies only the tich formula and the don anchor per level, so the four plates are one code path parameterized by `Cap`. Its value is coverage: it lifts the FR-TAT-006 oracle gate from per-epoch to per-epoch-and-per-time-level, which is the tat module's stated acceptance bar. The shared Dong Chi / Ha Chi anchor is the load-bearing detail - the same solstice instant TaiYi, QiMen, and LiuRen all read - so a divergence here is a RISK-1 calendar-core problem, not a TaiYi problem. Nien ke stays bit-identical to FR-TAT-001; the other three are the SHOULD extension.
