//! Dinh cuc table 24 jieqi × 3 nguyen. TASK-QMDG-001 / W3 classical table.
//!
//! Table source: Claude-03 s3.2 / TASK-QMDG-001 §3 (verbatim). This is the
//! classical 24×3 so_cuc grid — not a kinqimen dump (external oracle is W4).
//! Method-specific sieu-than / tiep-khi boundary drift remains school-flagged;
//! full kinqimen boundary certification: drop dump under `oracle/kinqimen/full/` (W4).

use crate::flags::DingjuMethod;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct DinhCuc {
    pub so_cuc: u8,      // 1..=9
    pub duong_don: bool, // true = yang dun
    pub nguyen: u8,      // 1=thuong,2=trung,3=ha
    pub method: DingjuMethod,
}

/// Classical 24×3 so_cuc table indexed by (term_index 0..24, nguyen 0..3).
/// `term_index` 0 = Lập Xuân (315°); see `cyberos_lichphap::tietkhi::NAMES`.
///
/// Rows are `[thượng, trung, hạ]` per Claude-03 s3.2.
const SO_CUC_24X3: [[u8; 3]; 24] = [
    // Dương độn half (Đông Chí → Mang Chủng), then Âm độn (Hạ Chí → Đại Tuyết),
    // ordered by Lap-Xuan-origin index:
    [8, 5, 2], // 0  Lập Xuân
    [9, 6, 3], // 1  Vũ Thủy
    [1, 7, 4], // 2  Kinh Trập
    [3, 9, 6], // 3  Xuân Phân
    [4, 1, 7], // 4  Thanh Minh
    [5, 2, 8], // 5  Cốc Vũ
    [4, 1, 7], // 6  Lập Hạ
    [5, 2, 8], // 7  Tiểu Mãn
    [6, 3, 9], // 8  Mang Chủng
    [9, 3, 6], // 9  Hạ Chí (âm)
    [8, 2, 5], // 10 Tiểu Thử
    [7, 1, 4], // 11 Đại Thử
    [2, 5, 8], // 12 Lập Thu
    [1, 4, 7], // 13 Xử Thử
    [9, 3, 6], // 14 Bạch Lộ
    [7, 1, 4], // 15 Thu Phân
    [6, 9, 3], // 16 Hàn Lộ
    [5, 8, 2], // 17 Sương Giáng
    [6, 9, 3], // 18 Lập Đông
    [5, 8, 2], // 19 Tiểu Tuyết
    [4, 7, 1], // 20 Đại Tuyết
    [1, 7, 4], // 21 Đông Chí (dương)
    [2, 8, 5], // 22 Tiểu Hàn
    [3, 9, 6], // 23 Đại Hàn
];

/// Canonical 24×3 table: so_cuc for (term_index 0..24, nguyen 0..3).
pub fn table_so_cuc(term_index: u8, nguyen: u8) -> u8 {
    assert!(term_index < 24 && nguyen < 3);
    SO_CUC_24X3[term_index as usize][nguyen as usize]
}

/// Dương độn from Đông Chí through Mang Chủng; âm độn from Hạ Chí through Đại Tuyết.
/// Term index is Lap-Xuan-origin (0 = Lập Xuân).
pub fn table_duong_don(term_index: u8) -> bool {
    assert!(term_index < 24);
    // Dương: Đông Chí(21), Tiểu Hàn(22), Đại Hàn(23), Lập Xuân..Mang Chủng (0..=8)
    // Âm: Hạ Chí..Đại Tuyết (9..=20)
    matches!(term_index, 0..=8 | 21..=23)
}

/// Branch → nguyen (phù đầu style), Claude-03 s3.3:
/// Tý/Ngọ/Mão/Dậu → thượng; Dần/Thân/Tỵ/Hợi → trung; Thìn/Tuất/Sửu/Mùi → hạ.
pub fn phu_dau_nguyen(branch_index: u8) -> u8 {
    match branch_index % 12 {
        0 | 3 | 6 | 9 => 1,  // Tý Mão Ngọ Dậu — thượng
        2 | 5 | 8 | 11 => 2, // Dần Tỵ Thân Hợi — trung
        _ => 3,              // Sửu Thìn Mùi Tuất — hạ
    }
}

pub fn dinh_cuc(
    term_index: u8,
    branch_index: u8,
    method: DingjuMethod,
    tri_nhuan: bool,
) -> Result<DinhCuc, String> {
    if term_index >= 24 {
        return Err("term_index out of range".into());
    }
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
    // Method-specific sieu-than / tiep-khi / tri-nhuan adjust.
    // Full kinqimen boundary divergence set: oracle/kinqimen/full/ (W4 harness).
    match method {
        DingjuMethod::Chaibu => {}
        DingjuMethod::Zhirun if tri_nhuan => {
            nguyen = (nguyen % 3) + 1;
        }
        DingjuMethod::Maoshan => {
            // Mao-shan: shift nguyen at the same structural step used historically
            // for boundary absorption (kinqimen divergence table: oracle/kinqimen/full/).
            nguyen = (nguyen % 3) + 1;
        }
        _ => {}
    }
    let nguyen0 = nguyen - 1;
    Ok(DinhCuc {
        so_cuc: table_so_cuc(term_index, nguyen0),
        duong_don: table_duong_don(term_index),
        nguyen,
        method,
    })
}

/// Luoshu outer palace numbers for structural invariant test (Claude-03 s3.2).
/// Order: Đông Chí Khảm, Lập Xuân Cấn, Xuân Phân Chấn, Lập Hạ Tốn,
/// Hạ Chí Ly, Lập Thu Khôn, Thu Phân Đoài, Lập Đông Càn.
pub fn luoshu_outer() -> [u8; 8] {
    [1, 8, 3, 4, 9, 2, 7, 6]
}

/// First term governed by each outer palace (Lap-Xuan-origin indices).
pub fn luoshu_governed_terms() -> [u8; 8] {
    [21, 0, 3, 6, 9, 12, 15, 18]
}
