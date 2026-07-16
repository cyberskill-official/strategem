---
id: TASK-TAT-003
title: "Bat tuong + cac toan - place the eight generals (Van Xuong / Thuy Kich via ke than, chu/khach dai tuong + tham tuong) and compute chu toan / khach toan by walking the sixteen-than ring (chinh cung lends its number, gian than counts as one, stop before Thai At by default), with the truong/doan label and the dem_toan flag; extends the ban for he=thai_at"
module: TAT
priority: MUST
status: done
phase: P2
slice: 3
lang: rust
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-04 s4, Claude-04 s8.1, Grok-30]
related_frs: [TASK-TAT-001, TASK-TAT-002, TASK-TAT-004, TASK-TAT-005, TASK-TAT-006, TASK-PLAT-002]
depends_on: [TASK-TAT-002]
blocks: [TASK-TAT-005, TASK-TAT-006]
new_paths:
  - crates/cyberos-thaiat/src/battuong.rs
  - crates/cyberos-thaiat/src/toan.rs
  - crates/cyberos-thaiat/tests/battuong_oracle.rs
  - crates/cyberos-thaiat/tests/fixtures/battuong_kintaiyi.csv
---

## §1 - Description (BCP-14 normative)

This task computes the most distinctive part of a Thai At chart: the eight tuong (八將, eight generals) and the toan (算, counts) that measure the strength of host and guest. It extends the `cyberos-thaiat` crate, reading the sixteen-than ring and the Thai At seat from TASK-TAT-002 and the `nhap_cuc` / don from TASK-TAT-001.

The module SHALL place the eight tuong (Claude-04 s4.1): the two muc Van Xuong (文昌, the host / thien muc, the defending side, our side) and Thuy Kich (始擊, the guest / dia muc, the attacking side, the opponent); ke than (計神); the two dai tuong (chu dai tuong, khach dai tuong); and the two tham tuong (chu tham tuong, khach tham tuong). Van Xuong SHALL be placed from `nhap_cuc`: reduce `nhap_cuc` by eighteen until it is under eighteen, then count that many marks forward on the sixteen-than ring, starting from Vu duc at Than under duong don and from Lu than at Dan under am don, counting Can(乾) and Khon twice under duong don and Can(艮) and Ton twice under am don. Ke than SHALL be placed by the year chi (Claude-04 s4.2): duong don starts Lu than at Dan and runs forward through the twelve chi, am don starts from Than and runs backward. Thuy Kich SHALL be derived through ke than (ke than gia Can(艮), then shift palace), so ke than SHALL be computed before Thuy Kich.

The module SHALL compute chu toan (主算) from the Van Xuong mark and khach toan (客算) from the Thuy Kich mark by the same rule (Claude-04 s4.3): count forward around the ring, add the palace number of each chinh cung passed, count each gian than as one, and stop at the mark immediately before Thai At. The stop rule SHALL be a flag `dem_toan` with default `truoc_thai_at` (stop before Thai At, per the classical Thong Tong); the alternative `sau_thai_at` (stop after Thai At) SHALL be selectable and stamped. The chinh-cung-lends-its-number vs gian-than-counts-as-one distinction SHALL be read from the TASK-TAT-002 mark tags and applied consistently to both toan.

The module SHALL derive the dai tuong and tham tuong palaces from the toan (Claude-04 s4.4): for a toan in 1..9, 11..19, 21..29, 31..39 the dai tuong palace is the units digit; for a toan of exactly 10, 20, 30, 40 the dai tuong palace is `toan mod 9`; the tham tuong palace is the dai tuong palace times three, reduced back into a palace. The module SHALL also label each toan truong (長, at least eleven, the long / enduring count, tends to win) or doan (短, nine or below, the short / hurried count, tends to lose); the truong/doan of chu and khach toan is one of the four victory criteria consumed by TASK-TAT-005. The module SHALL extend the `ban` for `he = "thai_at"` with `bat_tuong` and `cac_toan`. The oracle is kintaiyi.

## §2 - Why this design (rationale for humans)

The toan are the numeric spine of a Thai At reading: everything about host-versus-guest strength (Claude-04 s6.2, TASK-TAT-005) hangs off chu toan and khach toan, and both are produced here by walking the ring. This is where the chinh cung vs gian than rule of TASK-TAT-002 does its real work: a chinh cung contributes its palace number, a gian than contributes one, and mixing the two conventions is the classic TaiYi bug (Claude-04 s3.3, s4.3). Because TASK-TAT-002 already tagged every mark, the loop here reads the tag rather than re-deciding it, which is the whole point of splitting the coordinate frame out first.

The `dem_toan` flag exists because the sources genuinely disagree on where the count stops: the classical Thong Tong stops at the mark before Thai At, but secondary sources count to the mark after (Claude-04 s4.3). That one-mark difference changes both toan and therefore the whole victory reading, so it cannot be hardcoded - it is a stamped school flag, like the epoch flag of TASK-TAT-001, so a chart is reproducible and two schools can see which convention was used (strategy 4.4, RISK-2).

The tuong placements read like a pile of small counting quirks - reduce by eighteen, count two marks twice, derive Thuy Kich through ke than - and they are, but each is deterministic and each is stated in the source, so the defense is faithful transcription plus the kintaiyi oracle. The truong/doan label is computed here rather than in TASK-TAT-005 because it is a pure function of a toan (the eleven / nine thresholds), so it belongs next to the toan; TASK-TAT-005 only reads it as one of its four criteria.

## §3 - Contract (algorithm and types)

### The eight tuong (Claude-04 s4.1, s8.1)

| Thanh phan | Vai tro |
|---|---|
| 文昌 Van Xuong | chu muc / thien muc; the host, our side, the defender |
| 始擊 Thuy Kich | khach muc / dia muc; the guest, the opponent, the attacker |
| 計神 Ke than | the marker to derive Thuy Kich; also one of the eight tuong |
| 主大將 Chu dai tuong | the host's great general (main force) |
| 客大將 Khach dai tuong | the guest's great general |
| 主參將 Chu tham tuong | the host's support general |
| 客參將 Khach tham tuong | the guest's support general |

### Van Xuong, ke than, Thuy Kich (Claude-04 s4.1 / s4.2, reproduced)

```
# Van Xuong: placed by nhap cuc; counts on the TASK-TAT-002 ring
def van_xuong(nhap_cuc, duong_don):
    r = nhap_cuc
    while r >= 18:                 # reduce by 18 until r < 18 (watch r == 0 boundary, see §9)
        r -= 18
    start = ring_of("武德@申") if duong_don else ring_of("呂申@寅")
    # count r marks forward; duong don counts 乾 and 坤 twice, am don counts 艮 and 巽 twice
    return count_forward(start, r, double = ("乾","坤") if duong_don else ("艮","巽"))

# Ke than: placed by the year chi
def ke_than(nam_chi, duong_don):
    if duong_don:  return count_forward_over_12_chi(start="呂申@寅", chi=nam_chi)   # forward
    else:          return count_backward_over_12_chi(start="@申",     chi=nam_chi)   # backward

# Thuy Kich: derived through ke than (ke than gia 艮, then shift palace)
def thuy_kich(ke_than_ring, duong_don):
    return shift_palace(gia(ke_than_ring, "艮"), duong_don)
```

### Chu toan and khach toan (Claude-04 s4.3, reproduced)

```
# Same rule for both; only the start mark differs.
def toan(start_ring, thai_at_ring, dem_toan = "truoc_thai_at"):
    total = 0
    mark  = start_ring
    stop  = mark_before(thai_at_ring) if dem_toan == "truoc_thai_at" else thai_at_ring
    while True:
        if is_chinh_cung(mark):  total += palace_number(mark)   # chinh cung lends its number
        else:                    total += 1                     # gian than counts as one
        if mark == stop: break
        mark = next_forward(mark)
    return total

chu_toan   = toan(van_xuong_ring, thai_at_ring, dem_toan)   # from Van Xuong
khach_toan = toan(thuy_kich_ring, thai_at_ring, dem_toan)   # from Thuy Kich
```

### Dai tuong, tham tuong, truong/doan (Claude-04 s4.4, reproduced)

```
def dai_tuong_cung(toan):
    if toan in (10, 20, 30, 40):  return toan % 9          # exact tens -> mod 9
    else:                          return toan % 10         # else -> units digit

def tham_tuong_cung(dt_cung):     return reduce_palace(dt_cung * 3)   # x3, back into 1..9

def truong_doan(toan):
    return "truong" if toan >= 11 else "doan"              # >=11 long/wins; <=9 short/loses
```

### Public types (`crates/cyberos-thaiat/src/`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TruongDoan { Truong, Doan }                 // >= 11 vs <= 9

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DemToan { TruocThaiAt, SauThaiAt }          // stop before (default) vs after Thai At

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BatTuong {
    pub van_xuong: u8, pub thuy_kich: u8, pub ke_than: u8,   // ring indices 0..=15
    pub chu_dai_tuong: u8, pub khach_dai_tuong: u8,
    pub chu_tham_tuong: u8, pub khach_tham_tuong: u8,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CacToan {
    pub chu_toan: u16, pub khach_toan: u16,
    pub chu_truong_doan: TruongDoan, pub khach_truong_doan: TruongDoan,
}

pub fn van_xuong(nhap_cuc: u8, duong_don: bool) -> u8;
pub fn ke_than(nam_chi: u8, duong_don: bool) -> u8;
pub fn thuy_kich(ke_than_ring: u8, duong_don: bool) -> u8;
pub fn tinh_toan(start_ring: u8, thai_at_ring: u8, dem: DemToan) -> u16;
pub fn dai_tuong_cung(toan: u16) -> u8;
pub fn tham_tuong_cung(dai_tuong_cung: u8) -> u8;
pub fn truong_doan(toan: u16) -> TruongDoan;
```

## §4 - Acceptance criteria

1. `van_xuong` reduces `nhap_cuc` below eighteen, starts from Vu duc at Than (duong) or Lu than at Dan (am), and applies the double-count of Can(乾)/Khon (duong) or Can(艮)/Ton (am); the s5.1 worked chart (2004, cuc 33, duong don) matches kintaiyi.
2. `ke_than` runs forward from Dan (duong) or backward from Than (am) over the twelve chi; `thuy_kich` is derived through ke than (gia Can(艮), shift palace) and matches kintaiyi.
3. `tinh_toan` adds a chinh cung's palace number and a gian than's one (tags read from TASK-TAT-002), and stops before Thai At under `truoc_thai_at`; switching to `sau_thai_at` changes both toan; the flag value is stamped into `co_truong_phai`.
4. `dai_tuong_cung` returns the units digit for 1..9 / 11..19 / 21..29 / 31..39 and `toan mod 9` for 10 / 20 / 30 / 40; `tham_tuong_cung` is the dai tuong palace times three reduced into 1..9.
5. `truong_doan` is truong for toan >= 11 and doan for toan <= 9; both chu and khach are labeled; a unit test pins the eleven / nine thresholds including the exact boundaries 9, 10, 11.
6. The emitted `ban.bat_tuong` and `ban.cac_toan` round-trip through the la so envelope (TASK-PLAT-002) under `he = "thai_at"`.

## §5 - Verification

- Unit: the s5.1 chart (2004) tuong and toan; the dai/tham tuong arithmetic table; the truong/doan thresholds (9 -> doan, 10 -> doan, 11 -> truong).
- Property: over 1..=72 x {duong, am}, `van_xuong`, `ke_than`, `thuy_kich` are total and land on valid ring indices; `tinh_toan` gives identical results whether the tag is read from TASK-TAT-002 or recomputed (guards against tag drift); switching `dem_toan` changes the toan by exactly the before/after mark's contribution.
- Oracle: `tests/battuong_oracle.rs` loads `fixtures/battuong_kintaiyi.csv` (generated once from kintaiyi, per epoch, both dons, both `dem_toan` values, many years) and asserts every tuong ring index and both toan match exactly. Central to the TASK-TAT-006 100% gate.
- Boundary: `nhap_cuc` a multiple of eighteen (the r reduction edge), the cuc wrap (72 -> 1), and a toan of exactly 10 / 20 / 30 / 40 (the mod-9 branch of `dai_tuong_cung`).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-thaiat -- -D warnings`, `cargo test -p cyberos-thaiat`.

## §6 - Implementation skeleton

1. `battuong.rs`: `van_xuong` (the reduce-by-eighteen count with the double-count marks), `ke_than` (forward/backward over the twelve chi), `thuy_kich` (derive through ke than), and the two dai/tham tuong placements reusing TASK-TAT-002's chinh-cung-mark correspondence.
2. `toan.rs`: `tinh_toan` reading the chinh-cung / gian-than tag from TASK-TAT-002, the `DemToan` flag, `dai_tuong_cung`, `tham_tuong_cung`, `truong_doan`.
3. Wire the `dem_toan` flag into the TASK-TAT-001 flag set (default `truoc_thai_at`); TASK-TAT-006 stamps it.
4. Extend the `he = "thai_at"` `ban` with `bat_tuong` and `cac_toan`; keep TASK-TAT-002's `thap_luc_than` and seat intact.
5. Generate the kintaiyi tuong / toan fixture once (documented script, not run in CI) across both `dem_toan` values and commit; wire the oracle, property, and boundary tests.

## §7 - Dependencies

Depends on TASK-TAT-002 (the sixteen-than ring, the chinh-cung / gian-than tags, and the Thai At seat) and transitively on TASK-TAT-001 (`nhap_cuc`, don, the flag set). Blocks TASK-TAT-005 (cach cuc reads the tuong positions and the toan; the truong/doan label is one of its four criteria) and TASK-TAT-006 (assembly + the oracle gate). Emits into the TASK-PLAT-002 envelope.

## §8 - Example payloads

`ban` fragment for a cast (values illustrative; pinned to kintaiyi by the oracle):

```json
{ "ban": {
    "tich": { "tich_nien": 10155921, "nhap_cuc": 33, "can_chi": "甲申", "duong_don": true },
    "thai_at_cung": 1, "thai_at_ring": 14,
    "thap_luc_than": { "...": "from TASK-TAT-002" },
    "bat_tuong": {
      "van_xuong": 8, "thuy_kich": 3, "ke_than": 5,
      "chu_dai_tuong": 4, "khach_dai_tuong": 12,
      "chu_tham_tuong": 6, "khach_tham_tuong": 2
    },
    "cac_toan": {
      "chu_toan": 15, "khach_toan": 8,
      "chu_truong_doan": "truong", "khach_truong_doan": "doan"
    }
  },
  "co_truong_phai": { "epoch": "kim_kinh", "dem_toan": "truoc_thai_at" } }
```

## §9 - Open questions

- Van Xuong r reduction at a multiple of eighteen: repeated subtraction can leave r = 0. Default: treat r = 0 as "no forward step" (stay on the start mark) pending the oracle; a boundary test at `nhap_cuc` in {18, 36, 54, 72} decides, and the rule is corrected to match kintaiyi if it diverges.
- The double-count of Can/Khon (duong) or Can(艮)/Ton (am) during the Van Xuong count is transcribed from s4.1; whether the doubled mark consumes two steps or is merely visited twice without an extra step is resolved by the oracle fixture before lock.
- `dem_toan` default is `truoc_thai_at` (classical Thong Tong, Claude-04 s4.3). The `sau_thai_at` reading is a real secondary tradition and stays behind the flag; if the oracle kintaiyi implements one convention only, the other is tested against a second source or left flagged-but-unverified with a note.
- Thuy Kich "gia Can(艮), shift palace" is stated compactly in s4.1; the exact shift (which direction, how many palaces) is pinned to kintaiyi, not guessed.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Chinh cung / gian than mixed in the toan | loop re-decides the tag instead of reading TASK-TAT-002 | property test: reading the tag vs recomputing gives identical toan; oracle diverges otherwise |
| dem_toan hardcoded | count always stops before (or after) Thai At | switching the flag must change both toan; unstamped flag fails the reproduction test |
| Van Xuong double-count dropped | Can/Khon (or Can(艮)/Ton) not counted twice | s5.1 chart and the oracle fixture diverge |
| dai_tuong_cung wrong branch | units digit taken for 10/20/30/40 | dedicated test at exact tens asserts the mod-9 branch |
| truong/doan off by one | threshold set at 10 instead of 11 | boundary test at 9 / 10 / 11 pins doan, doan, truong |
| Ke than computed after Thuy Kich | ordering inverted | Thuy Kich must read a ke than already placed; a unit test asserts the dependency order |

## §11 - Notes

This is the heaviest computational slice of the TaiYi engine and the one most exposed to the classic counting bug, which is exactly why TASK-TAT-002 pre-tagged the ring: the toan loop here reads the chinh-cung / gian-than tag rather than re-deriving it (Claude-04 s3.3, s4.3). Two flags meet here - the epoch from TASK-TAT-001 and `dem_toan` from this task - and both are stamped by TASK-TAT-006; a one-mark stop difference re-casts the victory reading, so `dem_toan` is load-bearing (RISK-2). The truong/doan label lives with the toan because it is a pure function of it; TASK-TAT-005 consumes it as one of the four victory criteria. Faithful transcription against the s4 pseudocode plus the kintaiyi oracle, over both dons and both `dem_toan` values, is the acceptance bar.
