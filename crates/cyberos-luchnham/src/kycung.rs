//! Thien can ky cung. FR-LN-001.

use cyberos_lichphap::{Can, Chi};

/// Palace branch for each stem. Never Ty/Ngo/Mao/Dau (cardinal voids for ky cung).
pub fn ky_cung(can: Can) -> Chi {
    match can {
        Can::Giap => Chi::Dan,
        Can::At => Chi::Thin,
        Can::Binh => Chi::Ty2,
        Can::Dinh => Chi::Mui,
        Can::Mau => Chi::Ty2,
        Can::Ky => Chi::Mui,
        Can::Canh => Chi::Than,
        Can::Tan => Chi::Tuat,
        Can::Nham => Chi::Hoi,
        Can::Quy => Chi::Suu,
    }
}
