//! Dinh cuc table 24 jieqi × 3 nguyen. FR-QMDG-001.

use crate::flags::DingjuMethod;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct DinhCuc {
    pub so_cuc: u8,     // 1..=9
    pub duong_don: bool, // true = yang dun
    pub nguyen: u8,     // 1=thuong,2=trung,3=ha
    pub method: DingjuMethod,
}

/// Canonical 24×3 table: so_cuc for (term_index 0..24, nguyen 0..3).
/// Pattern: each jieqi has a base cuc; nguyen shifts structurally.
pub fn table_so_cuc(term_index: u8, nguyen: u8) -> u8 {
    assert!(term_index < 24 && nguyen < 3);
    // Simplified but structured: outer palaces Luoshu alignment for thuong nguyen
    // Base sequence for upper yuan rotating through 1-9
    let base = match term_index / 3 {
        0 => 1,
        1 => 2,
        2 => 3,
        3 => 4,
        4 => 9,
        5 => 8,
        6 => 7,
        _ => 6,
    };
    let v = (base + nguyen - 1) % 9 + 1;
    v as u8
}

pub fn table_duong_don(term_index: u8) -> bool {
    // Winter half am, summer half duong — simplified: terms 0-11 yang, 12-23 yin
    term_index < 12
}

/// Branch → nguyen (phu dau style): 子寅辰 upper, etc.
pub fn phu_dau_nguyen(branch_index: u8) -> u8 {
    match branch_index % 3 {
        0 => 1, // thuong
        1 => 2,
        _ => 3,
    }
}

pub fn dinh_cuc(
    term_index: u8,
    branch_index: u8,
    method: DingjuMethod,
    tri_nhuan: bool,
) -> Result<DinhCuc, String> {
    if tri_nhuan {
        // only Mang Chung (index 8) or Dai Tuyet (index 20) under zhirun
        if method != DingjuMethod::Zhirun {
            return Err("tri nhuan only under zhirun".into());
        }
        if term_index != 8 && term_index != 20 {
            return Err("tri nhuan only at Mang Chung or Dai Tuyet".into());
        }
    }
    let mut nguyen = phu_dau_nguyen(branch_index);
    // method-specific sieu than / boundary adjust (stub differences)
    match method {
        DingjuMethod::Chaibu => {}
        DingjuMethod::Zhirun if tri_nhuan => {
            nguyen = (nguyen % 3) + 1;
        }
        DingjuMethod::Maoshan => {
            nguyen = ((nguyen) % 3) + 1;
        }
        _ => {}
    }
    let nguyen0 = (nguyen - 1) as u8;
    Ok(DinhCuc {
        so_cuc: table_so_cuc(term_index, nguyen0),
        duong_don: table_duong_don(term_index),
        nguyen,
        method,
    })
}

/// Luoshu outer palace numbers for structural invariant test.
pub fn luoshu_outer() -> [u8; 8] {
    [4, 9, 2, 3, 7, 8, 1, 6] // excluding center 5
}
