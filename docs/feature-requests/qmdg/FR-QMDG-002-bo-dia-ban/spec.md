---
id: FR-QMDG-002
title: "Bo dia ban - place luc nghi + tam ky on the nine palaces by so cuc, directional fill (duong forward, am reverse), start palace = so cuc"
module: QMDG
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, Claude-03 s4]
related_frs: [FR-QMDG-001, FR-QMDG-003, FR-QMDG-006]
depends_on: [FR-QMDG-001]
blocks: [FR-QMDG-003, FR-QMDG-006]
new_paths:
  - crates/cyberos-qimen/src/dia_ban.rs
  - crates/cyberos-qimen/tests/dia_ban_oracle.rs
---

## §1 - Description (BCP-14 normative)

This FR implements bo dia ban (布地盤): after dinh cuc (FR-QMDG-001) yields the so cuc and don direction, place the luc nghi (六儀, the six stems Mậu Kỷ Canh Tân Nhâm Quý) and the tam ky (三奇, the three qi Ất Bính Đinh) onto the nine palaces to form the fixed earth plate. The earth plate is the still foundation every later plate rotates over, so it is computed once per cuc and cached with the chart.

The module SHALL start at the palace whose number equals the so cuc, place Mậu there, and step through the nine palaces filling the fixed sequence Mậu, Kỷ, Canh, Tân, Nhâm, Quý, Đinh, Bính, Ất. The stepping direction is the don direction: duong don steps forward through the Luoshu palace numbers, am don steps backward. The three qi come out in reverse qi-order (Đinh, Bính, Ất) after the six nghi, which is the encoded form of "duong don places the nghi forward then the qi reverse" (s4.1); am don reverses the walk.

The module SHALL fill all nine palaces including the center (Trung 5); every palace carries exactly one stem. The result feeds FR-QMDG-003, which reads the earth plate to locate the tuan-thu nghi and identify truc phu / truc su. This FR stamps no new flag - it inherits `dingju_method` from the `DinhCuc` it consumes - but its output becomes the `dia_ban` slot of the QiMen `ban` in the la so envelope (FR-PLAT-002).

## §2 - Why this design (rationale for humans)

The earth plate is deterministic and school-invariant once the cuc and direction are fixed: there is no flag here, only the mechanical fill. Encoding the fill as one fixed stem sequence plus a single direction toggle (forward vs backward) keeps it trivially testable and matches how the source presents it (s4.2 pseudocode). The subtle point that trips implementations is the direction of the qi in am don: the source states the concept as "am don reverse-places the nghi then forward-places the qi" (s4.1) but gives an implementable pseudocode that keeps the stem sequence fixed and only flips the walk (s4.2). This FR follows the pseudocode as the source of truth and gates the am-don qi direction against kinqimen rather than trusting the prose, because the two descriptions can disagree at the edges (see §9).

## §3 - Contract (algorithm)

### Reference pseudocode (Claude-03 s4.2, verbatim)

```
# cuc = so cuc (1..9); duong = True neu duong don
# LUOSHU_ORDER: chuoi cung theo Lac Thu; NGHI_KY = [Mau..Quy, Dinh, Binh, At]
def bo_dia_ban(cuc, duong):
    dia = {}
    cung = cuc                         # cung khoi = so cuc
    seq  = ["戊","己","庚","辛","壬","癸","丁","丙","乙"]
    for can in seq:
        dia[cung] = can
        if duong:
            cung = buoc_thuan_lac_thu(cung)   # tien 1 cung
        else:
            cung = buoc_nghich_lac_thu(cung)  # lui 1 cung
    return dia
```

The stem sequence `["戊","己","庚","辛","壬","癸","丁","丙","乙"]` is the six nghi in order followed by the three qi in reverse order. `buoc_thuan_lac_thu` advances to the next Luoshu palace number and `buoc_nghich_lac_thu` steps back one; per the s4.2 worked table the walk is by palace number 1..9 (including the center), wrapping, which is the earth-plate convention and is distinct from the flying-star order used for the sky plate in FR-QMDG-003.

### Worked example - duong don cuc 1 (Claude-03 s4.2, verbatim)

Start at Khảm 1, place Mậu, then step forward: Kỷ to Khôn 2, Canh to Chấn 3, Tân to Tốn 4, Nhâm to Trung 5, Quý to Càn 6, then the qi Đinh to Đoài 7, Bính to Cấn 8, Ất to Ly 9.

| Cung | Số Lạc Thư | Bát quái | Nghi kỳ |
|---|---|---|---|
| Khảm | 1 | 坎 | 戊 Mậu |
| Khôn | 2 | 坤 | 己 Kỷ |
| Chấn | 3 | 震 | 庚 Canh |
| Tốn | 4 | 巽 | 辛 Tân |
| Trung | 5 | 中 | 壬 Nhâm |
| Càn | 6 | 乾 | 癸 Quý |
| Đoài | 7 | 兌 | 丁 Đinh |
| Cấn | 8 | 艮 | 丙 Bính |
| Ly | 9 | 離 | 乙 Ất |

Am don keeps the start palace at the so cuc but steps backward, and (per §9, gated against the oracle) the qi direction flips relative to duong don.

### Public types and entry point

```rust
pub enum Can { Giap, At, Binh, Dinh, Mau, Ky, Canh, Tan, Nham, Quy }  // 甲乙丙丁戊己庚辛壬癸

pub struct DiaBan {
    pub cung: [Can; 9],   // index 0..8 maps palace 1..9; every palace carries one stem
}

pub fn bo_dia_ban(dinh_cuc: &DinhCuc) -> DiaBan;
```

Giáp never appears on the plate - it is hidden under the nghi by the don-giap rule (s2.2) - so the nine visible stems are the six nghi plus the three qi.

## §4 - Acceptance criteria

1. duong don cuc 1 reproduces the s4.2 worked table exactly (Khảm 1 -> Mậu ... Ly 9 -> Ất); a golden unit test asserts all nine cells.
2. Every so cuc 1-9 in duong don fills all nine palaces with the fixed sequence stepping forward, wrapping 9 -> 1; a unit test walks all nine cuc.
3. Am don fills all nine palaces stepping backward from the start palace; the am-don qi direction matches kinqimen.
4. Giáp never appears on the plate; a unit test asserts the plate is a permutation of the six nghi plus the three qi.
5. `bo_dia_ban` matches the kinqimen earth plate across a sample covering so cuc 1-9 in both don directions.

## §5 - Verification

- `tests/dia_ban_oracle.rs` loads the earth-plate rows from the shared kinqimen fixture (per cuc, per don) and asserts an exact palace-by-palace match.
- Golden unit test on the s4.2 duong-don cuc-1 table.
- Property test: for every cuc and don, the plate is a permutation of the nine visible stems (no stem missing or duplicated, Giáp absent).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`.

## §6 - Implementation skeleton

1. Add `dia_ban.rs` with `Can`, `DiaBan`, and the fixed stem sequence const.
2. Implement the forward and backward Luoshu-number walk (1..9 wrapping), starting at the so cuc.
3. Fill the plate; assert the permutation property internally in debug builds.
4. Wire the golden test and the oracle test; confirm the am-don qi direction against kinqimen and lock it with a fixture.

## §7 - Dependencies

Depends on FR-QMDG-001 (consumes `DinhCuc.so_cuc` and `DinhCuc.duong_don`). Blocks FR-QMDG-003 (truc phu / truc su reads the earth plate to find the tuan-thu nghi's palace) and FR-QMDG-006 (assembly). No new flag; inherits `dingju_method` from the `DinhCuc`.

## §8 - Example payloads

The `dia_ban` slot of the QiMen `ban` (palace number -> stem), for duong don cuc 1:

```json
{ "dia_ban": { "1": "戊", "2": "己", "3": "庚", "4": "辛", "5": "壬", "6": "癸", "7": "丁", "8": "丙", "9": "乙" } }
```

## §9 - Open questions

- Am-don qi direction: the s4.1 prose ("am don reverse-places the nghi then forward-places the qi") and the s4.2 pseudocode (fixed stem sequence, walk direction flipped) can disagree on whether the three qi come out Đinh-Bính-Ất or Ất-Bính-Đinh in am don. Decision: follow the s4.2 pseudocode, then lock the exact am-don placement against kinqimen with a fixture; if the oracle sides with the prose, adjust the stem sequence for am don and record the divergence. This is a boundary detail, not an architectural one.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Center palace skipped | walk excludes Trung 5 | permutation property fails (a stem is unplaced) |
| Wrong walk direction | duong/am toggle inverted | oracle diverges for every am-don cuc; direction test fails |
| Qi order wrong in am don | s4.1 vs s4.2 ambiguity unresolved | am-don oracle fixture fails until placement is locked |
| Giáp placed on plate | don-giap rule violated | permutation test fails |
| Off-by-one start palace | start not equal to so cuc | duong-don cuc-1 golden test fails |

## §11 - Notes

The earth plate is the one QiMen step with no school flag of its own, which makes it a good early confidence check: if the s4.2 worked table does not reproduce byte-for-byte, something upstream in `Can` ordering or the Luoshu walk is wrong. Keep the stem sequence and the walk in `dia_ban.rs` only; later FRs read `DiaBan` but never re-derive it.
