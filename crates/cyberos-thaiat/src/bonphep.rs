//! Bốn phép — nien / nguyet / nhat / thoi ke — FR-TAT-004.
//! Reuses FR-TAT-001 reduction (map 1..=72) and epoch machinery.

use crate::ban::Cap;
use crate::flags::Epoch;
use crate::tichnien::{compute_tich_nien, TichNien};
use serde::{Deserialize, Serialize};

/// Map remainder into 1..=72 (0 → 72).
pub fn map_1_72(rem: u64) -> u8 {
    let r = (rem % 72) as u8;
    if r == 0 {
        72
    } else {
        r
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct TichCap {
    pub cap: Cap,
    pub tich: u64,
    pub cuc: u8,
    pub duong_don: bool,
}

/// Year plate — identical to FR-TAT-001 tich nien path.
pub fn tich_nien_ke(nam_ce: i32, epoch: Epoch) -> TichCap {
    let tn: TichNien = compute_tich_nien(nam_ce, epoch);
    TichCap {
        cap: Cap::Nien,
        tich: tn.tich_nien,
        cuc: tn.nhap_cuc,
        duong_don: true,
    }
}

/// Month plate: tich nguyet = tich nien × 12 + leap-month offset (0..1).
/// `leap_months_before` is the dedicated leap-month solve input (count of leap
/// months from epoch year through the target year-month, not a naive multiply).
pub fn tich_nguyet_ke(
    nam_ce: i32,
    month: u8,
    epoch: Epoch,
    leap_months_before: u32,
) -> TichCap {
    let tn = compute_tich_nien(nam_ce, epoch);
    let month_i = month.clamp(1, 12) as u64;
    let tich = tn.tich_nien.saturating_mul(12)
        + month_i.saturating_sub(1)
        + leap_months_before as u64;
    TichCap {
        cap: Cap::Nguyet,
        tich,
        cuc: map_1_72(tich),
        duong_don: true,
    }
}

/// Day plate: anchored on Dong Chi; tich nhat = days_from_anchor (scaled).
/// `days_from_dong_chi` is whole days since the shared solstice instant (CORE-001).
/// cuc = map_1_72(tich) then +1 style advance by day (mod 72 into 1..=72).
pub fn tich_nhat_ke(days_from_dong_chi: i64, duong_don: bool) -> TichCap {
    // Scale with tropical year factor as fractional days already folded into day count.
    let tich = if days_from_dong_chi < 0 {
        0u64
    } else {
        days_from_dong_chi as u64
    };
    let base = map_1_72(tich) as u16;
    let advanced = ((base as u64) % 72) + 1;
    let cuc = map_1_72(advanced);
    TichCap {
        cap: Cap::Nhat,
        tich,
        cuc,
        duong_don,
    }
}

/// Hour plate: tich thoi = tich nhat × 12; one hour = one cuc.
pub fn tich_thoi_ke(days_from_dong_chi: i64, hour_idx: u8, duong_don: bool) -> TichCap {
    let day = tich_nhat_ke(days_from_dong_chi, duong_don);
    let h = (hour_idx % 12) as u64;
    let tich = day.tich.saturating_mul(12) + h;
    let base = map_1_72(tich) as u16;
    let advanced = ((base as u64) % 72) + 1;
    TichCap {
        cap: Cap::Thoi,
        tich,
        cuc: map_1_72(advanced),
        duong_don,
    }
}

/// Dispatch by cap selector.
pub fn tich_theo_cap(
    cap: Cap,
    nam_ce: i32,
    month: u8,
    days_from_dong_chi: i64,
    hour_idx: u8,
    leap_months_before: u32,
    epoch: Epoch,
    duong_don: bool,
) -> TichCap {
    match cap {
        Cap::Nien => tich_nien_ke(nam_ce, epoch),
        Cap::Nguyet => tich_nguyet_ke(nam_ce, month, epoch, leap_months_before),
        Cap::Nhat => tich_nhat_ke(days_from_dong_chi, duong_don),
        Cap::Thoi => tich_thoi_ke(days_from_dong_chi, hour_idx, duong_don),
    }
}
