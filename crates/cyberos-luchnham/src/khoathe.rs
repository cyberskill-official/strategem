//! Khoa the recognition — TASK-LN-005 layer one + deepened layer-two shapes (W3).

use crate::tamtruyen::{KhoaThe, Phap, TamTruyen};
use crate::thientuong::{ThienTuong, ThienTuongBan};
use crate::tukhoa::TuKhoa;
use cyberos_lichphap::Chi;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct KhoaTheHit {
    pub id: String,
    pub name: String,
    pub polarity: String,
    pub layer: u8,
}

/// Layer-one khoa the from TASK-LN-003 method.
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
        KhoaThe::Other => match tt.phap {
            Phap::BatChuyen => ("ln_bat_chuyen", "八專", "trung"),
            Phap::BietTrach => ("ln_biet_trach", "別責", "trung"),
            Phap::DaoKhac => ("ln_dao_khac", "遙剋", "trung"),
            Phap::MaoTinh => ("ln_mao_tinh", "昴星", "trung"),
            _ => ("ln_other", "雜課", "trung"),
        },
    };
    let _ = tt.phap;
    KhoaTheHit {
        id: id.into(),
        name: name.into(),
        polarity: pol.into(),
        layer: 1,
    }
}

fn general_on(ban: &ThienTuongBan, chi: Chi) -> ThienTuong {
    ban.generals[chi.index() as usize]
}

fn is_cat(g: ThienTuong) -> bool {
    g.polarity() == "cat"
}

/// Collect all khoa the (layer one + layer-two shape predicates).
///
/// Layer-two predicates use tam truyen + generals when provided. Full 64-body
/// classical catalog: drop kinliuren dump under `oracle/kinliuren/full/` (W4).
pub fn recognize_khoa_the(tt: &TamTruyen) -> Vec<KhoaTheHit> {
    recognize_khoa_the_full(tt, None, None)
}

/// Extended recognition with board context for L2 shapes.
pub fn recognize_khoa_the_full(
    tt: &TamTruyen,
    _tk: Option<&TuKhoa>,
    generals: Option<&ThienTuongBan>,
) -> Vec<KhoaTheHit> {
    let mut hits = vec![khoa_the_from_method(tt)];

    // L2: phục / phản ngâm → ngưng trệ shape
    if matches!(tt.phap, Phap::PhucNgam | Phap::PhanNgam) {
        hits.push(KhoaTheHit {
            id: "ln_shape_ngung".into(),
            name: "凝滯".into(),
            polarity: "hung".into(),
            layer: 2,
        });
    }

    // L2: thiệp hại method → explicit 涉害課 shape stamp
    if matches!(tt.phap, Phap::ThiepHai) {
        hits.push(KhoaTheHit {
            id: "ln_shape_thiep_hai".into(),
            name: "涉害課".into(),
            polarity: "hung".into(),
            layer: 2,
        });
    }

    // L2: tam dương — all three truyen on tứ mãnh / advancing yang branches
    let yangish = |z: Chi| {
        matches!(
            z,
            Chi::Dan | Chi::Mao | Chi::Thin | Chi::Ty2 | Chi::Ngo | Chi::Mui
        )
    };
    if yangish(tt.so) && yangish(tt.trung) && yangish(tt.mat) {
        hits.push(KhoaTheHit {
            id: "ln_tam_duong".into(),
            name: "三陽".into(),
            polarity: "cat".into(),
            layer: 2,
        });
    }

    // L2: tam quang — three truyen ride cat generals (when generals available)
    if let Some(ban) = generals {
        let g_so = general_on(ban, tt.so);
        let g_trung = general_on(ban, tt.trung);
        let g_mat = general_on(ban, tt.mat);
        if is_cat(g_so) && is_cat(g_trung) && is_cat(g_mat) {
            hits.push(KhoaTheHit {
                id: "ln_tam_quang".into(),
                name: "三光".into(),
                polarity: "cat".into(),
                layer: 2,
            });
        }
        // Long đức: Thanh Long rides sơ truyền
        if g_so == ThienTuong::ThanhLong {
            hits.push(KhoaTheHit {
                id: "ln_long_duc".into(),
                name: "龍德".into(),
                polarity: "cat".into(),
                layer: 2,
            });
        }
    }

    hits
}
