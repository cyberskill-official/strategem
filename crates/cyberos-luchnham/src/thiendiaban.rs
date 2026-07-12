//! Thien / dia ban rotation. FR-LN-001.

use cyberos_lichphap::Chi;
use serde::{Deserialize, Serialize};

/// Fixed earth plate: chi on 12 positions 0..12 starting at 子.
pub fn dia_ban() -> [Chi; 12] {
    Chi::ALL
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TrangThaiBan {
    Thuong,
    PhucNgam,
    PhanNgam,
}

/// Rotate dia ban by offset so thien[i] = dia[(i+offset) mod 12] with offset = (nt - gio) mod 12.
pub fn quay_thien_ban(nguyet_tuong: Chi, gio_chiem: Chi) -> ([Chi; 12], TrangThaiBan) {
    let offset = (nguyet_tuong.index() as i32 - gio_chiem.index() as i32).rem_euclid(12) as u8;
    let dia = dia_ban();
    let mut thien = [Chi::Ty; 12];
    for i in 0..12 {
        thien[i] = dia[((i as u8 + offset) % 12) as usize];
    }
    let state = if offset == 0 {
        TrangThaiBan::PhucNgam
    } else if offset == 6 {
        TrangThaiBan::PhanNgam
    } else {
        TrangThaiBan::Thuong
    };
    (thien, state)
}

/// Map: for earth position holding `earth_chi`, which heaven chi sits above.
pub fn thien_over(dia: &[Chi; 12], thien: &[Chi; 12], earth_chi: Chi) -> Chi {
    let i = dia.iter().position(|c| *c == earth_chi).unwrap();
    thien[i]
}
