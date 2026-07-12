//! KyMon ban types — FR-QMDG-006.

use crate::dia_ban::{DiaBan, Stem};
use crate::dinh_cuc::DinhCuc;
use crate::flags::DingjuMethod;
use crate::sao_mon_than::YinYangPan;
use crate::sao_mon_than::{BatMon, BatThan, CuuTinh, SaoMonThan};
use crate::truc_phu_su::{PanMethod, TrucPhuSu, ZhongGongKy};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub struct QiMenFlags {
    pub dingju_method: DingjuMethod,
    pub pan_method: PanMethod,
    pub yin_yang_pan: YinYangPan,
    pub zhong_gong_ky: ZhongGongKy,
    pub chan_thai_duong_thoi: bool,
}

impl Default for QiMenFlags {
    fn default() -> Self {
        Self {
            dingju_method: DingjuMethod::Chaibu,
            pan_method: PanMethod::Zhuan,
            yin_yang_pan: YinYangPan::Duong,
            zhong_gong_ky: ZhongGongKy::Khon2,
            chan_thai_duong_thoi: true,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct KyMonBan {
    pub dinh_cuc: DinhCuc,
    pub dia_ban: DiaBan,
    pub thien_ban: [Stem; 9],
    pub cuu_tinh: [CuuTinh; 9],
    pub bat_mon: [Option<BatMon>; 9],
    pub bat_than: [Option<BatThan>; 9],
    pub truc_phu: u8,
    pub truc_su: u8,
    pub sao_mon_than: SaoMonThan,
    pub tps: TrucPhuSu,
}
