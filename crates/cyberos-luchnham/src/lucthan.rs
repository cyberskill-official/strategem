//! Luc than + dung than — TASK-LN-005.

use cyberos_lichphap::{khac, ngu_hanh_of_can, ngu_hanh_of_chi, sinh, Can, Chi, NguHanh};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LucThan {
    PhuMau,  // generates day stem
    TuTon,   // day stem generates
    QuanQuy, // controls day stem
    TheTai,  // day stem controls
    HuynhDe, // same element
}

impl LucThan {
    pub fn glyph(self) -> &'static str {
        match self {
            LucThan::PhuMau => "父母",
            LucThan::TuTon => "子孫",
            LucThan::QuanQuy => "官鬼",
            LucThan::TheTai => "妻財",
            LucThan::HuynhDe => "兄弟",
        }
    }
}

pub fn luc_than_of(chi: Chi, can_ngay: Can) -> LucThan {
    let day = ngu_hanh_of_can(can_ngay);
    let el = ngu_hanh_of_chi(chi);
    if el == day {
        LucThan::HuynhDe
    } else if sinh(el, day) {
        LucThan::PhuMau
    } else if sinh(day, el) {
        LucThan::TuTon
    } else if khac(el, day) {
        LucThan::QuanQuy
    } else if khac(day, el) {
        LucThan::TheTai
    } else {
        LucThan::HuynhDe
    }
}

/// Map question type -> luc than for dung than.
pub fn dung_than_kind(loai_cau_hoi: &str) -> LucThan {
    match loai_cau_hoi {
        "tai_loc" | "tai_van" | "trach_thoi" => LucThan::TheTai,
        "cong_danh" | "su_nghiep" => LucThan::QuanQuy,
        "con_cai" | "hoc_van" => LucThan::TuTon,
        "cha_me" | "nha_cua" | "hon_nhan" => LucThan::PhuMau,
        _ => LucThan::HuynhDe,
    }
}

/// Find a chi among candidates that carries the requested luc than.
pub fn pick_dung_than(can_ngay: Can, candidates: &[Chi], loai: &str) -> Option<Chi> {
    let want = dung_than_kind(loai);
    candidates
        .iter()
        .copied()
        .find(|c| luc_than_of(*c, can_ngay) == want)
}

/// Silence unused NguHanh import if optimized away.
pub fn _phase_eq(a: NguHanh, b: NguHanh) -> bool {
    a == b
}
