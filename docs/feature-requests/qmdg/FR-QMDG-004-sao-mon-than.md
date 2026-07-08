---
id: FR-QMDG-004
title: "Cuu tinh / bat mon / bat than placement - nine stars, eight doors (Khai/Huu/Sinh cat), eight gods led by Truc Phu; yin_yang_pan lineage flag (duong classical / am Vuong Phuong Lan god swap)"
module: QMDG
priority: MUST
status: ready_to_implement
phase: P0
slice: 1
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-2, Claude-03 s2.3, Claude-03 s6]
related_frs: [FR-QMDG-003, FR-QMDG-005, FR-QMDG-006]
depends_on: [FR-QMDG-003]
blocks: [FR-QMDG-005, FR-QMDG-006]
new_paths:
  - crates/cyberos-qimen/src/sao_mon_than.rs
  - crates/cyberos-qimen/tests/sao_mon_than_oracle.rs
---

## §1 - Description (BCP-14 normative)

This FR places the three dynamic rings that complete the four-plate chart over the earth plate: the cuu tinh (九星, nine stars of the sky plate), the bat mon (八門, eight doors of the human plate), and the bat than (八神, eight gods of the god plate). It consumes the truc phu, truc su, and rotation offset from FR-QMDG-003 and produces the star / door / god at every palace.

The module SHALL place the nine stars carrying the truc phu by the FR-QMDG-003 rotation (chuyen or phi), the eight doors carrying the truc su, and the eight gods starting from Trực Phù at the truc phu palace and walking the ring in the don direction (forward in duong don, reverse in am don, per s10.4). The three cat doors are Khai 開, Hưu 休, Sinh 生 (s2.3).

The module SHALL treat the classical / modern split as a high-level flag `yin_yang_pan` in {`duong`, `am`}, default `duong` (s6). `duong` (classical, number-theory, cach-cuc heavy) uses the sieu-than-tiep-khi dinh cuc of FR-QMDG-001 and the classical god ring. `am` (the modern Vuong Phuong Lan / Kỳ Môn đạo gia lineage) computes the cuc by remainder-mod-9 (thai am so) and swaps two god pairs - Bạch Hổ with Câu Trần, and Huyền Vũ with Chu Tước - so its god map differs. The two lineages SHALL NOT be mixed in one chart; `yin_yang_pan` SHALL be stamped into `co_truong_phai` (FR-PLAT-002), and it governs the whole operation chain, not just this ring.

## §2 - Why this design (rationale for humans)

The stars, doors, and gods are what a reader actually looks at in each palace, so getting the rings and their placement direction right is what makes the chart legible. The stars follow the same rotation as the sky-plate stems (they are the sky plate), the doors follow the truc su, and the gods lead with Trực Phù - three rings, three anchors, one direction rule.

The `yin_yang_pan` axis is the largest fork in QiMen: it is not two cuc numbers but two whole practices with different cuc rules and a different god map (s6, strategy RISK-2). Users of one lineage do not accept the other's charts. Modeling it as a high-level flag that gates the entire chain - and stamping it - is the only way a chart is honest about which lineage cast it. This FR specifies `duong` in full and leaves `am` as a lineage the flag selects, with the god swap and the remainder-mod-9 cuc rule called out so the engine has a clear extension seam rather than a hidden default.

## §3 - Contract (algorithm)

### The three rings (Claude-03 s2.3, names verbatim)

- Cuu tinh (nine stars): Thiên Bồng 天蓬, Thiên Nhuế 天芮, Thiên Xung 天沖, Thiên Phụ 天輔, Thiên Cầm 天禽, Thiên Tâm 天心, Thiên Trụ 天柱, Thiên Nhậm 天任, Thiên Anh 天英.
- Bat mon (eight doors): Hưu 休, Sinh 生, Thương 傷, Đỗ 杜, Cảnh 景, Tử 死, Kinh 驚, Khai 開. The three cat doors are Khai 開, Hưu 休, Sinh 生.
- Bat than (eight gods), classical duong ring led by Trực Phù: Trực Phù 值符, Đằng Xà 螣蛇, Thái Âm 太陰, Lục Hợp 六合, Bạch Hổ 白虎, Huyền Vũ 玄武, Cửu Địa 九地, Cửu Thiên 九天. Some texts run a nine-god ring (s10.4 notes "eight or nine gods"); the ninth is a school variant and is reserved.

### Resting home rings (reference, gated against kinqimen)

The resting arrangement each ring rotates from - each star's and door's home palace - is the Luoshu-anchored fixture the whole engine shares (imported by FR-QMDG-003 to identify truc phu / truc su). It is presented here as the reference arrangement and is validated cell-by-cell against kinqimen rather than asserted as canon:

| Palace | 1 Khảm | 2 Khôn | 3 Chấn | 4 Tốn | 5 Trung | 6 Càn | 7 Đoài | 8 Cấn | 9 Ly |
|---|---|---|---|---|---|---|---|---|---|
| Cửu tinh | 天蓬 | 天芮 | 天沖 | 天輔 | 天禽 | 天心 | 天柱 | 天任 | 天英 |
| Bát môn | 休 | 死 | 傷 | 杜 | - | 開 | 驚 | 生 | 景 |

Thiên Cầm 天禽 rests in Trung 5 and lodges by `zhong_gong_ky` (FR-QMDG-003); Trung has no door.

### Placement direction (Claude-03 s5.2, s10.4)

- Stars: rotate with the sky plate by the FR-QMDG-003 `xoay` offset under `pan_method` (rigid wheel for `zhuan`, per-star flight for `fei`); the truc phu ends on the hour-stem palace.
- Doors: the truc su moves by counting from the tuan-thu palace to the hour palace; the remaining doors follow around the ring.
- Gods: start Trực Phù at the truc phu palace and walk the eight-god ring in the don direction - forward in duong don, reverse in am don.

### yin_yang_pan lineage (Claude-03 s6, flag)

- `duong` (陽盤, classical): dinh cuc via sieu than tiep khi (FR-QMDG-001), classical god ring above, cach-cuc heavy (FR-QMDG-005). Default; specified in full.
- `am` (陰盤, Vuong Phuong Lan): cuc by remainder-mod-9 (thai am so), light on cach cuc; god ring swaps Bạch Hổ 白虎 <-> Câu Trần 勾陳 and Huyền Vũ 玄武 <-> Chu Tước 朱雀. Selected by the flag; not mixed with `duong`.

### Public types and entry point

```rust
pub enum CuuTinh { ThienBong, ThienNhue, ThienXung, ThienPhu, ThienCam, ThienTam, ThienTru, ThienNham, ThienAnh }
pub enum BatMon  { Huu, Sinh, Thuong, Do, Canh, Tu, Kinh, Khai }   // Khai/Huu/Sinh are cat
pub enum BatThan { TrucPhu, DangXa, ThaiAm, LucHop, BachHo, HuyenVu, CuuDia, CuuThien }  // duong ring
pub enum YinYangPan { Duong, Am }   // default Duong

pub struct SaoMonThan {
    pub cuu_tinh: [CuuTinh; 9],   // by palace 1..9
    pub bat_mon:  [Option<BatMon>; 9],   // None at Trung 5
    pub bat_than: [Option<BatThan>; 9],
}

pub fn sao_mon_than(tps: &TrucPhuSu, dinh_cuc: &DinhCuc, flags: &QiMenFlags) -> SaoMonThan;

impl BatMon { pub fn is_cat(self) -> bool; }   // Khai | Huu | Sinh
```

## §4 - Acceptance criteria

1. The resting rings match kinqimen cell-by-cell in the resting arrangement (before rotation); a golden test asserts the star and door home rings.
2. `is_cat` is true for exactly Khai, Hưu, Sinh; a unit test enumerates all eight doors.
3. Under `duong`, the stars rotate with the sky plate to place the truc phu on the hour-stem palace, the doors carry the truc su, and the gods lead with Trực Phù in the don direction; a golden worked chart asserts all three rings.
4. The god ring walks forward in duong don and reverse in am don; a unit test checks one chart of each direction.
5. `yin_yang_pan = am` applies the two god swaps (Bạch Hổ <-> Câu Trần, Huyền Vũ <-> Chu Tước) and the remainder-mod-9 cuc; the resulting god map differs from `duong` on the same instant.
6. `sao_mon_than` matches kinqimen across a sample for every combination of `pan_method`, `zhong_gong_ky`, and `yin_yang_pan`.

## §5 - Verification

- `tests/sao_mon_than_oracle.rs` loads star / door / god rows from the kinqimen fixture and asserts an exact palace-by-palace match, iterating `pan_method` x `zhong_gong_ky` x `yin_yang_pan`.
- Golden resting-ring test and the `is_cat` enumeration.
- Direction test: one duong-don and one am-don chart, asserting the god-ring walk direction.
- Lineage test: `duong` vs `am` on the same instant differ by exactly the two god swaps (and the cuc rule), proving the fork.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`.

## §6 - Implementation skeleton

1. Add `sao_mon_than.rs` with the three ring enums, the resting home rings as consts, and `YinYangPan` added to `QiMenFlags`.
2. Place the stars from the FR-QMDG-003 `xoay` offset under `pan_method`; place the doors from the truc su; walk the gods from Trực Phù in the don direction.
3. Apply `zhong_gong_ky` lodging consistently (star at Trung, no door at Trung).
4. Implement the `am` lineage as a swap layer over the `duong` god ring plus the remainder-mod-9 cuc hook into FR-QMDG-001; keep `duong` the specified-in-full default.
5. Wire the oracle test across the flag product and the lineage divergence test.

## §7 - Dependencies

Depends on FR-QMDG-003 (truc phu, truc su, rotation offset, `pan_method`, `zhong_gong_ky`). Blocks FR-QMDG-005 (cach cuc reads the completed rings) and FR-QMDG-006 (assembly). The resting rings defined here are imported by FR-QMDG-003; they live in this FR as the single source of the home arrangement.

## §8 - Example payloads

The three ring slots of the QiMen `ban` for a worked chart:

```json
{ "cuu_tinh": { "1": "天蓬", "9": "天英", "...": "..." },
  "bat_mon":  { "1": "休", "6": "開", "...": "..." },
  "bat_than": { "1": "值符", "...": "..." },
  "co_truong_phai": { "pan_method": "zhuan", "zhong_gong_ky": "khon2", "yin_yang_pan": "duong" } }
```

## §9 - Open questions

- Eight-god vs nine-god ring: the source notes both (s10.4). Default to the eight-god ring; if kinqimen (or a school in scope) runs nine gods, add the ninth as a reserved value and gate to it. Do not silently choose.
- Exact `am`-lineage god ring and its walk direction beyond the two named swaps: specify against a Vuong Phuong Lan reference plus kinqimen before enabling `am` in production; `duong` remains the default and is fully specified here.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Wrong resting ring | star / door home palace transcribed wrong | golden resting-ring test fails against kinqimen |
| God walk direction wrong | forward/reverse not tied to don | direction test fails on am-don chart |
| Lineage mixed | am god swap applied under duong (or vice versa) | lineage divergence test fails; flag must gate the whole chain |
| Trung door placed | a door assigned to Trung 5 | type is `Option`; None enforced at Trung; test asserts it |
| Cat-door set wrong | is_cat includes a hung door | door enumeration test fails |

## §11 - Notes

`yin_yang_pan` is the QiMen fork that most needs the stamp-and-do-not-mix discipline (strategy RISK-2): the two lineages share almost no rules, so an implicit default would silently mis-serve half the users. Specify `duong` completely, gate it hard, and keep `am` a clean, flagged extension with its swaps and cuc rule written down rather than a half-built branch.
