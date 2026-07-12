---
id: FR-LN-004
title: "Muoi hai thien tuong (twelve generals) - khoi quy nhan by day stem and tru/da quy, thuan bo / nghich bo by the quy nhan palace, cat/hung tuong; flags khoi_quy_nhan and quy_nhan_variant; emits thien_tuong into the la so ban for he=luc_nham"
module: LN
priority: MUST
status: done
phase: P1
slice: 4
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-02 s5, Grok-29]
related_frs: [FR-LN-001, FR-LN-002, FR-LN-003, FR-LN-005, FR-LN-006, FR-PLAT-002]
depends_on: [FR-LN-002]
blocks: [FR-LN-005, FR-LN-006]
new_paths:
  - crates/cyberos-luchnham/src/thientuong.rs
  - crates/cyberos-luchnham/tests/thientuong_oracle.rs
  - crates/cyberos-luchnham/tests/fixtures/thientuong_kinliuren.csv
---

## §1 - Description (BCP-14 normative)

This FR places the muoi hai thien tuong (十二天將), the twelve generals, over the board, giving each chi its second layer of meaning. It extends the `cyberos-luchnham` crate.

The module SHALL start the arrangement from Quy Nhan (貴人, the Thien At noble), whose palace is fixed by the day stem and by whether the consultation is by day or by night (tru quy 晝貴 or da quy 夜貴), per the ca quyet lookup (Claude-02 s5.1). The module SHALL select tru quy or da quy from the gio chiem: by the classical threshold, gio Mao through gio Than uses tru quy and gio Dau through gio Dan uses da quy. The threshold SHALL be a configuration parameter defaulting to the Mao..Than window, and the resolved choice SHALL be stamped as `khoi_quy_nhan` (tru_quy or da_quy) in `co_truong_phai`.

The module SHALL then lay the remaining eleven generals in the fixed sequence Quy Nhan, Dang Xa, Chu Tuoc, Luc Hop, Cau Tran, Thanh Long, Thien Khong, Bach Ho, Thai Thuong, Huyen Vu, Thai Am, Thien Hau, with the direction determined by where Quy Nhan lands (Claude-02 s5.2): thuan bo (順布, forward) when Quy Nhan is in the palaces Hoi Ty Suu Dan Mao Thin, nghich bo (逆布, reverse) when it is in Ti Ngo Mui Than Dau Tuat. Each general co-locates with one palace and therefore annotates the thien ban chi resting on that palace (FR-LN-001).

The module SHALL support the Giap grouping variant as a flag `quy_nhan_variant` (default giap_mau_canh, the alternative tach_giap moving Giap's noble to Mui per the di ban "Giap duong Mau Canh nguu" reading), and SHALL classify each general as cat (吉), hung (凶), or trung tinh (中, Thien Khong, leaning unfavorable) per Claude-02 s5.3. It SHALL emit the arrangement into `ban.thien_tuong` of the la so envelope (FR-PLAT-002) under `he = "luc_nham"` and stamp the LN flag set. The oracle is kinliuren.

## §2 - Why this design (rationale for humans)

The generals are the sole part of a LiuRen chart that depends on a real day/night decision, which is why the tru/da quy choice is stamped rather than assumed. The stamp matters because two operators using different day/night thresholds (the fixed Mao..Than window versus a true sunrise/sunset boundary) will place a different Quy Nhan and therefore a different eleven-general ring, and without the stamp their charts silently disagree (strategy 4.4, the flag invariant; strategy RISK-2). Making the threshold a parameter and stamping the result is the same flag discipline the platform requires everywhere.

The forward/reverse rule is the classic placement trap. The direction is not a free choice; it is fixed by which half of the ring Quy Nhan occupies, and getting it backwards mirrors the entire general layout - every general lands on the wrong chi while the chart still looks well-formed. That is why the acceptance criteria enumerate both a thuan-bo and a nghich-bo board rather than trusting a single example.

The Giap grouping variant is the one genuine school split in the twelve generals. Most schools group Giap with Mau and Canh (noble at Suu day / Mui night); a minority split Giap out (noble at Mui) under the "Giap duong" reading. Both are defensible, so neither is hardcoded; the default is the common grouping and the alternative is a flag, exactly as the platform treats every school difference.

## §3 - Contract (algorithm and types)

### Khoi quy nhan by day stem and day/night (Claude-02 s5.1, reproduced)

| Can ngày | Trú quý (ngày) | Dạ quý (đêm) |
|---|---|---|
| 甲 戊 庚 Giáp Mậu Canh | 丑 Sửu | 未 Mùi |
| 乙 己 Ất Kỷ | 子 Tý | 申 Thân |
| 丙 丁 Bính Đinh | 亥 Hợi | 酉 Dậu |
| 壬 癸 Nhâm Quý | 卯 Mão | 巳 Tỵ |
| 辛 Tân | 午 Ngọ | 寅 Dần |

Ca quyet: "Giáp Mậu Canh ngưu dương, Ất Kỷ thử hầu hương, Bính Đinh trư kê vị, Nhâm Quý thố xà tàng, lục Tân phùng mã hổ." The first chi of each pair is the tru quy (day), the second the da quy (night). The di ban "Giáp dương Mậu Canh ngưu" moves Giap's noble to Mui and is selected by `quy_nhan_variant = tach_giap`; the default giap_mau_canh keeps the table above.

Day/night selection: gio Mao through gio Than -> tru quy; gio Dau through gio Dan -> da quy. The window is a parameter (default Mao..Than); some schools use true sunrise/sunset.

### Thuan bo and nghich bo (Claude-02 s5.2, reproduced)

After Quy Nhan is placed, the other eleven follow in this fixed sequence:

Quý nhân (貴人), Đằng xà (螣蛇), Chu tước (朱雀), Lục hợp (六合), Câu trần (勾陳), Thanh long (青龍), Thiên không (天空), Bạch hổ (白虎), Thái thường (太常), Huyền vũ (玄武), Thái âm (太陰), Thiên hậu (天后).

Direction by the Quy Nhan palace:

- Quy Nhan in Hợi Tý Sửu Dần Mão Thìn -> thuan bo (forward, along the canonical chi order).
- Quy Nhan in Tỵ Ngọ Mùi Thân Dậu Tuất -> nghich bo (reverse).

Each successive general occupies the next (or previous) palace, so all twelve generals map one-to-one onto the twelve palaces and thereby onto the twelve thien ban chi.

### Cat tuong and hung tuong (Claude-02 s5.3, reproduced)

Cat: Quy Nhan, Luc Hop, Thanh Long, Thien Hau, Thai Am, Thai Thuong. Hung: Dang Xa, Chu Tuoc, Cau Tran, Huyen Vu, Bach Ho. Thien Khong is trung tinh, leaning unfavorable.

| Tướng | Cát hung | Loại việc chủ |
|---|---|---|
| 貴人 Quý nhân | Cát | Quý nhân giúp đỡ, quan chức, việc lớn |
| 螣蛇 Đằng xà | Hung | Kinh sợ, quái dị, việc rối |
| 朱雀 Chu tước | Hung | Văn thư, tin tức, khẩu thiệt, kiện tụng |
| 六合 Lục hợp | Cát | Hợp tác, hôn nhân, trung gian |
| 勾陳 Câu trần | Hung | Tranh chấp, ràng buộc, đình trệ |
| 青龍 Thanh long | Cát | Tài lộc, hỷ sự, thăng tiến |
| 天空 Thiên không | Bất lợi | Hư dối, trống rỗng, thất tín |
| 白虎 Bạch hổ | Hung | Tật bệnh, tang thương, đường xa, tranh đấu |
| 太常 Thái thường | Cát | Ăn uống, y phục, lễ nghi, ban thưởng |
| 玄武 Huyền vũ | Hung | Trộm cắp, mất mát, ẩn khuất, lừa dối |
| 太陰 Thái âm | Cát | Ẩn giấu, nữ nhân, riêng tư, che chở |
| 天后 Thiên hậu | Cát | Nữ nhân, tình cảm, hôn nhân, âm trợ |

### Public types (`crates/cyberos-luchnham/src/thientuong.rs`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ThienTuong {
    QuyNhan, DangXa, ChuTuoc, LucHop, CauTran, ThanhLong,
    ThienKhong, BachHo, ThaiThuong, HuyenVu, ThaiAm, ThienHau,   // fixed ring order
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CatHung { Cat, Hung, TrungTinh }         // Thien Khong = TrungTinh (leaning hung)

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TruDa { TruQuy, DaQuy }                  // 晝貴 day noble | 夜貴 night noble

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ChieuBo { Thuan, Nghich }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum QuyNhanVariant { GiapMauCanh, TachGiap }

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AnThienTuong {
    pub tren_cung: [ThienTuong; 12],   // general over dia ban palace i (co-located with thien_ban[i])
    pub quy_nhan_chi: Chi,             // the palace Quy Nhan occupies
    pub tru_da: TruDa,
    pub chieu: ChieuBo,
}

pub fn quy_nhan_chi(can: Can, tru_da: TruDa, variant: QuyNhanVariant) -> Chi;
pub fn chon_tru_da(gio_chiem: Chi, cua_so_ngay: (Chi, Chi)) -> TruDa;   // default (Mao, Than)
pub fn an_thien_tuong(ban: &ThienDiaBan, can_ngay: Can, tru_da: TruDa,
                      variant: QuyNhanVariant) -> AnThienTuong;
pub fn cat_hung(t: ThienTuong) -> CatHung;
```

## §4 - Acceptance criteria

1. `quy_nhan_chi` is correct for all ten stems in both tru and da quy under the default giap_mau_canh (matching the s5.1 table), and the tach_giap variant moves only Giap's noble to Mui.
2. `chon_tru_da` returns TruQuy for gio Mao..Than and DaQuy for gio Dau..Dan under the default window, and honors a custom window parameter.
3. Direction: a board whose Quy Nhan lands in Hoi Ty Suu Dan Mao Thin arranges thuan bo; one landing in Ti Ngo Mui Than Dau Tuat arranges nghich bo. Both enumerated, and the eleven following generals land on the correct palaces in each.
4. All twelve generals appear exactly once across the twelve palaces (a bijection), for every sampled board and direction.
5. `cat_hung` matches s5.3 for all twelve, with Thien Khong classified TrungTinh.
6. The emitted `ban.thien_tuong` round-trips through the la so envelope (FR-PLAT-002) under `he = "luc_nham"`, `co_truong_phai` carries `khoi_quy_nhan` (the resolved tru/da) and `quy_nhan_variant`, and the whole arrangement matches kinliuren across day stem x day/night x variant.

## §5 - Verification

- Unit: `quy_nhan_chi` over ten stems x {tru, da} x {giap_mau_canh, tach_giap}; `chon_tru_da` across the twelve gio at the default window and one custom window; a thuan-bo and a nghich-bo board with the full eleven-general placement checked; the bijection property; `cat_hung` over twelve generals.
- Oracle: `tests/thientuong_oracle.rs` loads `fixtures/thientuong_kinliuren.csv` (>= 500 cases spanning day stem, day/night, board offset, and both variants, generated once from kinliuren and committed) and asserts the twelve-palace arrangement is identical for every case.
- Property: for 10,000 random (board, day stem, day/night, variant) tuples, the twelve generals form a bijection over the palaces and Quy Nhan sits on its computed palace.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-luchnham -- -D warnings`, `cargo test -p cyberos-luchnham`.

## §6 - Implementation skeleton

1. `thientuong.rs`: `ThienTuong` (ring order), `CatHung`, `TruDa`, `ChieuBo`, `QuyNhanVariant`, `AnThienTuong` types.
2. `quy_nhan_chi`: the s5.1 table with the tach_giap override.
3. `chon_tru_da`: window test on the gio chiem (default Mao..Than).
4. `an_thien_tuong`: place Quy Nhan, decide thuan/nghich from its palace, walk the fixed sequence in that direction across palaces.
5. `cat_hung`: static classification.
6. Extend `flags.rs` (FR-LN-001) to carry `quy_nhan_variant`; stamp `khoi_quy_nhan` (resolved tru/da) and `quy_nhan_variant` into `co_truong_phai`; emit `AnThienTuong` into `ban.thien_tuong` for `he = "luc_nham"`.
7. Generate the kinliuren fixture once (documented script, not run in CI) spanning both variants and commit; wire the oracle and property tests.

## §7 - Dependencies

Depends on FR-LN-002 for crate sequencing; the hard data input is FR-LN-001's `ThienDiaBan` (the generals ride the thien ban) plus the day stem and gio chiem from FR-CORE-005. Extends the FR-LN-001 `flags.rs` flag set with `quy_nhan_variant`. Blocks FR-LN-005 (khoa the read the general a spirit rides) and FR-LN-006 (assembly). Emits into the FR-PLAT-002 envelope.

## §8 - Example payloads

`ban.thien_tuong` slice (a general per palace, co-located with the thien ban chi over that palace):

```json
{ "envelope_version": 1, "he": "luc_nham",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "cong_danh" },
  "lich_phap": { "...": "from FR-CORE-005" },
  "ban": {
    "thien_dia_ban": { "...": "from FR-LN-001" },
    "tu_khoa": [ "...": "from FR-LN-002" ],
    "tam_truyen": { "...": "from FR-LN-003" },
    "thien_tuong": {
      "quy_nhan_chi": "丑", "tru_da": "tru_quy", "chieu": "thuan",
      "tren_cung": ["貴人","螣蛇","朱雀","六合","勾陳","青龍","天空","白虎","太常","玄武","太陰","天后"]
    }
  },
  "cach_cuc": [],
  "co_truong_phai": { "khoi_quy_nhan": "tru_quy", "quy_nhan_variant": "giap_mau_canh", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "..." } }
```

`tren_cung[i]` is the general over dia ban palace `i` (index 0 = Ty). Here Quy Nhan sits in Suu (a Giap day-time noble) so the arrangement is thuan bo. The illustrative array shows the sequence starting at Quy Nhan's palace; the concrete per-palace assignment for any board is pinned by kinliuren.

## §9 - Open questions

- Placement anchor: this FR reads the "Quy Nhan palace" as the dia ban palace of the computed noble chi (Claude-02 s5.2, "vi tri quy nhan tren dia ban"), then walks palaces; an alternative anchors on the palace whose thien ban chi equals the noble. Confirm the anchor against kinliuren before locking, since the two can differ and it changes the whole ring. This is the single highest-risk ambiguity in this slice.
- Day/night threshold: default is the fixed Mao..Than window; a sunrise/sunset school is a parameter. Decide whether the platform ever needs the astronomical boundary (it would consume FR-CORE-002 true solar time) or whether the fixed window suffices for MVP.
- Giap grouping default: giap_mau_canh is the default and tach_giap the flagged alternative. Confirm kinliuren's default matches so the un-flagged chart agrees with the oracle out of the box.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Direction reversed | thuan/nghich decided from the wrong ring half | nghich-bo enumerated case mirrors the ring; oracle fails |
| Wrong day/night | tru/da chosen from the wrong window or wrong gio | Quy Nhan palace wrong; whole arrangement diverges |
| Placement anchor off | anchoring on thien ban chi vs dia ban palace | ring shifted; oracle diverges on non-trivial boards |
| Giap variant hardcoded | ignoring `quy_nhan_variant` | tach_giap case places Giap's noble at Suu instead of Mui |
| General not a bijection | sequence walk steps by the wrong amount | bijection property fails: a palace has two or zero generals |
| Unstamped day/night | `khoi_quy_nhan` not written | reproduction from stamp diverges; envelope CI fails |

## §11 - Notes

The generals are the day/night-sensitive layer, so this slice is where the LiuRen engine first exercises a real school flag beyond the ky cung and rotation. `quy_nhan_variant` joins `khoi_quy_nhan` and `truong_sinh_phai` in the LN flag set, and all three are stamped from here on so a chart stays reproducible from its stamp. The placement anchor (§9) is the load-bearing ambiguity - resolve it against kinliuren early, because it silently rotates every general if wrong. Oracle kinliuren; the twelve-general arrangement is part of the FR-LN-006 100% gate.
