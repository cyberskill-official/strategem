//! Toan counting — TASK-TAT-003 / W3 classical palace numbers.

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

/// Classical Luoshu palace number for a chính cung ring mark (Claude-04 s3).
/// 坎1 坤2 震3 巽4 中5 乾6 兌7 艮8 離9.
fn palace_number(ring: u8) -> u32 {
    match ring {
        0 => 1,  // 子 坎
        2 => 8,  // 艮
        4 => 3,  // 卯 震
        6 => 4,  // 巽
        8 => 9,  // 午 離
        10 => 2, // 坤
        12 => 7, // 酉 兌
        14 => 6, // 乾
        _ => 1,  // gian thần should not call this; caller adds 1
    }
}

pub fn mark_before(ring: u8) -> u8 {
    if ring == 0 {
        15
    } else {
        ring - 1
    }
}

/// Count toán from `start_ring` around the 16-god ring.
/// Chính cung contribute their Luoshu number; gian thần contribute 1.
/// Stop at the mark immediately before Thái Ất (`TruocThaiAt`) or on Thái Ất
/// (`SauThaiAt`) per `dem_toan` school flag.
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
    // Claude-04: ≥11 trường, ≤9 đoản (10 treated as đoản here).
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn luoshu_palace_pins() {
        assert_eq!(palace_number(0), 1); // 坎
        assert_eq!(palace_number(8), 9); // 離
        assert_eq!(palace_number(14), 6); // 乾
        assert_eq!(palace_number(2), 8); // 艮
    }
}
