//! Bat tuong placement — TASK-TAT-003.

use crate::anthaiat::{an_thai_at, ThaiAtSeat};
use crate::tichnien::TichNien;
use crate::toan::{compute_toan, dai_tuong_cung, tham_tuong_cung, DemToan, ToanResult, TruongDoan};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct BatTuong {
    pub van_xuong: u8,
    pub thuy_kich: u8,
    pub ke_than: u8,
    pub chu_dai_tuong: u8,
    pub khach_dai_tuong: u8,
    pub chu_tham_tuong: u8,
    pub khach_tham_tuong: u8,
    pub chu_toan: ToanResult,
    pub khach_toan: ToanResult,
    pub dem_toan: DemToan,
}

/// Van Xuong: reduce nhap_cuc by 18, count from ring 11 (Than/Vu duc) or 3 (Dan/Lu).
pub fn van_xuong(nhap_cuc: u8, duong_don: bool) -> u8 {
    let mut r = nhap_cuc as u16;
    while r >= 18 {
        r -= 18;
    }
    if r == 0 {
        r = 18;
    }
    let start: u16 = if duong_don { 11 } else { 3 };
    // simplified: step r without double-count for now
    ((start + r - 1) % 16) as u8
}

/// Ke than by year can_chi mod 12: start Dan(3) forward or Than(11) backward.
pub fn ke_than(year_chi_idx: u8, duong_don: bool) -> u8 {
    // map 12-chi year to ring positions that correspond to chi marks
    // chi indices on ring: 0子 1丑 3寅 4卯 5辰 7巳 8午 9未 11申 12酉 13戌 15亥
    const CHI_RINGS: [u8; 12] = [0, 1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15];
    let target = CHI_RINGS[(year_chi_idx % 12) as usize];
    if duong_don {
        target
    } else {
        // mirrored placement for am
        (16 - target % 16) % 16
    }
}

pub fn thuy_kich(ke: u8, duong_don: bool) -> u8 {
    // ke than gia 艮 (ring 2), then shift
    let base = (ke as u16 + 2) % 16;
    if duong_don {
        base as u8
    } else {
        ((base + 8) % 16) as u8
    }
}

pub fn place_bat_tuong(
    tn: &TichNien,
    year_chi_idx: u8,
    duong_don: bool,
    dem: DemToan,
) -> (BatTuong, ThaiAtSeat) {
    let seat = an_thai_at(tn, duong_don);
    let vx = van_xuong(tn.nhap_cuc, duong_don);
    let ke = ke_than(year_chi_idx, duong_don);
    let tk = thuy_kich(ke, duong_don);
    let chu = compute_toan(vx, &seat, dem);
    let khach = compute_toan(tk, &seat, dem);
    let chu_dai = dai_tuong_cung(chu.value);
    let khach_dai = dai_tuong_cung(khach.value);
    let bt = BatTuong {
        van_xuong: vx,
        thuy_kich: tk,
        ke_than: ke,
        chu_dai_tuong: chu_dai,
        khach_dai_tuong: khach_dai,
        chu_tham_tuong: tham_tuong_cung(chu_dai),
        khach_tham_tuong: tham_tuong_cung(khach_dai),
        chu_toan: chu,
        khach_toan: khach,
        dem_toan: dem,
    };
    let _ = TruongDoan::Truong;
    (bt, seat)
}
