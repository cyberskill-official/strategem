//! Thai At — FR-TAT-001..003 + FR-TAT-006 assembly.

pub mod anthaiat;
pub mod ban;
pub mod battuong;
pub mod cuucung;
pub mod engine;
pub mod epoch;
pub mod flags;
pub mod thaplucthan;
pub mod tichnien;
pub mod toan;

pub use anthaiat::{an_thai_at, palace_to_ring, ThaiAtSeat};
pub use ban::{Cap, TatFlags, ThaiAtBan};
pub use battuong::{ke_than, place_bat_tuong, thuy_kich, van_xuong, BatTuong};
pub use cuucung::{thai_at_palace, ThaiAtPosition};
pub use engine::{cast_thai_at, CastInput, CastResult};
pub use flags::Epoch;
pub use thaplucthan::{is_chinh_cung, LoaiThan, Than, THAP_LUC_THAN};
pub use tichnien::{compute_tich_nien, TichNien};
pub use toan::{compute_toan, dai_tuong_cung, tham_tuong_cung, DemToan, ToanResult, TruongDoan};
