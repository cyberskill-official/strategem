//! Four victory *criteria* as deterministic facts — FR-TAT-005.
//! No "who wins" verdict field; AI layer owns the reading.

use crate::battuong::BatTuong;
use crate::cachcuc::CachCucTat;
use crate::toan::TruongDoan;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TamTai {
    Du,
    Khuyet,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HoaEdge {
    Chu,
    Khach,
    Hoa,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BonTieuChi {
    pub hoa: HoaEdge,
    pub chu_truong_doan: TruongDoan,
    pub khach_truong_doan: TruongDoan,
    pub tam_tai: TamTai,
    pub cach_cuc: Vec<CachCucTat>,
    // deliberately NO winner / verdict field
}

/// Tam tai du if thien/dia/nhan presence flags all true.
pub fn tinh_tam_tai(thien: bool, dia: bool, nhan: bool) -> TamTai {
    if thien && dia && nhan {
        TamTai::Du
    } else {
        TamTai::Khuyet
    }
}

pub fn luan_bon_tieu_chi(
    bat: &BatTuong,
    cach_cuc: Vec<CachCucTat>,
    thien: bool,
    dia: bool,
    nhan: bool,
) -> BonTieuChi {
    let hoa = match bat.chu_toan.value.cmp(&bat.khach_toan.value) {
        std::cmp::Ordering::Greater => HoaEdge::Chu,
        std::cmp::Ordering::Less => HoaEdge::Khach,
        std::cmp::Ordering::Equal => HoaEdge::Hoa,
    };
    BonTieuChi {
        hoa,
        chu_truong_doan: bat.chu_toan.label,
        khach_truong_doan: bat.khach_toan.label,
        tam_tai: tinh_tam_tai(thien, dia, nhan),
        cach_cuc,
    }
}
