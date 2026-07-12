//! Toan counting — FR-TAT-003.

use crate::anthaiat::ThaiAtSeat;
use crate::thaplucthan::{is_chinh_cung, LoaiThan, THAP_LUC_THAN};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum DemToan {
    #[default]
    TruocThaiAt,
    SauThaiAt,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TruongDoan {
    Truong,
    Doan,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct ToanResult {
    pub value: u32,
    pub label: TruongDoan,
}

/// Palace number contribution for a chinh cung ring mark (simplified mapping).
fn palace_number(ring: u8) -> u32 {
    match ring {
        0 => 8,  // 子 坎
        2 => 3,  // 艮
        4 => 4,  // 卯 震
        6 => 9,  // 巽
        8 => 2,  // 午 離 (TAT layout)
        10 => 7, // 坤
        12 => 6, // 酉 兌
        14 => 1, // 乾
        _ => 1,
    }
}

pub fn mark_before(ring: u8) -> u8 {
    if ring == 0 {
        15
    } else {
        ring - 1
    }
}

pub fn compute_toan(start_ring: u8, seat: &ThaiAtSeat, dem: DemToan) -> ToanResult {
    let stop = match dem {
        DemToan::TruocThaiAt => mark_before(seat.thai_at_ring),
        DemToan::SauThaiAt => seat.thai_at_ring,
    };
    let mut total = 0u32;
    let mut mark = start_ring;
    for _ in 0..16 {
        if is_chinh_cung(mark) {
            total += palace_number(mark);
        } else {
            total += 1;
        }
        if mark == stop {
            break;
        }
        mark = (mark + 1) % 16;
    }
    let label = if total >= 11 {
        TruongDoan::Truong
    } else {
        TruongDoan::Doan
    };
    ToanResult {
        value: total,
        label,
    }
}

pub fn dai_tuong_cung(toan: u32) -> u8 {
    if matches!(toan, 10 | 20 | 30 | 40) {
        let m = (toan % 9) as u8;
        if m == 0 {
            9
        } else {
            m
        }
    } else {
        let u = (toan % 10) as u8;
        if u == 0 {
            9
        } else {
            u
        }
    }
}

pub fn tham_tuong_cung(dai: u8) -> u8 {
    let v = (dai as u16 * 3 - 1) % 9 + 1;
    v as u8
}

/// Ensure THAP_LUC_THAN loai used.
pub fn count_chinh() -> usize {
    THAP_LUC_THAN
        .iter()
        .filter(|t| t.loai == LoaiThan::ChinhCung)
        .count()
}
