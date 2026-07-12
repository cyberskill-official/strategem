//! Muoi hai thien tuong — FR-LN-004.

use cyberos_lichphap::{Can, Chi};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ThienTuong {
    QuyNhan,
    DangXa,
    ChuTuoc,
    LucHop,
    CauTran,
    ThanhLong,
    ThienKhong,
    BachHo,
    ThaiThuong,
    HuyenVu,
    ThaiAm,
    ThienHau,
}

impl ThienTuong {
    pub const SEQ: [ThienTuong; 12] = [
        ThienTuong::QuyNhan,
        ThienTuong::DangXa,
        ThienTuong::ChuTuoc,
        ThienTuong::LucHop,
        ThienTuong::CauTran,
        ThienTuong::ThanhLong,
        ThienTuong::ThienKhong,
        ThienTuong::BachHo,
        ThienTuong::ThaiThuong,
        ThienTuong::HuyenVu,
        ThienTuong::ThaiAm,
        ThienTuong::ThienHau,
    ];

    pub fn polarity(self) -> &'static str {
        match self {
            ThienTuong::QuyNhan
            | ThienTuong::LucHop
            | ThienTuong::ThanhLong
            | ThienTuong::ThienHau
            | ThienTuong::ThaiAm
            | ThienTuong::ThaiThuong => "cat",
            ThienTuong::ThienKhong => "trung",
            _ => "hung",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum KhoiQuyNhan {
    #[default]
    TruQuy,
    DaQuy,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum QuyNhanVariant {
    #[default]
    GiapMauCanh,
    TachGiap,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThienTuongBan {
    /// general at each dia ban palace index 0..12
    pub generals: [ThienTuong; 12],
    pub khoi: KhoiQuyNhan,
    pub thuan_bo: bool,
    pub quy_nhan_palace: Chi,
}

/// Day/night: Mao(3)..Than(8) inclusive = day (tru quy).
pub fn khoi_from_gio(gio: Chi) -> KhoiQuyNhan {
    let i = gio.index();
    if (3..=8).contains(&i) {
        KhoiQuyNhan::TruQuy
    } else {
        KhoiQuyNhan::DaQuy
    }
}

pub fn quy_nhan_palace(can: Can, khoi: KhoiQuyNhan, variant: QuyNhanVariant) -> Chi {
    if variant == QuyNhanVariant::TachGiap && can == Can::Giap {
        return Chi::Mui; // di ban Giap duong
    }
    let (tru, da) = match can {
        Can::Giap | Can::Mau | Can::Canh => (Chi::Suu, Chi::Mui),
        Can::At | Can::Ky => (Chi::Ty, Chi::Than),
        Can::Binh | Can::Dinh => (Chi::Hoi, Chi::Dau),
        Can::Nham | Can::Quy => (Chi::Mao, Chi::Ty2),
        Can::Tan => (Chi::Ngo, Chi::Dan),
    };
    match khoi {
        KhoiQuyNhan::TruQuy => tru,
        KhoiQuyNhan::DaQuy => da,
    }
}

/// Thuan bo when Quy Nhan in Hoi Ty Suu Dan Mao Thin (indices 11,0,1,2,3,4).
pub fn is_thuan_bo(palace: Chi) -> bool {
    matches!(
        palace,
        Chi::Hoi | Chi::Ty | Chi::Suu | Chi::Dan | Chi::Mao | Chi::Thin
    )
}

pub fn lap_thien_tuong(can_ngay: Can, gio_chiem: Chi, variant: QuyNhanVariant) -> ThienTuongBan {
    let khoi = khoi_from_gio(gio_chiem);
    let start = quy_nhan_palace(can_ngay, khoi, variant);
    let thuan = is_thuan_bo(start);
    let mut generals = [ThienTuong::QuyNhan; 12];
    for (k, gen) in ThienTuong::SEQ.iter().enumerate() {
        let offset = if thuan {
            k as u8
        } else {
            (12 - (k as u8 % 12)) % 12
        };
        // when nghich and k=0, offset 0; for k=1 offset 11, etc.
        let off = if thuan {
            k as u8
        } else if k == 0 {
            0
        } else {
            (12 - (k as u8)) % 12
        };
        let palace = Chi::from_index((start.index() + off) % 12).unwrap();
        let _ = offset;
        generals[palace.index() as usize] = *gen;
    }
    ThienTuongBan {
        generals,
        khoi,
        thuan_bo: thuan,
        quy_nhan_palace: start,
    }
}
