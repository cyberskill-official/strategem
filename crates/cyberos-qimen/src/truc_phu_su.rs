//! Truc phu / truc su + thien ban rotation — FR-QMDG-003.

use crate::dia_ban::{DiaBan, Stem};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum PanMethod {
    #[default]
    Zhuan,
    Fei,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum ZhongGongKy {
    #[default]
    Khon2,
    GiuNguyen,
}

/// Placeholder star/door indices 0..8 until FR-QMDG-004 formalizes names.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct TrucPhuSu {
    pub truc_phu: u8,
    pub truc_su: u8,
    /// Jia-decade head as (can_index 0..10, chi_index 0..12); always Giap + one of 6 chi.
    pub tuan_thu_chi: u8,
    pub nghi_an: Stem,
    pub cung_tuan_thu: u8,
    pub cung_gio: u8,
    pub thien_ban: [Stem; 9],
    pub xoay: i8,
    pub pan_method: PanMethod,
    pub zhong_gong_ky: ZhongGongKy,
}

/// Six tuan: Giap + {Ty, Tuat, Than, Ngo, Thin, Dan} → hidden nghi.
pub fn tuan_thu_from_hour(can_idx: u8, chi_idx: u8) -> (u8, Stem) {
    // Distance from Giap-Ty cycle: day/hour in 60 JiaZi; for hour, (can, chi) share parity.
    // Find which of the 6 tuan heads is the start of the decade containing this stem-branch.
    // Standard: tuan head chi = chi - can (mod 12) when can is offset from Giap...
    // For hour ganzhi, tuan head is the Giap day/hour where chi = (chi - can) mod 12.
    let head_chi = (chi_idx as i16 - can_idx as i16).rem_euclid(12) as u8;
    let nghi = match head_chi {
        0 => Stem::Mau,  // 甲子
        10 => Stem::Ky,  // 甲戌
        8 => Stem::Canh, // 甲申
        6 => Stem::Tan,  // 甲午
        4 => Stem::Nham, // 甲辰
        2 => Stem::Quy,  // 甲寅
        _ => Stem::Mau,  // fallback
    };
    (head_chi, nghi)
}

pub fn palace_of_stem(dia: &DiaBan, stem: Stem) -> u8 {
    for p in 1u8..=9 {
        if dia.at_palace(p) == stem {
            return p;
        }
    }
    1
}

/// Resting star/door rings: palace p has star (p-1) and door (p-1) until QMDG-004.
fn resting_star(palace: u8) -> u8 {
    palace.saturating_sub(1) % 9
}
fn resting_door(palace: u8) -> u8 {
    palace.saturating_sub(1) % 9
}

fn lodge_center(p: u8, z: ZhongGongKy) -> u8 {
    if p == 5 {
        match z {
            ZhongGongKy::Khon2 => 2,
            ZhongGongKy::GiuNguyen => 5,
        }
    } else {
        p
    }
}

/// Rigid-wheel rotate: earth plate stems move so stem at from_p lands on to_p.
pub fn rotate_zhuan(dia: &DiaBan, from_p: u8, to_p: u8) -> ([Stem; 9], i8) {
    let xoay = (to_p as i16 - from_p as i16).rem_euclid(9) as i8;
    let mut out = [Stem::Mau; 9];
    for p in 1u8..=9 {
        // stem that was at (p - xoay) moves to p
        let src = ((p as i16 - 1 - xoay as i16).rem_euclid(9) + 1) as u8;
        out[(p - 1) as usize] = dia.at_palace(src);
    }
    (out, xoay)
}

/// Fei (simplified): each palace stem flies by its own Luoshu step from from_p toward to_p offset.
pub fn rotate_fei(dia: &DiaBan, from_p: u8, to_p: u8) -> ([Stem; 9], i8) {
    let base = (to_p as i16 - from_p as i16).rem_euclid(9) as i8;
    let mut out = [Stem::Mau; 9];
    for p in 1u8..=9 {
        // fly by palace number steps (variant form)
        let steps = ((base as i16 + p as i16) % 9) as i8;
        let src = ((p as i16 - 1 - steps as i16).rem_euclid(9) + 1) as u8;
        out[(p - 1) as usize] = dia.at_palace(src);
    }
    (out, base)
}

pub fn truc_phu_truc_su(
    dia: &DiaBan,
    hour_can: u8,
    hour_chi: u8,
    hour_stem_palace: u8,
    pan: PanMethod,
    zhong: ZhongGongKy,
) -> TrucPhuSu {
    let (tuan_chi, nghi) = tuan_thu_from_hour(hour_can, hour_chi);
    let mut cung_tt = palace_of_stem(dia, nghi);
    cung_tt = lodge_center(cung_tt, zhong);
    let mut cung_gio = hour_stem_palace;
    cung_gio = lodge_center(cung_gio, zhong);
    let (thien, xoay) = match pan {
        PanMethod::Zhuan => rotate_zhuan(dia, cung_tt, cung_gio),
        PanMethod::Fei => rotate_fei(dia, cung_tt, cung_gio),
    };
    TrucPhuSu {
        truc_phu: resting_star(cung_tt),
        truc_su: resting_door(cung_tt),
        tuan_thu_chi: tuan_chi,
        nghi_an: nghi,
        cung_tuan_thu: cung_tt,
        cung_gio,
        thien_ban: thien,
        xoay,
        pan_method: pan,
        zhong_gong_ky: zhong,
    }
}
