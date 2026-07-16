---
id: TASK-LN-001
title: "Thien dia ban + nguyet tuong - fixed dia ban ring, rotating thien ban by gia nguyet tuong, nguyet tuong changes at trung khi, thien can ky cung; emits into the la so ban for he=luc_nham"
module: LN
priority: MUST
status: done
phase: P1
slice: 1
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-02 s2, Grok-29]
related_frs: [TASK-LN-002, TASK-LN-003, TASK-LN-004, TASK-LN-006, TASK-CORE-001, TASK-CORE-005, TASK-PLAT-002]
depends_on: [TASK-CORE-005]
blocks: [TASK-LN-002, TASK-LN-003, TASK-LN-004, TASK-LN-006]
new_paths:
  - crates/cyberos-luchnham/Cargo.toml
  - crates/cyberos-luchnham/src/lib.rs
  - crates/cyberos-luchnham/src/chi.rs
  - crates/cyberos-luchnham/src/nguyettuong.rs
  - crates/cyberos-luchnham/src/thiendiaban.rs
  - crates/cyberos-luchnham/src/kycung.rs
  - crates/cyberos-luchnham/src/flags.rs
  - crates/cyberos-luchnham/tests/thiendiaban_oracle.rs
  - crates/cyberos-luchnham/tests/fixtures/thiendiaban_kinliuren.csv
---

## §1 - Description (BCP-14 normative)

This task builds the root state of every Dai Luc Nham chart: the two-layer thien dia ban and the nguyet tuong that rotates it. It owns the birth of the `cyberos-luchnham` crate; TASK-LN-002..006 extend it.

The module SHALL model the dia ban (地盤) as a fixed twelve-chi ring in canonical order (Ty..Hoi) and the thien ban (天盤) as the same twelve chi rotated by the cast. It SHALL compute the rotation by nguyet tuong gia thoi (月將加時): place the nguyet tuong chi over the dia ban palace of the hour of consultation (gio chiem), then fill the remaining eleven thien ban chi in forward chi order. The relationship is a single modular offset: the thien ban chi sitting over dia ban palace X SHALL equal `(nguyet_tuong + X - gio_chiem) mod 12`.

The module SHALL derive nguyet tuong from the current trung khi (中氣), not from the jie (節). This is the single most error-prone point in LiuRen: month-pillar boundaries follow jie, but nguyet tuong changes at trung khi, and the two differ by roughly half a month. The module SHALL read the TrungKhi-kind term in force from the CORE calendar object (TASK-CORE-001 distinguishes Jie from TrungKhi), never a jie boundary.

The module SHALL implement thien can ky cung (天干寄宮): because the board carries only twelve chi but the day stem is a thien can, each of the ten can lodges in a fixed chi palace so it can enter chart construction; the four cardinal chi (Ty Ngo Mao Dau) hold no can.

The module SHALL emit its result (dia ban, thien ban, nguyet tuong, gio chiem, board state) into the `ban` slot of the la so JSON envelope (TASK-PLAT-002) under `he = "luc_nham"`, and SHALL stamp the LN flag set into `co_truong_phai`. The oracle for the whole engine is kinliuren.

## §2 - Why this design (rationale for humans)

The entire information content of a LiuRen consultation is how far the thien ban has turned relative to the fixed dia ban (Claude-02 s2.1). Everything downstream - the four khoa, the three truyen, the twelve thien tuong - is read off this one rotated board, so an error here is not local: it propagates through the whole chart exactly as a CORE calendar error propagates across all three engines. That is why the thien dia ban is its own slice with its own oracle test before any lesson or truyen is built.

Nguyet tuong is called out separately because it is the classic silent bug. Nguyet tuong is the sun's apparent zodiacal position reduced to a chi, and it steps at the twelve trung khi (Vu Thuy, Xuan Phan, ...), whereas the can-chi month steps at the twelve jie (Lap Xuan, Kinh Trap, ...). Take the wrong marker and the nguyet tuong is off by one, the thien ban is off, and every khoa and truyen is wrong while still looking plausible. Reading the trung khi from CORE (which computes term instants from solar longitude, TASK-CORE-001) keeps LiuRen and the calendar core on the same clock.

Thien can ky cung exists because the board has twelve chi seats and the day stem is a stem; without a fixed lodging rule the first lesson could not be built. The rule is a closed lookup table with no school dispute, so it is pure data.

## §3 - Contract (algorithm and types)

### The twelve chi ring (canonical index)

Index 0..11 in fixed order. All rotation arithmetic is modulo twelve over this order.

| idx | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| chi | 子 Ty | 丑 Suu | 寅 Dan | 卯 Mao | 辰 Thin | 巳 Ti | 午 Ngo | 未 Mui | 申 Than | 酉 Dau | 戌 Tuat | 亥 Hoi |

The dia ban is this array, fixed. The traditional compass drawing (Ty at the bottom, Ngo at the top, Mao at the left, Dau at the right) is a rendering concern for CHART-002; the engine works only in the index model.

### Nguyet tuong by trung khi (Claude-02 s2.2, reproduced)

Nguyet tuong changes when the sun enters each trung khi. Table (after the given trung khi, the nguyet tuong chi holds until the next):

| Sau trung khi | Nguyet tuong | Ten tuong | Hoang kinh |
|---|---|---|---|
| Vu Thuy 雨水 | 亥 Hoi | 登明 Dang Minh | 330-360 |
| Xuan Phan 春分 | 戌 Tuat | 河魁 Ha Khoi | 0-30 |
| Coc Vu 穀雨 | 酉 Dau | 從魁 Tong Khoi | 30-60 |
| Tieu Man 小滿 | 申 Than | 傳送 Truyen Tong | 60-90 |
| Ha Chi 夏至 | 未 Mui | 小吉 Tieu Cat | 90-120 |
| Dai Thu 大暑 | 午 Ngo | 勝光 Thang Quang | 120-150 |
| Xu Thu 處暑 | 巳 Ti | 太乙 Thai At | 150-180 |
| Thu Phan 秋分 | 辰 Thin | 天罡 Thien Cuong | 180-210 |
| Suong Giang 霜降 | 卯 Mao | 太衝 Thai Xung | 210-240 |
| Tieu Tuyet 小雪 | 寅 Dan | 功曹 Cong Tao | 240-270 |
| Dong Chi 冬至 | 丑 Suu | 大吉 Dai Cat | 270-300 |
| Dai Han 大寒 | 子 Ty | 神后 Than Hau | 300-330 |

### Gia nguyet tuong - the thien ban rotation (Claude-02 s2.3, verbatim algorithm)

```
# dia_ban[i] = fixed chi at palace i (i = 0..11, order Ty..Hoi)
# yue_jiang = nguyet tuong chi; zhan_shi = gio chiem chi
def quay_thien_ban(yue_jiang, zhan_shi):
    off = (index(yue_jiang) - index(zhan_shi)) % 12
    thien_ban = [None]*12
    for i in range(12):
        # chi of the thien ban sitting over dia ban palace i
        thien_ban[i] = CHI[(i + off) % 12]
    return thien_ban
```

Two special rotations that TASK-LN-003 keys off (detected here, resolved there): when `nguyet_tuong == gio_chiem` the offset is 0, thien ban coincides with dia ban - phuc ngam (伏吟). When they are xung (opposite, offset 6) the thien ban is the dia ban turned exactly six palaces - phan ngam (返吟). This task returns the board state marker; the special tam truyen laws are LN-003's.

### Thien can ky cung (Claude-02 s2.4, reproduced)

| Can | Ky cung | Can | Ky cung |
|---|---|---|---|
| 甲 Giap | 寅 Dan | 己 Ky | 未 Mui |
| 乙 At | 辰 Thin | 庚 Canh | 申 Than |
| 丙 Binh | 巳 Ti | 辛 Tan | 戌 Tuat |
| 丁 Dinh | 未 Mui | 壬 Nham | 亥 Hoi |
| 戊 Mau | 巳 Ti | 癸 Quy | 丑 Suu |

Ca quyet: Giap khoa tai Dan, At khoa Thin, Binh Mau khoa Ti, Dinh Ky khoa Mui, Canh khoa Than, Tan khoa Tuat, Nham khoa Hoi, Quy khoa Suu. The four cardinal chi Ty Ngo Mao Dau hold no can.

### Public types (`crates/cyberos-luchnham/src/`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Chi { Ty, Suu, Dan, Mao, Thin, Ti, Ngo, Mui, Than, Dau, Tuat, Hoi }  // idx 0..11

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Can { Giap, At, Binh, Dinh, Mau, Ky, Canh, Tan, Nham, Quy }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TrangThaiBan { Thuong, PhucNgam, PhanNgam }  // normal | offset 0 | offset 6

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThienDiaBan {
    pub dia_ban: [Chi; 12],       // fixed, index 0 = Ty ... 11 = Hoi
    pub thien_ban: [Chi; 12],     // thien_ban[i] sits over dia_ban[i]
    pub nguyet_tuong: Chi,
    pub gio_chiem: Chi,
    pub trang_thai: TrangThaiBan,
}

pub fn quay_thien_ban(nguyet_tuong: Chi, gio_chiem: Chi) -> [Chi; 12];
pub fn nguyet_tuong_tai(trung_khi: &TrungKhiTerm) -> Chi;   // from the CORE term in force
pub fn ky_cung(can: Can) -> Chi;                            // never Ty/Ngo/Mao/Dau
pub fn lap_thien_dia_ban(nguyet_tuong: Chi, gio_chiem: Chi) -> ThienDiaBan;
```

## §4 - Acceptance criteria

1. `quay_thien_ban` is a pure rotation: for all 144 (nguyet_tuong, gio_chiem) pairs the result equals the dia ban rotated by `(nguyet_tuong - gio_chiem) mod 12`, and the map from dia ban to thien ban is a bijection.
2. `nguyet_tuong == gio_chiem` yields `TrangThaiBan::PhucNgam` and `thien_ban == dia_ban`; a xung pair yields `TrangThaiBan::PhanNgam` and `thien_ban` equal to `dia_ban` rotated by 6. Both enumerated.
3. `nguyet_tuong_tai` returns the correct chi for each of the twelve trung khi (table-driven) and is keyed off the TrungKhi-kind term only: a probe whose instant falls after a jie but before the following trung khi still returns the previous trung khi's nguyet tuong.
4. `ky_cung` is correct for all ten can, and a test asserts no can maps to Ty, Ngo, Mao, or Dau.
5. Worked example (Claude-02 s3.3): nguyet tuong Hoi, gio Ty gives offset 11, so the thien ban has Suu over Dan, Ty over Suu, Hoi over Ty, Tuat over Hoi. The value matches kinliuren.
6. The emitted `ban.thien_dia_ban` round-trips through the la so envelope (TASK-PLAT-002) under `he = "luc_nham"`, and `co_truong_phai` carries the stamped LN flag set.

## §5 - Verification

- Unit: `quay_thien_ban` over all 144 pairs (rotation + bijection property); `TrangThaiBan` detection at offsets 0 and 6; `nguyet_tuong_tai` over the twelve trung khi; `ky_cung` over ten can plus the four-empty-chi assertion.
- Oracle: `tests/thiendiaban_oracle.rs` loads `fixtures/thiendiaban_kinliuren.csv` (>= 500 cases spanning the year, generated once from kinliuren and committed) and asserts the computed thien ban is identical for every case. This is the LN half of the LN-006 oracle gate; kinliuren is fed the same tu tru and nguyet tuong that CORE produces.
- Property: for 10,000 random (nguyet_tuong, gio_chiem) pairs, offset is exactly `(nguyet_tuong - gio_chiem) mod 12` and every thien ban chi appears exactly once.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-luchnham -- -D warnings`, `cargo test -p cyberos-luchnham`.

## §6 - Implementation skeleton

1. Create the `cyberos-luchnham` crate (this task owns its birth; TASK-LN-002..006 add modules).
2. `chi.rs`: `Chi` and `Can` enums, the canonical CHI order, index and `xung` (opposite) helpers.
3. `nguyettuong.rs`: the trung-khi -> chi table and `nguyet_tuong_tai` reading the CORE term in force.
4. `thiendiaban.rs`: `quay_thien_ban`, `TrangThaiBan` detection (offset 0 phuc ngam, offset 6 phan ngam), `lap_thien_dia_ban`.
5. `kycung.rs`: the `ky_cung` table.
6. `flags.rs`: the LN flag set (`khoi_quy_nhan`, `truong_sinh_phai`) with defaults; stamped whole even though this slice branches on none of them.
7. Emit the `ThienDiaBan` into the `ban` slot for `he = "luc_nham"`; wire the envelope.
8. Generate the kinliuren fixture once (documented script, not run in CI) and commit; wire the oracle and property tests.

## §7 - Dependencies

Depends on TASK-CORE-005 (the calendar module API supplies the tu tru and the current trung khi that sets nguyet tuong; the TrungKhi/Jie distinction comes from TASK-CORE-001). Blocks TASK-LN-002 (tu khoa reads the thien ban and ky cung), TASK-LN-003 (tam truyen reads the thien ban and the phuc/phan ngam state), and TASK-LN-004 (thien tuong are placed on the thien ban). Emits into the TASK-PLAT-002 envelope; TASK-LN-006 assembles and gates the whole engine.

## §8 - Example payloads

Worked example, nguyet tuong Hoi (Dang Minh), gio Ty:

```json
{ "envelope_version": 1, "he": "luc_nham",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "hon_nhan" },
  "lich_phap": { "...": "from TASK-CORE-005; tiet_khi.hien_hanh is a TrungKhi term" },
  "ban": {
    "thien_dia_ban": {
      "dia_ban":   ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"],
      "thien_ban": ["亥","子","丑","寅","卯","辰","巳","午","未","申","酉","戌"],
      "nguyet_tuong": "亥", "gio_chiem": "子", "trang_thai": "Thuong"
    },
    "tu_khoa": [], "tam_truyen": {}, "thien_tuong": {}
  },
  "cach_cuc": [],
  "co_truong_phai": { "khoi_quy_nhan": "tru_quy", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "..." } }
```

Reading the thien ban array: over dia ban Dan (idx 2) sits 丑 Suu; over Suu (idx 1) sits 子 Ty; over Ty (idx 0) sits 亥 Hoi; over Hoi (idx 11) sits 戌 Tuat - the four lessons LN-002 will build from Giap (ky cung Dan) and the day chi Ty.

## §9 - Open questions

- Does nguyet tuong use CORE's Meeus-computed trung khi instant or a tabular approximation? Default: CORE's computed instant, to keep LiuRen and the calendar core on one clock (strategy RISK-1). A term near a day boundary must not let LiuRen and CORE disagree.
- Index origin: the engine fixes 0 = Ty. CHART-002 renders with Ty at the bottom; confirm the shared origin so the visual board and the index model never drift.
- Phuc ngam / phan ngam are detected here but resolved in LN-003. Confirm the marker names (`PhucNgam`, `PhanNgam`) are the exact tokens LN-003's tam truyen branch reads.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Nguyet tuong keyed off jie | reading the month-pillar jie instead of the trung khi | table test with a probe in the jie..trung window fails; do not ship |
| Rotation direction reversed | thuan/nghich confusion in gia nguyet tuong | phuc-ngam self-check (nguyet==gio must give the identity board) fails |
| Ky cung sends a can to a cardinal chi | wrong ky cung table | enumerated `ky_cung` test asserts Ty/Ngo/Mao/Dau hold no can |
| CHI index origin off by one | array not starting at Ty | golden example (Suu over Dan ...) diverges from kinliuren |
| Phan ngam offset not exactly 6 | xung mis-detected | offset test asserts thien ban == dia ban rotated 6 |

## §11 - Notes

The crate name `cyberos-luchnham` is shared with TASK-LN-002..006; they extend this crate rather than spawn new ones, so the LiuRen engine is one cargo-testable unit. LiuRen is the base system: its Chi / Can primitives and the thien dia ban model are what the later slices and the training curriculum reuse first, so getting the ring order and the rotation exactly right here is load-bearing for the whole engine. Oracle kinliuren; the thien dia ban oracle here is the calendar-facing half of the LN-006 100% gate. The `khoi_quy_nhan` (day/night) and `truong_sinh_phai` (ngu_hanh default) flags are declared and stamped from this first slice even though it branches on neither, so a LiuRen chart is reproducible from its stamp before LN-004 and LN-005 exist.
