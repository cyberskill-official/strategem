//! Khoa the recognition — FR-LN-005 layer one (+ stubs for layer two).

use crate::tamtruyen::{KhoaThe, Phap, TamTruyen};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct KhoaTheHit {
    pub id: String,
    pub name: String,
    pub polarity: String,
    pub layer: u8,
}

/// Layer-one khoa the from FR-LN-003 method.
pub fn khoa_the_from_method(tt: &TamTruyen) -> KhoaTheHit {
    let (id, name, pol) = match tt.khoa_the {
        KhoaThe::NguyenThu => ("ln_nguyen_thu", "元首", "cat"),
        KhoaThe::TrongTham => ("ln_trong_tham", "重審", "trung"),
        KhoaThe::TriNhat => ("ln_tri_nhat", "知一", "trung"),
        KhoaThe::ThiepHai => ("ln_thiep_hai", "涉害", "hung"),
        KhoaThe::CaoThi => ("ln_cao_thi", "蒿矢", "trung"),
        KhoaThe::DanXa => ("ln_dan_xa", "彈射", "trung"),
        KhoaThe::PhucNgam => ("ln_phuc_ngam", "伏吟", "hung"),
        KhoaThe::PhanNgam => ("ln_phan_ngam", "返吟", "hung"),
        KhoaThe::Other => ("ln_other", "雜課", "trung"),
    };
    let _ = tt.phap;
    KhoaTheHit {
        id: id.into(),
        name: name.into(),
        polarity: pol.into(),
        layer: 1,
    }
}

/// Collect all khoa the (layer one + optional shape stubs).
pub fn recognize_khoa_the(tt: &TamTruyen) -> Vec<KhoaTheHit> {
    let mut hits = vec![khoa_the_from_method(tt)];
    // layer-two example stubs keyed off method family
    if matches!(tt.phap, Phap::PhucNgam | Phap::PhanNgam) {
        hits.push(KhoaTheHit {
            id: "ln_shape_ngung".into(),
            name: "凝滯".into(),
            polarity: "hung".into(),
            layer: 2,
        });
    }
    hits
}
