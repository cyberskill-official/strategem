---
id: FR-QMDG-001
title: "Dinh cuc - so cuc 1-9 + duong/am don direction from the full 24-jieqi x 3-nguyen table, phu dau + sieu than tiep khi + tri nhuan drift, dingju_method flag (chaibu/zhirun/maoshan)"
module: QMDG
priority: MUST
status: ready_to_implement
phase: P0
slice: 1
lang: rust
effort_h: 18
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.4, strategy RISK-7, Claude-03 s3, Claude-03 s9]
related_frs: [FR-QMDG-002, FR-QMDG-003, FR-QMDG-006, FR-CORE-001, FR-CORE-005]
depends_on: [FR-CORE-005]
blocks: [FR-QMDG-002, FR-QMDG-006]
new_paths:
  - crates/cyberos-qimen/Cargo.toml
  - crates/cyberos-qimen/src/lib.rs
  - crates/cyberos-qimen/src/flags.rs
  - crates/cyberos-qimen/src/dinh_cuc.rs
  - crates/cyberos-qimen/tests/dinh_cuc_oracle.rs
  - crates/cyberos-qimen/tests/fixtures/dinh_cuc_kinqimen.csv
---

## §1 - Description (BCP-14 normative)

This FR implements dinh cuc (定局), the first step of the QiMen engine: given the calendar context from CORE (the tiet khi in force, its tam nguyen, and the four pillars), determine the so cuc (局, a number 1-9) and the don direction (duong don / am don) that seed every later step. It owns the birth of the `cyberos-qimen` crate; FR-QMDG-002..006 extend this crate rather than create new ones, so the engine is one testable unit.

The module SHALL map (tiet khi, tam nguyen) to a so cuc via the full 24-jieqi x 3-nguyen table (s3.2), reproduced verbatim in §3. It SHALL return duong don for the winter-half terms (from Dong Chi 冬至, days lengthening, forward placement) and am don for the summer-half terms (from Ha Chi 夏至, days shortening, reverse placement). The don direction is not decorative: it fixes the direction in which FR-QMDG-002 lays the luc nghi tam ky and in which FR-QMDG-004 walks the god ring.

The module SHALL resolve which tam nguyen (thuong / trung / ha) a day belongs to from the phu dau (符頭), and SHALL handle the sieu than tiep khi (超神接氣) drift and tri nhuan (置閏) leap-term insertion per the selected method. Because the phu dau drifts against the true tiet khi by up to about nine days, and the schools disagree on how to absorb that drift, the resolution method is a flag, never a hardcoded choice: `dingju_method` in {`chaibu`, `zhirun`, `maoshan`}, default `chaibu`.

The module SHALL stamp `dingju_method` into `co_truong_phai` of the la so envelope (FR-PLAT-002) and SHALL emit its result as the `dinh_cuc` component of the QiMen `ban`. Two charts with the same instant but a different `dingju_method` MAY differ at boundary days; the stamp makes each reproducible.

## §2 - Why this design (rationale for humans)

Dinh cuc is where QiMen splits into schools more than anywhere else (Claude-03 s9.1). The so cuc itself is a table lookup once the tam nguyen is known; the hard part is knowing which tam nguyen the day is in, because the QiMen "year" of 360 days (3 nguyen x 5 days x 24 terms) does not line up with the 365-day solar year, so the phu dau slips ahead of or behind the true term. Three traditions absorb that slip differently, and they can land a boundary day in a different nguyen - hence a different cuc, hence a different chart (strategy RISK-7). If the engine picked one silently, half the users of another school would reject the chart, so the method is a stamped flag and the test matrix runs per method.

Building dinh cuc first, and building it flag-first, forces the flag-and-stamp discipline into the platform at the earliest engine step, which is exactly why QiMen was chosen as the flagship (strategy 3.4). Everything downstream inherits the pattern: no hardcoded school, full flag stamp, oracle gate per flag combination.

## §3 - Contract (algorithm)

### The 24-jieqi x 3-nguyen table (Claude-03 s3.2, verbatim)

Left half is duong don from Dong Chi; right half is am don from Ha Chi. Columns are thuong / trung / ha nguyen.

| Tiết khí (dương độn) | Thượng | Trung | Hạ | Tiết khí (âm độn) | Thượng | Trung | Hạ |
|---|---|---|---|---|---|---|---|
| Đông Chí 冬至 | 1 | 7 | 4 | Hạ Chí 夏至 | 9 | 3 | 6 |
| Tiểu Hàn 小寒 | 2 | 8 | 5 | Tiểu Thử 小暑 | 8 | 2 | 5 |
| Đại Hàn 大寒 | 3 | 9 | 6 | Đại Thử 大暑 | 7 | 1 | 4 |
| Lập Xuân 立春 | 8 | 5 | 2 | Lập Thu 立秋 | 2 | 5 | 8 |
| Vũ Thủy 雨水 | 9 | 6 | 3 | Xử Thử 處暑 | 1 | 4 | 7 |
| Kinh Trập 驚蟄 | 1 | 7 | 4 | Bạch Lộ 白露 | 9 | 3 | 6 |
| Xuân Phân 春分 | 3 | 9 | 6 | Thu Phân 秋分 | 7 | 1 | 4 |
| Thanh Minh 清明 | 4 | 1 | 7 | Hàn Lộ 寒露 | 6 | 9 | 3 |
| Cốc Vũ 穀雨 | 5 | 2 | 8 | Sương Giáng 霜降 | 5 | 8 | 2 |
| Lập Hạ 立夏 | 4 | 1 | 7 | Lập Đông 立冬 | 6 | 9 | 3 |
| Tiểu Mãn 小滿 | 5 | 2 | 8 | Tiểu Tuyết 小雪 | 5 | 8 | 2 |
| Mang Chủng 芒種 | 6 | 3 | 9 | Đại Tuyết 大雪 | 4 | 7 | 1 |

Structural invariant (s3.2): each of the eight outer palaces governs three consecutive terms, and the Luoshu number of the palace equals the thuong-nguyen cuc of the first of those terms - Đông Chí Khảm 1, Lập Xuân Cấn 8, Xuân Phân Chấn 3, Lập Hạ Tốn 4, Hạ Chí Ly 9, Lập Thu Khôn 2, Thu Phân Đoài 7, Lập Đông Càn 6. From the thuong nguyen the cuc steps forward in duong don and backward in am don. A unit test SHALL assert the table obeys this invariant so a transcription slip is caught mechanically.

### Phu dau, sieu than tiep khi, tri nhuan (Claude-03 s3.3)

The phu dau is the day that anchors which nguyen a run of days is in. Thuong nguyen begins on a Giáp or Kỷ day. The day branch selects the nguyen:

- branch in Tý 子 / Ngọ 午 / Mão 卯 / Dậu 酉 -> thuong nguyen (上元)
- branch in Dần 寅 / Thân 申 / Tỵ 巳 / Hợi 亥 -> trung nguyen (中元)
- branch in Thìn 辰 / Tuất 戌 / Sửu 丑 / Mùi 未 -> ha nguyen (下元)

Concretely: Giáp Tý, Giáp Ngọ, Kỷ Mão, Kỷ Dậu open thuong nguyen; Giáp Dần, Giáp Thân, Kỷ Tỵ, Kỷ Hợi open trung nguyen; Giáp Thìn, Giáp Tuất, Kỷ Sửu, Kỷ Mùi open ha nguyen.

Because 3 x 5 x 24 = 360 QiMen days do not fill the 365-day solar year, the phu dau drifts against the term. A phu dau arriving before the term is sieu than (超神), after the term is tiep khi (接氣), and on the same day is chinh thu (正授). When the drift accumulates to about nine days, a repeated term is inserted - tri nhuan (置閏) - and it is inserted only at Mang Chung 芒種 or Dai Tuyet 大雪.

### The three methods (flag `dingju_method`)

- `chaibu` (拆補法, sach bo / chiet bo): use the nearest phu dau and split-and-fill to line up, without a leap term. Simple, common in modern apps. Default.
- `zhirun` (置閏法, tri nhuan): insert the repeated term at Mang Chung and Dai Tuyet to keep the tam-nguyen cadence. Traditional.
- `maoshan` (茅山道人法): the Mao Son dao nhan resolution, a distinct school rule.

s9.1 also names a fourth resolution, am duong thuan nghich (陰陽順逆), which places the cuc purely by don direction without a leap term; it belongs to the number-theory lineage and is reached through `yin_yang_pan` (FR-QMDG-004), not through this flag. This flag stays a closed three-value enum (strategy RISK-7).

### Public types and entry point

```rust
pub enum TamNguyen { Thuong, Trung, Ha }            // serializes 上元 / 中元 / 下元 in ban, thuong/trung/ha in lich_phap
pub enum DingJuMethod { Chaibu, Zhirun, Maoshan }   // default Chaibu

pub struct DinhCuc {
    pub tiet_khi: &'static str,   // han name of the term in force, e.g. "冬至"
    pub tam_nguyen: TamNguyen,
    pub duong_don: bool,          // true = yang (forward), false = yin (reverse)
    pub so_cuc: u8,               // 1..=9
    pub phu_dau: GanChi,          // the fu-tou day that anchored the nguyen
    pub method: DingJuMethod,     // stamped into co_truong_phai
}

// ctx carries the tiet khi + tam nguyen + tu tru from FR-CORE-005.
pub fn dinh_cuc(ctx: &LichPhap, flags: &QiMenFlags) -> Result<DinhCuc, QiMenError>;
```

`QiMenFlags` (defined in `flags.rs`, extended by later FRs) carries `dingju_method` here; FR-QMDG-003/004 add `pan_method`, `yin_yang_pan`, `zhong_gong_ky`. Only the flags this step consumed are stamped by this step.

## §4 - Acceptance criteria

1. For every (tiet khi, tam nguyen) pair, `so_cuc` and `duong_don` match the s3.2 table; an enumerated unit test walks all 24 x 3 = 72 cells.
2. The structural invariant holds: for each of the eight outer palaces, the palace Luoshu number equals the thuong-nguyen cuc of its first governed term; a unit test asserts it.
3. The phu dau branch-to-nguyen mapping is correct for all twelve branches; a unit test enumerates the sixty jia-zi days and checks the nguyen.
4. `dingju_method` is honored: with the same instant, `chaibu`, `zhirun`, and `maoshan` produce the documented result, and a sieu-than / tiep-khi boundary day resolves to the method-specific nguyen (matched against kinqimen).
5. tri nhuan is inserted only at Mang Chung or Dai Tuyet under `zhirun`; an attempt to insert it elsewhere is a defect and is covered by a negative test.
6. `dinh_cuc` matches the kinqimen oracle on `so_cuc` and `duong_don` across a sample covering all 24 terms x 3 nguyen, for each `dingju_method`; the fixture in `tests/fixtures/` drives the gate.

## §5 - Verification

- `tests/dinh_cuc_oracle.rs` loads `fixtures/dinh_cuc_kinqimen.csv` (generated once from kinqimen with the day, hour, flags, and expected so_cuc / don) and asserts an exact match per row, iterating the `dingju_method` enum. This is the RISK-7 gate; it MUST run in CI.
- Table unit tests: the 72-cell exhaustive check, the structural invariant, and the branch-to-nguyen enumeration described in §4.
- Boundary tests: a dedicated set of sieu-than, tiep-khi, and chinh-thu days near Mang Chung and Dai Tuyet, one per method, asserting the nguyen and cuc the oracle gives.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`.

## §6 - Implementation skeleton

1. Create the `cyberos-qimen` crate; add `flags.rs` with `QiMenFlags` (only `dingju_method` populated at this FR, other fields added by later FRs with their defaults).
2. Encode the s3.2 table as a static `[(term, [thuong, trung, ha]); 24]` split into the duong and am halves; add the structural-invariant test.
3. Implement the phu dau resolver: from the tu tru day and the day branch, find the anchoring Giáp / Kỷ day and the nguyen, per method.
4. Implement `chaibu` first (nearest phu dau, no leap), then `zhirun` (leap term at Mang Chung / Dai Tuyet), then `maoshan`.
5. Assemble `DinhCuc`, stamp `method`, wire the oracle test and the boundary tests.

## §7 - Dependencies

Depends on FR-CORE-005 (the calendar module API that supplies the in-force tiet khi, its tam nguyen marker, and the four pillars). Blocks FR-QMDG-002 (bo dia ban starts from `so_cuc` and steps by `duong_don`) and FR-QMDG-006 (assembly + oracle gate). The tam-nguyen boundary with CORE is the open question flagged in FR-CORE-001 s9: CORE returns the raw term and instant, and this FR computes the QiMen tam nguyen from the phu dau, since it is QiMen-specific.

## §8 - Example payloads

Engine-native `dinh_cuc` component plus the flag stamp this step contributes to the envelope:

```json
{
  "dinh_cuc": { "tiet_khi": "冬至", "tam_nguyen": "上元", "duong_don": true, "so_cuc": 1, "phu_dau": "甲子", "method": "chaibu" },
  "co_truong_phai": { "dingju_method": "chaibu" }
}
```

`dinh_cuc(Dong Chi, thuong nguyen, chaibu)` returns `{ so_cuc: 1, duong_don: true }`; `dinh_cuc(Ha Chi, thuong nguyen, chaibu)` returns `{ so_cuc: 9, duong_don: false }`.

## §9 - Open questions

- Does `maoshan` diverge from `chaibu` outside the sieu-than / tiep-khi window, or only inside it? Default assumption: only inside it; confirm from the count of divergent boundary days the oracle harness reports, and record the divergence set as a fixture.
- Should the fourth s9.1 resolution (am duong thuan nghich) be a fourth `dingju_method` value or stay coupled to `yin_yang_pan`? Decision: keep it under `yin_yang_pan` (FR-QMDG-004), because it is the number-theory lineage's cuc rule, not a drift-absorption method. Revisit if kinqimen models it independently.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Wrong nguyen | phu dau branch-to-nguyen mismap | sixty-jia-zi enumeration test fails; do not ship |
| Sieu than / tiep khi mishandled | nearest phu dau chosen wrong | oracle diverges at boundary days; method-specific boundary test fails |
| tri nhuan misplaced | leap term inserted outside Mang Chung / Dai Tuyet | negative test fails; assertion guards the insert site |
| Yang/yin half wrong | Dong Chi vs Ha Chi split off by one term | direction unit test fails |
| Table transcription slip | a cell copied wrong from s3.2 | structural-invariant test fails |
| Center cuc confusion | so_cuc 5 mishandled downstream | this FR returns raw so_cuc; center-palace lodging is FR-QMDG-003 |

## §11 - Notes

This is the highest-variance FR in the QiMen engine (strategy RISK-7): the same instant can yield a different cuc under a different `dingju_method`, so the oracle gate MUST run per method, not just for the default. The crate name `cyberos-qimen` is shared with FR-QMDG-002..006 - they extend this crate. Keep `flags.rs` the single home of `QiMenFlags` so the flag set grows in one place and the envelope stamp stays complete.
