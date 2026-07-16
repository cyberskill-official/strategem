//! LiuRen ban assembly types — TASK-LN-006.

use crate::tamtruyen::TamTruyen;
use crate::thiendiaban::TrangThaiBan;
use crate::thientuong::ThienTuongBan;
use crate::tukhoa::TuKhoa;
use cyberos_lichphap::Chi;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThienDiaBan {
    pub dia: [Chi; 12],
    pub thien: [Chi; 12],
    pub nguyet_tuong: Chi,
    pub gio_chiem: Chi,
    pub state: TrangThaiBan,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BanLucNham {
    pub thien_dia_ban: ThienDiaBan,
    pub tu_khoa: TuKhoa,
    pub tam_truyen: TamTruyen,
    pub thien_tuong: ThienTuongBan,
    pub khoa_the: Vec<String>,
    pub khong_vong: [Chi; 2],
}
