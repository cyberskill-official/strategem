//! Tich nien + three reductions — FR-TAT-001.

use crate::epoch::tich_nien_raw;
use crate::flags::Epoch;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct TichNien {
    pub tich_nien: u64,
    pub nhap_ky_nguyen: u32, // mod 360
    pub nhap_cuc: u8,        // 1..=72
    pub can_chi: u8,         // mod 60
    pub epoch: Epoch,
}

pub fn compute_tich_nien(nam_ce: i32, epoch: Epoch) -> TichNien {
    let tn = tich_nien_raw(nam_ce, epoch);
    let r72 = (tn % 72) as u8;
    let nhap_cuc = if r72 == 0 { 72 } else { r72 };
    TichNien {
        tich_nien: tn,
        nhap_ky_nguyen: (tn % 360) as u32,
        nhap_cuc,
        can_chi: (tn % 60) as u8,
        epoch,
    }
}
