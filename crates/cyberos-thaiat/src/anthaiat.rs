//! Seat Thai At on sixteen-than ring — TASK-TAT-002.

use crate::cuucung::thai_at_palace;
use crate::tichnien::TichNien;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThaiAtSeat {
    pub thai_at_cung: u8,
    pub thai_at_ring: u8,
}

/// Palace (1..=9 TAT layout) → chinh cung ring index.
/// 乾1→14, 離2→8, 艮3→2, 震4→4, 中5→10(Khon), 兌6→12, 坤7→10, 坎8→0, 巽9→6
pub fn palace_to_ring(palace: u8) -> u8 {
    match palace {
        1 => 14, // 乾 Âm đức
        2 => 8,  // 午 Đại uy
        3 => 2,  // 艮
        4 => 4,  // 卯
        5 => 10, // center → 坤
        6 => 12, // 酉
        7 => 10, // 坤
        8 => 0,  // 子
        9 => 6,  // 巽
        _ => 10,
    }
}

pub fn an_thai_at(tn: &TichNien, duong_don: bool) -> ThaiAtSeat {
    let pos = thai_at_palace(tn, duong_don);
    let cung = if pos.palace == 5 { 7 } else { pos.palace };
    let ring = palace_to_ring(cung);
    ThaiAtSeat {
        thai_at_cung: cung,
        thai_at_ring: ring,
    }
}
