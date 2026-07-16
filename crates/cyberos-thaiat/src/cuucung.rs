//! Thai At palace movement — TASK-TAT-001.

use crate::tichnien::TichNien;
use serde::{Deserialize, Serialize};

/// Thai At layout palace 1..=9 (5 = center, skipped).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThaiAtPosition {
    pub palace: u8, // 1..=9, never 5 after lodging
    pub duong_don: bool,
}

/// Outer palaces in Thai At order (skips center 5): 1,2,3,4,6,7,8,9
const OUTER: [u8; 8] = [1, 2, 3, 4, 6, 7, 8, 9];

/// Map nhap_cuc 1..=72 → Thai At palace. Three years per palace; skip center → lodge Khon(2 in Luoshu / 7 in TAT layout).
/// Spec: Khon numbered 7 in TAT layout table; lodge rule says Khon (2 in Luoshu) — use TAT layout #7.
pub fn thai_at_palace(tn: &TichNien, duong_don: bool) -> ThaiAtPosition {
    // 0-based step within 72-year cycle; 3 years per outer palace → 24 steps per circuit × 3 = 72
    let step = ((tn.nhap_cuc as u16 - 1) / 3) % 8;
    let idx = if duong_don {
        step as usize
    } else {
        (8 - step as usize) % 8
    };
    let mut palace = OUTER[idx];
    if palace == 5 {
        palace = 7; // lodge Khon
    }
    ThaiAtPosition { palace, duong_don }
}
