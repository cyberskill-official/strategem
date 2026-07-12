//! Cuu tinh / bat mon / bat than placement — FR-QMDG-004.

use crate::dinh_cuc::DinhCuc;
use crate::truc_phu_su::{TrucPhuSu, ZhongGongKy};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CuuTinh {
    ThienBong,
    ThienNhue,
    ThienXung,
    ThienPhu,
    ThienCam,
    ThienTam,
    ThienTru,
    ThienNham,
    ThienAnh,
}

impl CuuTinh {
    pub const REST: [CuuTinh; 9] = [
        CuuTinh::ThienBong,
        CuuTinh::ThienNhue,
        CuuTinh::ThienXung,
        CuuTinh::ThienPhu,
        CuuTinh::ThienCam,
        CuuTinh::ThienTam,
        CuuTinh::ThienTru,
        CuuTinh::ThienNham,
        CuuTinh::ThienAnh,
    ];
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BatMon {
    Huu,
    Sinh,
    Thuong,
    Do,
    Canh,
    Tu,
    Kinh,
    Khai,
}

impl BatMon {
    /// Resting doors for palaces 1..9 (None at Trung 5).
    pub const REST: [Option<BatMon>; 9] = [
        Some(BatMon::Huu),
        Some(BatMon::Tu),
        Some(BatMon::Thuong),
        Some(BatMon::Do),
        None,
        Some(BatMon::Khai),
        Some(BatMon::Kinh),
        Some(BatMon::Sinh),
        Some(BatMon::Canh),
    ];

    pub fn is_cat(self) -> bool {
        matches!(self, BatMon::Khai | BatMon::Huu | BatMon::Sinh)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BatThan {
    TrucPhu,
    DangXa,
    ThaiAm,
    LucHop,
    BachHo,
    HuyenVu,
    CuuDia,
    CuuThien,
    // am-lineage extras used after swap
    CauTran,
    ChuTuoc,
}

impl BatThan {
    pub const DUONG: [BatThan; 8] = [
        BatThan::TrucPhu,
        BatThan::DangXa,
        BatThan::ThaiAm,
        BatThan::LucHop,
        BatThan::BachHo,
        BatThan::HuyenVu,
        BatThan::CuuDia,
        BatThan::CuuThien,
    ];

    pub fn am_swap(self) -> BatThan {
        match self {
            BatThan::BachHo => BatThan::CauTran,
            BatThan::CauTran => BatThan::BachHo,
            BatThan::HuyenVu => BatThan::ChuTuoc,
            BatThan::ChuTuoc => BatThan::HuyenVu,
            other => other,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum YinYangPan {
    #[default]
    Duong,
    Am,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct SaoMonThan {
    pub cuu_tinh: [CuuTinh; 9],
    pub bat_mon: [Option<BatMon>; 9],
    pub bat_than: [Option<BatThan>; 9],
    pub yin_yang_pan: YinYangPan,
}

fn rotate_stars(xoay: i8) -> [CuuTinh; 9] {
    let mut out = [CuuTinh::ThienBong; 9];
    for p in 0..9 {
        let src = (p as i16 - xoay as i16).rem_euclid(9) as usize;
        out[p] = CuuTinh::REST[src];
    }
    out
}

fn rotate_doors(xoay: i8, zhong: ZhongGongKy) -> [Option<BatMon>; 9] {
    let mut out = [None; 9];
    for p in 0..9 {
        if p == 4 {
            // Trung 5 has no door
            out[p] = None;
            continue;
        }
        let src = (p as i16 - xoay as i16).rem_euclid(9) as usize;
        let mut door = BatMon::REST[src];
        if src == 4 {
            // source was Trung — lodge
            door = match zhong {
                ZhongGongKy::Khon2 => BatMon::REST[1], // palace 2
                ZhongGongKy::GiuNguyen => None,
            };
        }
        out[p] = door;
    }
    out
}

fn place_gods(
    truc_phu_palace: u8,
    duong_don: bool,
    lineage: YinYangPan,
) -> [Option<BatThan>; 9] {
    let mut out = [None; 9];
    let ring = BatThan::DUONG;
    let mut p = if truc_phu_palace == 0 {
        1
    } else {
        truc_phu_palace
    };
    // walk 8 outer palaces (skip center when stepping)
    let mut placed = 0usize;
    while placed < 8 {
        if p != 5 {
            let mut god = ring[placed];
            if lineage == YinYangPan::Am {
                god = god.am_swap();
            }
            out[(p - 1) as usize] = Some(god);
            placed += 1;
        }
        p = if duong_don {
            if p >= 9 {
                1
            } else {
                p + 1
            }
        } else if p <= 1 {
            9
        } else {
            p - 1
        };
    }
    out
}

pub fn sao_mon_than(
    tps: &TrucPhuSu,
    dinh: &DinhCuc,
    lineage: YinYangPan,
) -> SaoMonThan {
    SaoMonThan {
        cuu_tinh: rotate_stars(tps.xoay),
        bat_mon: rotate_doors(tps.xoay, tps.zhong_gong_ky),
        bat_than: place_gods(tps.cung_tuan_thu, dinh.duong_don, lineage),
        yin_yang_pan: lineage,
    }
}
