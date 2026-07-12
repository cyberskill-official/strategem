//! Thai At ban types — FR-TAT-006.

use crate::anthaiat::ThaiAtSeat;
use crate::battuong::BatTuong;
use crate::flags::Epoch;
use crate::tichnien::TichNien;
use crate::toan::DemToan;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum Cap {
    #[default]
    Nien,
    Nguyet,
    Nhat,
    Thoi,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct TatFlags {
    pub epoch: Epoch,
    pub dem_toan: DemToan,
    pub cap: Cap,
    pub duong_don: bool,
}

impl Default for TatFlags {
    fn default() -> Self {
        Self {
            epoch: Epoch::KimKinh,
            dem_toan: DemToan::TruocThaiAt,
            cap: Cap::Nien,
            duong_don: true,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThaiAtBan {
    pub tich: TichNien,
    pub seat: ThaiAtSeat,
    pub bat_tuong: BatTuong,
}
