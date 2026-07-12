//! Thai At — FR-TAT-001..004 + FR-TAT-006 assembly.

pub mod anthaiat;
pub mod ban;
pub mod battuong;
pub mod bonphep;
pub mod cachcuc;
pub mod cuucung;
pub mod engine;
pub mod epoch;
pub mod flags;
pub mod thangbai;
pub mod thaplucthan;
pub mod tichnien;
pub mod toan;

pub use anthaiat::{an_thai_at, palace_to_ring, ThaiAtSeat};
pub use ban::{Cap, TatFlags, ThaiAtBan};
pub use battuong::{ke_than, place_bat_tuong, thuy_kich, van_xuong, BatTuong};
pub use bonphep::{
    map_1_72, tich_nguyet_ke, tich_nhat_ke, tich_nien_ke, tich_theo_cap, tich_thoi_ke, TichCap,
    TichCapInput,
};
pub use cachcuc::{map_to_envelope_cach_cuc, nhan_dien_cach_cuc, BienTheKich, Cach, CachCucTat};
pub use cuucung::{thai_at_palace, ThaiAtPosition};
pub use engine::{cast_thai_at, CastInput, CastResult};
pub use flags::Epoch;
pub use thangbai::{luan_bon_tieu_chi, tinh_tam_tai, BonTieuChi, HoaEdge, TamTai};
pub use thaplucthan::{is_chinh_cung, LoaiThan, Than, THAP_LUC_THAN};
pub use tichnien::{compute_tich_nien, TichNien};
pub use toan::{compute_toan, dai_tuong_cung, tham_tuong_cung, DemToan, ToanResult, TruongDoan};
