//! Tam truyen (三傳) nine-method tree — TASK-LN-003 + COV-005 branch suite.
//! W3: deepen thiệp-hại depth count (bản gia walk) instead of first-candidate stub.

use crate::thiendiaban::{thien_over, TrangThaiBan};
use crate::tukhoa::{KhacTac, TuKhoa};
use cyberos_lichphap::{khac, ngu_hanh_of_chi, Can, Chi};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Phap {
    TacKhac,
    TyDung,
    ThiepHai,
    DaoKhac,
    MaoTinh,
    BietTrach,
    BatChuyen,
    PhucNgam,
    PhanNgam,
}

/// All nine decision branches (normative COV-005 set).
pub const NINE_PHAP: [Phap; 9] = [
    Phap::TacKhac,
    Phap::TyDung,
    Phap::ThiepHai,
    Phap::DaoKhac,
    Phap::MaoTinh,
    Phap::BietTrach,
    Phap::BatChuyen,
    Phap::PhucNgam,
    Phap::PhanNgam,
];

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum KhoaThe {
    TrongTham, // 重審
    NguyenThu, // 元首
    TriNhat,   // 知一
    ThiepHai,  // 涉害
    CaoThi,    // 蒿矢
    DanXa,     // 彈射
    PhucNgam,
    PhanNgam,
    Other,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct TamTruyen {
    pub so: Chi,
    pub trung: Chi,
    pub mat: Chi,
    pub phap: Phap,
    pub khoa_the: KhoaThe,
}

fn is_yang_can(c: Can) -> bool {
    matches!(c, Can::Giap | Can::Binh | Can::Mau | Can::Canh | Can::Nham)
}

fn chi_yang(z: Chi) -> bool {
    z.index().is_multiple_of(2) // Ty(0) yang classical; even indices yang in our enum
}

fn chain(thien: &[Chi; 12], so: Chi) -> (Chi, Chi) {
    let dia = crate::thiendiaban::dia_ban();
    let trung = thien_over(&dia, thien, so);
    let mat = thien_over(&dia, thien, trung);
    (trung, mat)
}

fn so_from_khoa(tk: &TuKhoa, idx: usize) -> Chi {
    tk.khoa[idx].thuong_than
}

fn make(so: Chi, thien: &[Chi; 12], phap: Phap, khoa_the: KhoaThe) -> TamTruyen {
    let (trung, mat) = chain(thien, so);
    TamTruyen {
        so,
        trung,
        mat,
        phap,
        khoa_the,
    }
}

/// Tứ mãnh (四孟): Dần Thân Tỵ Hợi — first tie-break in thiệp hại.
fn is_tu_manh(z: Chi) -> bool {
    matches!(z, Chi::Dan | Chi::Than | Chi::Ty2 | Chi::Hoi)
}

/// Tứ trọng (四仲): Tý Ngọ Mão Dậu — second tie-break.
fn is_tu_trong(z: Chi) -> bool {
    matches!(z, Chi::Ty | Chi::Ngo | Chi::Mao | Chi::Dau)
}

/// Depth of harm: walk from the earth palace under `thuong` toward `thuong`'s
/// own bản gia, counting palaces whose element is controlled (khắc) by `thuong`.
/// Classical thiệp hại (Claude-02 s4.2).
pub fn thiep_hai_depth(thuong: Chi, ha_under: Chi) -> u8 {
    let spirit = ngu_hanh_of_chi(thuong);
    let home = thuong.index();
    let mut cur = ha_under.index();
    let mut depth = 0u8;
    // Inclusive walk toward home along the 12-branch ring (forward).
    for _ in 0..12 {
        let earth = Chi::from_index(cur).unwrap();
        if khac(spirit, ngu_hanh_of_chi(earth)) {
            depth += 1;
        }
        if cur == home {
            break;
        }
        cur = (cur + 1) % 12;
    }
    depth
}

/// Select sơ truyền among multi-census candidates by thiệp hại depth + tie-break.
fn pick_thiep_hai(tk: &TuKhoa, census: &[(usize, KhacTac)]) -> Chi {
    let mut best: Option<(Chi, u8, u8)> = None; // (so, depth, priority)
    for &(i, _) in census {
        let so = so_from_khoa(tk, i);
        let ha = tk.khoa[i].ha_than;
        let depth = thiep_hai_depth(so, ha);
        let prio = if is_tu_manh(so) {
            2
        } else if is_tu_trong(so) {
            1
        } else {
            0
        };
        match best {
            None => best = Some((so, depth, prio)),
            Some((_, bd, bp)) if depth > bd || (depth == bd && prio > bp) => {
                best = Some((so, depth, prio));
            }
            _ => {}
        }
    }
    best.map(|(so, _, _)| so)
        .unwrap_or_else(|| so_from_khoa(tk, census[0].0))
}

/// Build tam truyen from tu khoa + board state.
///
/// Nine decision branches (COV-005):
/// 1. PhucNgam  2. PhanNgam  3. TacKhac (single khac/tac)
/// 4. TyDung    5. ThiepHai  6. BatChuyen (empty census, closed chain)
/// 7. DaoKhac   8. BietTrach 9. MaoTinh (fallbacks on empty census)
pub fn lap_tam_truyen(
    tk: &TuKhoa,
    thien: &[Chi; 12],
    state: TrangThaiBan,
    can_ngay: Can,
) -> TamTruyen {
    // 1–2. phuc / phan ngam first
    if state == TrangThaiBan::PhucNgam {
        let so = if is_yang_can(can_ngay) {
            tk.khoa[0].ha_than
        } else {
            tk.khoa[2].ha_than
        };
        return make(so, thien, Phap::PhucNgam, KhoaThe::PhucNgam);
    }
    if state == TrangThaiBan::PhanNgam {
        let so = tk.khoa[0].thuong_than;
        return make(so, thien, Phap::PhanNgam, KhoaThe::PhanNgam);
    }

    let census: Vec<(usize, KhacTac)> = tk
        .khoa
        .iter()
        .enumerate()
        .filter_map(|(i, k)| k.quan_he.map(|q| (i, q)))
        .collect();

    // 3. single khac/tac → TacKhac
    if census.len() == 1 {
        let (i, q) = census[0];
        let so = so_from_khoa(tk, i);
        let (phap, khoa_the) = match q {
            KhacTac::TacHaThuong => (Phap::TacKhac, KhoaThe::TrongTham),
            KhacTac::KhacThuongHa => (Phap::TacKhac, KhoaThe::NguyenThu),
        };
        return make(so, thien, phap, khoa_the);
    }

    // 4–5. multi → ty dung then thiep hai
    if census.len() >= 2 {
        let day_yang = is_yang_can(can_ngay);
        let ty: Vec<_> = census
            .iter()
            .copied()
            .filter(|(i, _)| chi_yang(so_from_khoa(tk, *i)) == day_yang)
            .collect();
        if ty.len() == 1 {
            let so = so_from_khoa(tk, ty[0].0);
            return make(so, thien, Phap::TyDung, KhoaThe::TriNhat);
        }
        // Thiệp hại: depth count toward bản gia (no longer first-candidate stub).
        let candidates = if ty.is_empty() { &census[..] } else { &ty[..] };
        let so = pick_thiep_hai(tk, candidates);
        return make(so, thien, Phap::ThiepHai, KhoaThe::ThiepHai);
    }

    // empty census — branches 6–9
    empty_census_branch(tk, thien, can_ngay)
}

fn empty_census_branch(tk: &TuKhoa, thien: &[Chi; 12], can_ngay: Can) -> TamTruyen {
    // Prefer Dau (酉) as so for MaoTinh when present as upper
    let dau_so = tk
        .khoa
        .iter()
        .map(|k| k.thuong_than)
        .find(|c| *c == Chi::Dau);

    // Probe candidate sos for closed 3-step chain (bat chuyen)
    for k in &tk.khoa {
        let so = k.thuong_than;
        let (trung, mat) = chain(thien, so);
        if mat == so {
            return TamTruyen {
                so,
                trung,
                mat,
                phap: Phap::BatChuyen,
                khoa_the: KhoaThe::Other,
            };
        }
    }

    // DaoKhac (遥克): day stem palace remote — use khoa 3 upper (day chi chain)
    // when day is yang, else khoa 1 upper
    let dao_so = if is_yang_can(can_ngay) {
        tk.khoa[2].thuong_than
    } else {
        tk.khoa[0].thuong_than
    };
    // BietTrach: when dao_so equals a lower (ha) of another khoa → "choice" branch
    let hits_ha = tk
        .khoa
        .iter()
        .any(|k| k.ha_than == dao_so && k.thuong_than != dao_so);
    if hits_ha {
        return make(dao_so, thien, Phap::BietTrach, KhoaThe::Other);
    }

    // If Dau present → MaoTinh (蒿矢/昴星 family)
    if let Some(so) = dau_so {
        return make(so, thien, Phap::MaoTinh, KhoaThe::CaoThi);
    }

    // Default DaoKhac remote start
    make(dao_so, thien, Phap::DaoKhac, KhoaThe::DanXa)
}
