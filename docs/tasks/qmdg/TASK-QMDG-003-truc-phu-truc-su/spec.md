---
id: TASK-QMDG-003
title: "Truc phu / truc su + thien ban rotation - tuan-thu hidden-nghi lookup, locate on dia ban, rotate sky plate to the hour-stem palace, pan_method flag (zhuan/fei) + zhong_gong_ky"
module: QMDG
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-2, Claude-03 s5]
related_frs: [TASK-QMDG-002, TASK-QMDG-004, TASK-QMDG-006]
depends_on: [TASK-QMDG-002]
blocks: [TASK-QMDG-004, TASK-QMDG-006]
new_paths:
  - crates/cyberos-qimen/src/truc_phu_su.rs
  - crates/cyberos-qimen/tests/truc_phu_su_oracle.rs
---

## §1 - Description (BCP-14 normative)

This task implements the pivot that makes a QiMen chart specific to the hour: find the truc phu (值符, the leading star) and truc su (值使, the leading door), then rotate the thien ban (sky plate) so the truc phu and its nghi sit over the palace that holds the hour stem. It is the step that binds the still earth plate (TASK-QMDG-002) to the moment of the question, and it is one of the sharpest school-fork points in the whole engine (s5.2).

The module SHALL, per the four steps of s5.1: (1) from the hour ganzhi, find the tuan thu (旬首, the jia-decade head that contains the hour) and its hidden nghi from the six-tuan table in §3; (2) locate that nghi on the earth plate to get the tuan-thu palace; (3) read the resting cuu tinh star and resting bat mon door at that palace as truc phu and truc su; (4) rotate the sky plate so the truc phu and its nghi move to the hour-stem palace, carrying the other stems, while the truc su is carried by counting from the tuan-thu palace to the hour palace.

The module SHALL support two rotation lineages behind the flag `pan_method` in {`zhuan`, `fei`}, default `zhuan` (chuyen ban): `zhuan` rotates the nine stars as a rigid wheel; `fei` (phi ban) flies each star by its own Luoshu number, so the two produce different charts at the same hour. It SHALL resolve center-palace lodging behind the flag `zhong_gong_ky` in {`khon2`, `giu_nguyen`}, default `khon2` (a star or door landing in Trung 5 lodges to Khôn 2). Both flags SHALL be stamped into `co_truong_phai` (TASK-PLAT-002).

## §2 - Why this design (rationale for humans)

Truc phu and truc su are the hinge of the chart: every star and door turns around them, so a wrong hour-stem palace is a wrong chart everywhere at once (s10.3). That is why this step gets the second-highest test density after dinh cuc.

The chuyen-ban / phi-ban fork is not a rounding difference - the two lineages give genuinely different charts for the same instant, and their users reject each other's results (strategy RISK-2). Hardcoding either one would silently pick a side. So the rotation is a stamped flag with `zhuan` as the default because it is the most common thoi-gia practice, and the oracle gate runs both. The center-palace rule is a second, smaller fork: Trung 5 has no trigram of its own in many operations, so a piece landing there lodges to Khôn 2 by the usual convention - but that convention also varies, so it too is a flag rather than a constant.

## §3 - Contract (algorithm)

### Tuan thu and hidden nghi (Claude-03 s5.1, verbatim)

Each of the six jia-decades hides one nghi, the yang stem that stands in for the hidden Giáp in the layout. The hidden nghi is used to find the tuan-thu palace on the earth plate.

| Tuần | Tuần thủ | Nghi ẩn |
|---|---|---|
| 甲子 Giáp Tý | 甲子 | 戊 Mậu |
| 甲戌 Giáp Tuất | 甲戌 | 己 Kỷ |
| 甲申 Giáp Thân | 甲申 | 庚 Canh |
| 甲午 Giáp Ngọ | 甲午 | 辛 Tân |
| 甲辰 Giáp Thìn | 甲辰 | 壬 Nhâm |
| 甲寅 Giáp Dần | 甲寅 | 癸 Quý |

Each tuan spans ten hours. Example: an hour in tuan Giáp Tý has tuan thu Giáp Tý, hidden under nghi Mậu; find Mậu on the earth plate, and the star and door resting there are truc phu and truc su.

### The four steps (Claude-03 s5.1)

1. From the hour ganzhi, compute the tuan thu (the jia-decade head containing the hour) and read its hidden nghi from the table above.
2. Find that nghi's palace on the `DiaBan` from TASK-QMDG-002 - this is the tuan-thu palace.
3. The resting cuu tinh star at that palace is the truc phu; the resting bat mon door at that palace is the truc su. (The resting rings - each star's and door's home palace - are the fixtures formalized in TASK-QMDG-004; this task consumes them.)
4. Rotate the sky plate so the truc phu and its nghi move to the palace holding the hour stem; the other stems follow. The truc su is carried by counting from the tuan-thu palace to the hour palace.

### chuyen ban vs phi ban (Claude-03 s5.2, flag `pan_method`)

- `zhuan` (轉盤, chuyen ban): treat the nine stars as a rigid wheel. The truc phu moves to the hour-stem palace and the other eight stars keep their relative order and rotate along. The most common thoi-gia method. Default.
- `fei` (飛盤, phi ban): each star flies by its own Luoshu number, not as a rigid block; the landing palace of the truc phu is computed by a formula on the so cuc and the stem position.

The two give different charts at the same hour, so `pan_method` is stamped and both are gated. Do not hardcode one as the only correct method.

### Center palace and ky cung (Claude-03 s5.3, flag `zhong_gong_ky`)

Trung 5 has no trigram of its own in many steps, so a star or door landing in Trung lodges to Khôn 2 under the common convention (`khon2`, default); `giu_nguyen` keeps it in place. The rule must be applied consistently across every step or the oracle diverges.

### Public types and entry point

```rust
pub enum PanMethod { Zhuan, Fei }            // default Zhuan
pub enum ZhongGongKy { Khon2, GiuNguyen }    // default Khon2

pub struct TrucPhuSu {
    pub truc_phu: CuuTinh,        // leading star (type from TASK-QMDG-004)
    pub truc_su: BatMon,          // leading door
    pub tuan_thu: GanChi,         // the jia-decade head
    pub nghi_an: Can,             // hidden nghi
    pub cung_tuan_thu: u8,        // 1..=9, tuan-thu palace on the earth plate
    pub cung_gio: u8,             // 1..=9, palace holding the hour stem
    pub thien_ban: [Can; 9],      // rotated sky-plate stems by palace 1..9
    pub xoay: i8,                 // rotation offset consumed by TASK-QMDG-004
}

pub fn truc_phu_truc_su(dia: &DiaBan, gio: GanChi, flags: &QiMenFlags)
    -> Result<TrucPhuSu, QiMenError>;
```

## §4 - Acceptance criteria

1. The tuan thu and hidden nghi are correct for a probe in each of the six tuan; a unit test enumerates all sixty hour ganzhi and checks the tuan thu and nghi against the §3 table.
2. The tuan-thu palace equals the palace of the hidden nghi on the earth plate; a unit test cross-checks against TASK-QMDG-002 output.
3. Under `zhuan`, the sky plate is a rigid rotation carrying the truc phu to the hour-stem palace; a golden test on a worked hour asserts every palace stem.
4. Under `fei`, the sky plate matches the phi-ban formula; the two methods differ on at least the documented worked hour, proving the fork is real.
5. `zhong_gong_ky = khon2` lodges a Trung-landing piece to Khôn 2; a unit test exercises an hour whose hour stem is in the center.
6. `truc_phu_truc_su` matches the kinqimen truc phu, truc su, and sky plate across a sample, for every combination of `pan_method` and `zhong_gong_ky`.

## §5 - Verification

- `tests/truc_phu_su_oracle.rs` loads truc phu / truc su / sky-plate rows from the kinqimen fixture and asserts an exact match, iterating `pan_method` x `zhong_gong_ky`.
- Enumeration test over the sixty hour ganzhi for the tuan thu and hidden nghi.
- Golden worked-hour test asserting the full rotated sky plate under `zhuan`, plus the divergence assertion between `zhuan` and `fei`.
- Center-palace test: an hour whose hour stem lodges through Trung, checked under both `zhong_gong_ky` values.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`.

## §6 - Implementation skeleton

1. Add `truc_phu_su.rs`; encode the six-tuan hidden-nghi table and the tuan-thu computation from the hour ganzhi.
2. Locate the hidden nghi on the `DiaBan`; read the resting star and door (rings from TASK-QMDG-004, imported as consts).
3. Implement `zhuan` (rigid-wheel rotation, compute `xoay`), then `fei` (per-star Luoshu flight).
4. Apply `zhong_gong_ky` lodging uniformly; add `pan_method` and `zhong_gong_ky` to `QiMenFlags` with their defaults.
5. Wire the oracle test, the enumeration test, and the divergence test.

## §7 - Dependencies

Depends on TASK-QMDG-002 (reads the earth plate). Blocks TASK-QMDG-004 (the star / door / god rings are placed using the `xoay` offset and the truc phu / truc su this task identifies) and TASK-QMDG-006 (assembly). The resting cuu tinh and bat mon rings are formalized in TASK-QMDG-004 and imported here; within one crate they are shared consts, so there is no cyclic build dependency.

## §8 - Example payloads

The truc phu / truc su summary and the rotated sky plate for a worked hour:

```json
{ "truc_phu": "天蓬", "truc_su": "休門",
  "thien_ban": { "1": "戊", "2": "己", "9": "乙", "...": "..." },
  "co_truong_phai": { "pan_method": "zhuan", "zhong_gong_ky": "khon2" } }
```

## §9 - Open questions

- The phi-ban landing formula has minor variants across texts. Default: implement the mainstream so-cuc-plus-stem-offset form and lock it against kinqimen; if the oracle uses a different phi-ban variant, record which and gate to it, since `fei` is not the default and can be pinned precisely later.
- Whether `giu_nguyen` (keep a Trung-landing piece in place) is ever the kinqimen convention, or only `khon2` is: default to `khon2`, keep `giu_nguyen` as a reserved value, and only exercise it if a school in scope requires it.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Wrong hour-stem palace | tuan thu or nghi lookup wrong | whole chart wrong; enumeration test fails; do not ship |
| pan_method hardcoded | only zhuan implemented | fei oracle rows fail; divergence test absent |
| Rigid-wheel offset wrong | zhuan rotation miscomputed | golden sky-plate test fails |
| Center lodging inconsistent | ky cung applied in some steps only | oracle diverges on center-landing hours |
| Resting-ring drift | rings differ from TASK-QMDG-004 | shared const import prevents divergence; test cross-checks |

## §11 - Notes

This task and TASK-QMDG-004 are tightly coupled: this one identifies the pivot and rotates the stems and exposes the `xoay` offset; the next one paints the three dynamic rings using that offset. Keep the split clean - rotation math lives here, ring placement lives there - so each has a focused oracle gate. The chuyen / phi fork is the RISK-2 exemplar for QiMen: never let a default become an implicit "only correct" answer.
