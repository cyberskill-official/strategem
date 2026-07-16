---
id: TASK-TAT-002
title: "An Thai At qua cuu cung + 16 than - seat Thai At on its outer palace (never center; center -> Khon 2) and lay the sixteen-than ring (8 chinh cung at Ty Ngo Mao Dau + Can Khon Can Ton, 8 gian than between), tagging each mark chinh cung vs gian than for the downstream toan counting; extends the ban for he=thai_at"
module: TAT
priority: MUST
status: done
phase: P2
slice: 2
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-04 s2.3, Claude-04 s3, Grok-30]
related_frs: [TASK-TAT-001, TASK-TAT-003, TASK-TAT-004, TASK-TAT-005, TASK-TAT-006, TASK-PLAT-002]
depends_on: [TASK-TAT-001]
blocks: [TASK-TAT-003, TASK-TAT-004]
new_paths:
  - crates/cyberos-thaiat/src/anthaiat.rs
  - crates/cyberos-thaiat/src/thaplucthan.rs
  - crates/cyberos-thaiat/tests/thaplucthan_oracle.rs
  - crates/cyberos-thaiat/tests/fixtures/thaplucthan_kintaiyi.csv
---

## §1 - Description (BCP-14 normative)

This task lays the coordinate substrate of every Thai At chart: it seats Thai At in its palace and builds the ring of sixteen than (十六神) that every tuong and every toan is later read against. It extends the `cyberos-thaiat` crate born in TASK-TAT-001, consuming that task's `nhap_cuc` and `thai_at_cung`.

The module SHALL model the sixteen than as a fixed sixteen-element ring, ordered from Ty clockwise (Claude-04 s3.1): Dia chu at Ty, Duong duc at Suu, Hoa duc at Can(艮), Lu than at Dan, Cao tung at Mao, Thai duong at Thin, Dai quynh at Ton, Dai than at Ty(巳), Dai uy at Ngo, Thien dao at Mui, Dai vu at Khon, Vu duc at Than, Thai thoc at Dau, Am chu at Tuat, Am duc at Can(乾), Dai nghia at Hoi. Each mark SHALL carry its chi, its Han name, its transliteration, and its ring index. This is fixed reference data and SHALL be encoded as a table, not derived.

The module SHALL classify each of the sixteen marks as either chinh cung (正宮, principal palace) or gian than (間神, intermediate god). The eight chinh cung are the four cardinal chi Ty Ngo Mao Dau and the four corner qua Can(艮) Ton Khon Can(乾), answering to the eight trigrams; the eight gian than are the remaining chi Dan Than Ty(巳) Hoi Thin Tuat Suu Mui, wedged between the chinh cung (Claude-04 s3.2). This classification is NOT decorative: it decides the counting arithmetic of TASK-TAT-003, where a chinh cung contributes its own palace number to a toan and a gian than counts only as one (Claude-04 s3.3). The module SHALL expose the classification on every mark.

The module SHALL seat Thai At on the ring at the chinh cung mark of its outer palace. Thai At's palace comes from TASK-TAT-001 `thai_at_cung` (the nine-palace layout Can(乾) 1, Ly 2, Can(艮) 3, Chan 4, Trung 5, Doai 6, Khon 7, Kham 8, Ton 9); it is never the center (5) - the center is skipped and Thai At lodges in Khon (2). Because the eight outer palaces answer one-to-one to the eight chinh cung marks, seating Thai At SHALL land it on exactly one chinh cung mark.

The module SHALL keep the canonical than names with their Han and SHALL record known variants (Lu than also written Lu than 呂神; Dai vu also written Doi vu) without auto-substituting them (Claude-04 s3.2); the variant-name handling is a stamped flag carried through to TASK-TAT-006. The module SHALL extend the `ban` slot for `he = "thai_at"` (TASK-PLAT-002) with `thap_luc_than` and the Thai At ring seat. The oracle is kintaiyi.

## §2 - Why this design (rationale for humans)

The chinh cung vs gian than distinction is, by the source's own account, the single most common place TaiYi implementations go wrong (Claude-04 s3.3), and it is called out as the second classic error after the large-integer arithmetic of TASK-TAT-001 (tat module notes). The defense is to make the distinction a property of the data model, decided once here, rather than a rule re-applied ad hoc inside every counting loop in TASK-TAT-003. If each mark already knows whether it is a chinh cung (and therefore lends its palace number) or a gian than (and therefore counts as one), the toan loop cannot silently mix the two conventions.

The sixteen than are a fixed lookup, so this task is cheap and fully auditable: there is no astronomy and no large-number arithmetic, only a table and a seating rule. That is exactly why it is worth isolating - it is the stable coordinate frame that TASK-TAT-003 (tuong and toan) and TASK-TAT-005 (cach cuc) both read. Seating Thai At here, on the ring rather than only on the bare nine-palace grid of TASK-TAT-001, gives those downstream tasks a single origin to count from.

Thai At sits on a chinh cung because it occupies an outer palace and never the center; stating the outer-palace-to-chinh-cung correspondence explicitly closes the gap between the nine-palace movement of TASK-TAT-001 and the sixteen-mark ring used from here on. The variant names are preserved rather than normalized because presenting schools fairly and keeping the original Han is a product invariant (strategy 4.4, section 7), and silently rewriting a than name would erase a lineage difference.

## §3 - Contract (algorithm and types)

### The sixteen than ring (Claude-04 s3.1 / s3.2, reproduced faithfully)

Order runs from Ty clockwise. Loai marks chinh cung (principal, lends its palace number) vs gian than (intermediate, counts as one). The four corner marks are the "chinh duy" (Cấn Tốn Khôn Càn); with the four cardinal chi they make up the eight chinh cung.

| Ring | Cung | Than | Phien am | Loai |
|---:|---|---|---|---|
| 0 | 子 Ty | 地主 | Địa chủ | Chính cung |
| 1 | 丑 Suu | 陽德 | Dương đức | Gian thần |
| 2 | 艮 Can(gen) | 和德 | Hoà đức | Chính (duy) |
| 3 | 寅 Dan | 呂申 | Lữ thân | Gian thần |
| 4 | 卯 Mao | 高叢 | Cao tùng | Chính cung |
| 5 | 辰 Thin | 太陽 | Thái dương | Gian thần |
| 6 | 巽 Ton | 大炅 | Đại quýnh | Chính (duy) |
| 7 | 巳 Ty(chi) | 大神 | Đại thần | Gian thần |
| 8 | 午 Ngo | 大威 | Đại uy | Chính cung |
| 9 | 未 Mui | 天道 | Thiên đạo | Gian thần |
| 10 | 坤 Khon | 大武 | Đại vũ | Chính (duy) |
| 11 | 申 Than | 武德 | Vũ đức | Gian thần |
| 12 | 酉 Dau | 太簇 | Thái thốc | Chính cung |
| 13 | 戌 Tuat | 陰主 | Âm chủ | Gian thần |
| 14 | 乾 Can(qian) | 陰德 | Âm đức | Chính (duy) |
| 15 | 亥 Hoi | 大義 | Đại nghĩa | Gian thần |

Variants (recorded, never auto-applied): 呂申 Lữ thân also written 呂神 Lữ thần; 大武 Đại vũ also written Đợi vũ.

### Seating Thai At on the ring (Claude-04 s2.3)

Thai At occupies an outer palace (never center 5; center -> Khon 2), and the eight outer palaces answer one-to-one to the eight chinh cung marks by trigram direction:

| Palace (TASK-TAT-001) | 乾1 | 離2 | 艮3 | 震4 | 中5 | 兌6 | 坤7 | 坎8 | 巽9 |
|---|---|---|---|---|---|---|---|---|---|
| Chinh cung mark | 乾 Âm đức | 午 Đại uy | 艮 Hoà đức | 卯 Cao tùng | (skipped -> 坤) | 酉 Thái thốc | 坤 Đại vũ | 子 Địa chủ | 巽 Đại quýnh |

The center palace has no ring mark; when TASK-TAT-001 lands Thai At on the center it returns Khon (2), which seats on 坤 Đại vũ. The exact palace-to-mark correspondence is pinned to kintaiyi by the oracle test (see §9).

```
# thai_at_cung comes from TASK-TAT-001 (1..9, never 5)
def an_thai_at(nhap_cuc, duong_don):
    palace = thai_at_cung(nhap_cuc, duong_don)   # TASK-TAT-001; 1..9, never 5
    ring   = CHINH_CUNG_MARK[palace]             # index into the 16-than ring
    return { "thai_at_cung": palace, "thai_at_ring": ring }
```

### Public types (`crates/cyberos-thaiat/src/`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LoaiThan { ChinhCung, GianThan }   // principal (lends palace no.) vs intermediate (counts as one)

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Than {
    pub ring: u8,              // 0..=15, from Ty clockwise
    pub chi: &'static str,     // 子, 丑, 艮, ...
    pub han: &'static str,     // 地主
    pub ten: &'static str,     // "Dia chu"
    pub loai: LoaiThan,
}

pub const THAP_LUC_THAN: [Than; 16];        // the fixed ring, this task's core data

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThaiAtSeat {
    pub thai_at_cung: u8,      // 1..=9, never 5 (from TASK-TAT-001)
    pub thai_at_ring: u8,      // 0..=15, always a chinh cung mark
}

pub fn an_thai_at(nhap_cuc: u8, duong_don: bool) -> ThaiAtSeat;
pub fn is_chinh_cung(ring: u8) -> bool;     // true for the 8 principal marks
```

## §4 - Acceptance criteria

1. `THAP_LUC_THAN` has sixteen entries in the s3.1 order from Ty; each carries the exact Han and transliteration of the s3.2 table; an enumerated unit test pins all sixteen.
2. Exactly eight marks are `ChinhCung` (子 午 卯 酉 艮 巽 坤 乾) and eight are `GianThan` (丑 寅 辰 巳 未 申 戌 亥); a unit test asserts the count and the membership.
3. `an_thai_at` seats Thai At on a `ChinhCung` mark for every `nhap_cuc` in 1..=72 under both dons; it never returns a `GianThan` ring index and never a center (there is no center mark).
4. When TASK-TAT-001 would place Thai At on the center, `thai_at_cung` is Khon (2) and `thai_at_ring` is 坤 Đại vũ (ring 10); the center-skip is honored end to end.
5. Variant names are retained on the canonical marks and are not substituted; a test asserts 呂申 is stored as-is with the 呂神 variant only recorded, not swapped in.
6. The emitted `ban.thap_luc_than` and the Thai At seat round-trip through the la so envelope (TASK-PLAT-002) under `he = "thai_at"`.

## §5 - Verification

- Unit: the sixteen-mark enumeration; the eight/eight chinh-cung / gian-than split; the variant-recording test.
- Property: `an_thai_at` is total over 1..=72 x {duong, am} and always lands on one of the eight chinh cung marks; `is_chinh_cung(r)` agrees with `THAP_LUC_THAN[r].loai` for all r in 0..=15.
- Oracle: `tests/thaplucthan_oracle.rs` loads `fixtures/thaplucthan_kintaiyi.csv` (generated once from kintaiyi, per epoch, over multiple years and both dons) and asserts the Thai At ring seat matches exactly. This feeds the TASK-TAT-006 100% gate.
- Boundary: cases where TASK-TAT-001 lands on the center (Thai At -> Khon 2 -> ring 10) and the cuc wrap (72 -> 1) both seat correctly.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-thaiat -- -D warnings`, `cargo test -p cyberos-thaiat`.

## §6 - Implementation skeleton

1. `thaplucthan.rs`: the `Than` type, `LoaiThan`, and the `THAP_LUC_THAN` sixteen-element constant transcribed from the s3.2 table (Han + transliteration + loai), plus `is_chinh_cung`.
2. `anthaiat.rs`: the `CHINH_CUNG_MARK[palace]` correspondence, `an_thai_at` reusing `thai_at_cung` from TASK-TAT-001, and the `ThaiAtSeat` type.
3. Record the two known name variants as data (canonical + variant string), gated behind the variant-name flag that TASK-TAT-006 stamps.
4. Extend the `he = "thai_at"` `ban` with `thap_luc_than` and the Thai At seat; keep TASK-TAT-001's `tich` and `thai_at_cung` intact.
5. Generate the kintaiyi ring fixture once (documented script, not run in CI) and commit; wire the oracle, property, and boundary tests.

## §7 - Dependencies

Depends on TASK-TAT-001 (`nhap_cuc`, `thai_at_cung`, the epoch / reduction machinery, and the crate itself). Blocks TASK-TAT-003 (Van Xuong, Thuy Kich, the tuong, and the chu/khach toan all count around this ring and rely on the chinh-cung / gian-than tag) and TASK-TAT-004 (each time level seats Thai At on this same ring). Emits into the TASK-PLAT-002 envelope; the assembly and cache key are TASK-TAT-006's.

## §8 - Example payloads

Nien ke for 2004 under `kim_kinh` (Thai At in palace 1, seated on 乾 Âm đức), `ban` fragment:

```json
{ "ban": {
    "tich": { "tich_nien": 10155921, "nhap_cuc": 33, "can_chi": "甲申", "duong_don": true },
    "thai_at_cung": 1,
    "thai_at_ring": 14,
    "thap_luc_than": {
      "ring": [
        { "ring": 0,  "chi": "子", "han": "地主", "ten": "Dia chu",  "loai": "chinh_cung" },
        { "ring": 1,  "chi": "丑", "han": "陽德", "ten": "Duong duc","loai": "gian_than" },
        { "ring": 2,  "chi": "艮", "han": "和德", "ten": "Hoa duc",  "loai": "chinh_cung" },
        "... twelve more ...",
        { "ring": 14, "chi": "乾", "han": "陰德", "ten": "Am duc",   "loai": "chinh_cung" },
        { "ring": 15, "chi": "亥", "han": "大義", "ten": "Dai nghia","loai": "gian_than" }
      ]
    },
    "bat_tuong": {}, "cac_toan": {}
  } }
```

(`thai_at_ring` is pinned to kintaiyi by the oracle; the correspondence table in §3 is the seed, not the authority.)

## §9 - Open questions

- The palace-to-chinh-cung-mark correspondence in §3 is derived from trigram direction; it MUST be confirmed against kintaiyi before it is locked, exactly as TASK-TAT-001 defers the placement question to the oracle. If kintaiyi disagrees on any of the eight seats, the correspondence table is corrected and the disagreement noted.
- Center-skip target: TASK-TAT-001 lodges the center in Khon (2). Confirm Khon here means the palace numbered 2 in the Thai At layout (Ly) or the Khon trigram at 坤 (ring 10); this task seats it on 坤 Đại vũ pending the oracle, and the two readings are cross-checked when the fixture lands.
- Variant-name flag surface: this task records variants as data; whether the flag also allows selecting a variant lineage for display is deferred to TASK-TAT-006, which owns the stamped flag set.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Chinh cung / gian than mislabeled | wrong loai on a mark | enumerated unit test on all sixteen fails; downstream toan (TASK-TAT-003) would diverge from kintaiyi |
| Thai At seated on a gian than | seating rule maps to a wrong ring index | property test asserts every seat is a chinh cung mark |
| Center not skipped | palace 5 passed through to a ring seat | there is no center mark; a center input must arrive as Khon (2) from TASK-TAT-001, asserted by a boundary test |
| Than name silently rewritten | variant substituted for canonical | variant-recording test asserts canonical stored, variant only noted |
| Ring order off by one | ring not started at Ty or wrong direction | oracle ring fixture diverges; enumerated order test fails |

## §11 - Notes

This task contributes the fixed coordinate frame - the sixteen-than ring and Thai At's seat on it - that TASK-TAT-003 and TASK-TAT-005 read. Its whole reason to exist as a separate slice is the chinh cung vs gian than tag: encoding that distinction once, in the data, is the cleanest defense against the most common TaiYi counting bug (Claude-04 s3.3, tat module notes). No astronomy and no large-integer arithmetic here - just a faithful table and a seating rule - so correctness is a matter of transcription discipline against the s3.2 table and the kintaiyi ring fixture. Keep the Han and the recorded variants exact; presenting schools fairly and preserving the original Han is a product invariant (strategy 4.4, section 7).
