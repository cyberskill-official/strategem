//! Tu khoa (四課) — FR-LN-002.

use crate::kycung::ky_cung;
use crate::thiendiaban::{dia_ban, thien_over};
use cyberos_lichphap::{khac, ngu_hanh_of_can, ngu_hanh_of_chi, Can, Chi, NguHanh};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum KhacTac {
    /// 克 — upper controls lower
    KhacThuongHa,
    /// 賊 — lower controls upper
    TacHaThuong,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Khoa {
    pub thuong_than: Chi,
    pub ha_than: Chi,
    /// true only for khoa 1: ha than stands for the day stem
    pub la_can_khoa: bool,
    pub quan_he: Option<KhacTac>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct TuKhoa {
    /// index 0 = khoa 1 (rightmost) … index 3 = khoa 4
    pub khoa: [Khoa; 4],
}

pub fn quan_he_khoa(thuong: NguHanh, ha: NguHanh) -> Option<KhacTac> {
    if khac(thuong, ha) {
        Some(KhacTac::KhacThuongHa)
    } else if khac(ha, thuong) {
        Some(KhacTac::TacHaThuong)
    } else {
        None
    }
}

/// Build four lessons from rotated thien ban + day stem/chi.
pub fn lap_tu_khoa(thien: &[Chi; 12], can_ngay: Can, chi_ngay: Chi) -> TuKhoa {
    let dia = dia_ban();

    // Khoa 1: ha = day stem ky cung palace; thuong = thien over that palace
    let ky = ky_cung(can_ngay);
    let t1 = thien_over(&dia, thien, ky);
    let ha1_elem = ngu_hanh_of_can(can_ngay);
    let q1 = quan_he_khoa(ngu_hanh_of_chi(t1), ha1_elem);

    // Khoa 2: ha = khoa1 thuong; thuong = thien over that chi's palace
    let t2 = thien_over(&dia, thien, t1);
    let q2 = quan_he_khoa(ngu_hanh_of_chi(t2), ngu_hanh_of_chi(t1));

    // Khoa 3: ha = day chi; thuong over day chi
    let t3 = thien_over(&dia, thien, chi_ngay);
    let q3 = quan_he_khoa(ngu_hanh_of_chi(t3), ngu_hanh_of_chi(chi_ngay));

    // Khoa 4: ha = khoa3 thuong
    let t4 = thien_over(&dia, thien, t3);
    let q4 = quan_he_khoa(ngu_hanh_of_chi(t4), ngu_hanh_of_chi(t3));

    TuKhoa {
        khoa: [
            Khoa {
                thuong_than: t1,
                ha_than: ky,
                la_can_khoa: true,
                quan_he: q1,
            },
            Khoa {
                thuong_than: t2,
                ha_than: t1,
                la_can_khoa: false,
                quan_he: q2,
            },
            Khoa {
                thuong_than: t3,
                ha_than: chi_ngay,
                la_can_khoa: false,
                quan_he: q3,
            },
            Khoa {
                thuong_than: t4,
                ha_than: t3,
                la_can_khoa: false,
                quan_he: q4,
            },
        ],
    }
}

pub fn census_khac_tac(tk: &TuKhoa) -> Vec<(usize, KhacTac)> {
    tk.khoa
        .iter()
        .enumerate()
        .filter_map(|(i, k)| k.quan_he.map(|q| (i, q)))
        .collect()
}
