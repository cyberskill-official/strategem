//! Tam truyen (三傳) nine-method tree — FR-LN-003.

use crate::thiendiaban::{thien_over, TrangThaiBan};
use crate::tukhoa::{KhacTac, TuKhoa};
use cyberos_lichphap::{Can, Chi};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
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

/// Build tam truyen from tu khoa + board state.
pub fn lap_tam_truyen(
    tk: &TuKhoa,
    thien: &[Chi; 12],
    state: TrangThaiBan,
    can_ngay: Can,
) -> TamTruyen {
    // 0. phuc / phan ngam first
    if state == TrangThaiBan::PhucNgam {
        let so = if is_yang_can(can_ngay) {
            tk.khoa[0].ha_than
        } else {
            tk.khoa[2].ha_than
        };
        let (trung, mat) = chain(thien, so);
        return TamTruyen {
            so,
            trung,
            mat,
            phap: Phap::PhucNgam,
            khoa_the: KhoaThe::PhucNgam,
        };
    }
    if state == TrangThaiBan::PhanNgam {
        let so = tk.khoa[0].thuong_than;
        let (trung, mat) = chain(thien, so);
        return TamTruyen {
            so,
            trung,
            mat,
            phap: Phap::PhanNgam,
            khoa_the: KhoaThe::PhanNgam,
        };
    }

    let census: Vec<(usize, KhacTac)> = tk
        .khoa
        .iter()
        .enumerate()
        .filter_map(|(i, k)| k.quan_he.map(|q| (i, q)))
        .collect();

    // single khac/tac
    if census.len() == 1 {
        let (i, q) = census[0];
        let so = so_from_khoa(tk, i);
        let (trung, mat) = chain(thien, so);
        let (phap, khoa_the) = match q {
            KhacTac::TacHaThuong => (Phap::TacKhac, KhoaThe::TrongTham),
            KhacTac::KhacThuongHa => (Phap::TacKhac, KhoaThe::NguyenThu),
        };
        return TamTruyen {
            so,
            trung,
            mat,
            phap,
            khoa_the,
        };
    }

    // multi → ty dung then thiep hai
    if census.len() >= 2 {
        let day_yang = is_yang_can(can_ngay);
        let ty: Vec<_> = census
            .iter()
            .copied()
            .filter(|(i, _)| chi_yang(so_from_khoa(tk, *i)) == day_yang)
            .collect();
        if ty.len() == 1 {
            let so = so_from_khoa(tk, ty[0].0);
            let (trung, mat) = chain(thien, so);
            return TamTruyen {
                so,
                trung,
                mat,
                phap: Phap::TyDung,
                khoa_the: KhoaThe::TriNhat,
            };
        }
        // thiep hai: pick first candidate (full count deferred)
        let so = so_from_khoa(tk, census[0].0);
        let (trung, mat) = chain(thien, so);
        return TamTruyen {
            so,
            trung,
            mat,
            phap: Phap::ThiepHai,
            khoa_the: KhoaThe::ThiepHai,
        };
    }

    // empty census: mao tinh fallback — take Dau as so when present as thuong
    let so = tk
        .khoa
        .iter()
        .map(|k| k.thuong_than)
        .find(|c| *c == Chi::Dau)
        .unwrap_or(tk.khoa[0].thuong_than);
    let (trung, mat) = chain(thien, so);
    TamTruyen {
        so,
        trung,
        mat,
        phap: Phap::MaoTinh,
        khoa_the: KhoaThe::Other,
    }
}
