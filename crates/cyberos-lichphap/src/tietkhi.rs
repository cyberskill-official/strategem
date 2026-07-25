//! 24 solar terms (tiết khí). TASK-CORE-001 / W3.

use crate::delta_t::{tt_jd_to_utc_jd, utc_jd_to_tt_jd};
use crate::solar::{ang_diff, julian_day_utc, kinh_do_mat_troi};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TermKind {
    Jie,      // 节 (odd indices in 0..24 starting at Lichun=0)
    TrungKhi, // 中气
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TietKhi {
    pub index: u8, // 0..24, 0 = Lập xuân @ 315°
    pub kind: TermKind,
    pub target_longitude: f64,
}

/// Names VN (for diagnostics).
pub const NAMES: [&str; 24] = [
    "Lap xuan",
    "Vu thuy",
    "Kinh trap",
    "Xuan phan",
    "Thanh minh",
    "Coc vu",
    "Lap ha",
    "Tieu man",
    "Mang chung",
    "Ha chi",
    "Tieu thu",
    "Dai thu",
    "Lap thu",
    "Xu thu",
    "Bach lo",
    "Thu phan",
    "Han lo",
    "Suong giang",
    "Lap dong",
    "Tieu tuyet",
    "Dai tuyet",
    "Dong chi",
    "Tieu han",
    "Dai han",
];

/// Target apparent longitudes for terms starting at Lập xuân = 315°.
pub fn target_longitude(index: u8) -> f64 {
    ((315.0 + 15.0 * (index as f64)) % 360.0 + 360.0) % 360.0
}

pub fn term_def(index: u8) -> TietKhi {
    assert!(index < 24);
    let kind = if index.is_multiple_of(2) {
        TermKind::Jie
    } else {
        TermKind::TrungKhi
    };
    TietKhi {
        index,
        kind,
        target_longitude: target_longitude(index),
    }
}

/// Meeus AA ch.27 approximate JD (TT) for March equinox of `year` (Y).
fn meeus_march_equinox_tt(year: i32) -> f64 {
    let y = (year as f64 - 2000.0) / 1000.0;
    2_451_623.809_84 + 365_242.374_04 * y + 0.051_69 * y * y
        - 0.004_11 * y * y * y
        - 0.000_57 * y * y * y * y
}

/// Rough UTC JD guess for term `index` in solar year of `year` (Lap-Xuan origin).
fn rough_term_guess_utc(year: i32, index: u8) -> f64 {
    // Seed from March equinox (Xuân Phân = index 3 @ 0°), then step ~15.218 days.
    let march_tt = meeus_march_equinox_tt(year);
    let march_utc = tt_jd_to_utc_jd(march_tt);
    let offset_terms = index as i32 - 3;
    march_utc + (offset_terms as f64) * (365.242_19 / 24.0)
}

/// Newton inverse: find UTC JD when solar longitude equals `target` near `guess_jd_utc`.
pub fn solve_term_instant(target_lon: f64, guess_jd_utc: f64) -> f64 {
    let mut jd = guess_jd_utc;
    for _ in 0..24 {
        let lon = kinh_do_mat_troi(jd);
        let err = ang_diff(lon, target_lon); // lon - target
                                             // Numerical derivative for robustness near extrema.
        let h = 1e-4;
        let dlon = ang_diff(kinh_do_mat_troi(jd + h), lon) / h;
        let denom = if dlon.abs() < 1e-6 { 0.985_647_4 } else { dlon };
        let step = -err / denom;
        jd += step;
        if step.abs() < 1e-9 {
            break;
        }
    }
    jd
}

/// All 24 term instants (UTC JD) for a solar year containing `year`'s Lập xuân.
pub fn tiet_khi_year(year: i32) -> [f64; 24] {
    let mut out = [0.0; 24];
    for i in 0u8..24 {
        let target = target_longitude(i);
        let base = rough_term_guess_utc(year, i);
        // Fallback seed if Meeus polynomial is far (very early/late years).
        let fallback = julian_day_utc(year, 2, 4.0) + (i as f64) * (365.2422 / 24.0);
        let guess = if (base - fallback).abs() < 40.0 {
            base
        } else {
            fallback
        };
        out[i as usize] = solve_term_instant(target, guess);
    }
    out
}

/// In-force term for a UTC JD: the last term whose instant is ≤ jd.
pub fn tiet_khi_hien_hanh(jd_utc: f64) -> TietKhi {
    // Probe surrounding year
    let year = ((jd_utc - 1_721_059.5) / 365.25) as i32; // rough
    let mut best: Option<(f64, u8)> = None;
    for y in (year - 1)..=(year + 1) {
        for (i, &inst) in tiet_khi_year(y).iter().enumerate() {
            if inst <= jd_utc && best.map(|(t, _)| inst >= t).unwrap_or(true) {
                best = Some((inst, i as u8));
            }
        }
    }
    let idx = best.map(|(_, i)| i).unwrap_or(0);
    term_def(idx)
}

/// Published-style check helper: apply ΔT direction on a TT instant.
pub fn known_term_tt_to_utc(jd_tt: f64) -> f64 {
    tt_jd_to_utc_jd(jd_tt)
}

/// Inverse: UTC probe uses TT for solar theory.
pub fn probe_uses_tt(jd_utc: f64) -> f64 {
    utc_jd_to_tt_jd(jd_utc)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn twenty_four_kinds_alternate() {
        for i in 0u8..24 {
            let t = term_def(i);
            if i % 2 == 0 {
                assert_eq!(t.kind, TermKind::Jie);
            } else {
                assert_eq!(t.kind, TermKind::TrungKhi);
            }
            assert!((t.target_longitude - target_longitude(i)).abs() < 1e-9);
        }
    }

    #[test]
    fn dong_chi_near_december() {
        // Winter solstice index 21 @ 270°
        let inst = solve_term_instant(270.0, julian_day_utc(2020, 12, 21.0));
        // Roughly Dec 21 2020
        assert!(inst > julian_day_utc(2020, 12, 20.0) && inst < julian_day_utc(2020, 12, 23.0));
        let lon = kinh_do_mat_troi(inst);
        assert!(ang_diff(lon, 270.0).abs() < 0.01, "lon={lon}");
    }

    #[test]
    fn hien_hanh_before_after_term() {
        let inst = solve_term_instant(270.0, julian_day_utc(2020, 12, 21.0));
        let before = tiet_khi_hien_hanh(inst - 1.0 / 86400.0);
        let after = tiet_khi_hien_hanh(inst + 1.0 / 86400.0);
        // After should be dong chi (21) or later; before is previous
        assert_ne!(before.index, after.index);
        assert_eq!(after.index, 21);
    }
}
