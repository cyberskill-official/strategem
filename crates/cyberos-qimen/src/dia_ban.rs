//! Bo dia ban (布地盤) — FR-QMDG-002.

use crate::dinh_cuc::DinhCuc;
use serde::{Deserialize, Serialize};

/// Visible stems on the earth plate (six nghi + three qi). Giap never appears.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Stem {
    Mau,  // 戊
    Ky,   // 己
    Canh, // 庚
    Tan,  // 辛
    Nham, // 壬
    Quy,  // 癸
    Dinh, // 丁
    Binh, // 丙
    At,   // 乙
}

impl Stem {
    pub const SEQ: [Stem; 9] = [
        Stem::Mau,
        Stem::Ky,
        Stem::Canh,
        Stem::Tan,
        Stem::Nham,
        Stem::Quy,
        Stem::Dinh,
        Stem::Binh,
        Stem::At,
    ];

    pub fn glyph(self) -> &'static str {
        match self {
            Stem::Mau => "戊",
            Stem::Ky => "己",
            Stem::Canh => "庚",
            Stem::Tan => "辛",
            Stem::Nham => "壬",
            Stem::Quy => "癸",
            Stem::Dinh => "丁",
            Stem::Binh => "丙",
            Stem::At => "乙",
        }
    }
}

/// Earth plate: index 0..8 maps to palace numbers 1..9.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct DiaBan {
    pub cung: [Stem; 9],
}

impl DiaBan {
    pub fn at_palace(&self, palace: u8) -> Stem {
        assert!((1..=9).contains(&palace));
        self.cung[(palace - 1) as usize]
    }
}

/// Advance one step in Luoshu palace numbers 1..=9 (wrap 9→1).
pub fn buoc_thuan_lac_thu(cung: u8) -> u8 {
    if cung >= 9 {
        1
    } else {
        cung + 1
    }
}

/// Step backward one palace (wrap 1→9).
pub fn buoc_nghich_lac_thu(cung: u8) -> u8 {
    if cung <= 1 {
        9
    } else {
        cung - 1
    }
}

/// Place luc nghi + tam ky starting at so_cuc, direction from duong_don.
pub fn bo_dia_ban(dinh: &DinhCuc) -> DiaBan {
    bo_dia_ban_raw(dinh.so_cuc, dinh.duong_don)
}

pub fn bo_dia_ban_raw(so_cuc: u8, duong_don: bool) -> DiaBan {
    assert!((1..=9).contains(&so_cuc));
    let mut dia = [Stem::Mau; 9];
    let mut cung = so_cuc;
    for stem in Stem::SEQ {
        dia[(cung - 1) as usize] = stem;
        cung = if duong_don {
            buoc_thuan_lac_thu(cung)
        } else {
            buoc_nghich_lac_thu(cung)
        };
    }
    DiaBan { cung: dia }
}
