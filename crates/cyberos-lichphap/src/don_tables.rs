//! Ngu Ho Don / Ngu Thu Don tables. TASK-CORE-003.

use crate::ganzhi::Can;

/// First month stem (for 寅 month) given year stem class.
pub fn ngu_ho_don_first_month_can(year_can: Can) -> Can {
    match year_can {
        Can::Giap | Can::Ky => Can::Binh,   // 甲己 -> 丙寅
        Can::At | Can::Canh => Can::Mau,    // 乙庚 -> 戊寅
        Can::Binh | Can::Tan => Can::Canh,  // 丙辛 -> 庚寅
        Can::Dinh | Can::Nham => Can::Nham, // 丁壬 -> 壬寅
        Can::Mau | Can::Quy => Can::Giap,   // 戊癸 -> 甲寅
    }
}

/// Stem for 子 hour given day stem class (Ngu Thu Don).
pub fn ngu_thu_don_zi_can(day_can: Can) -> Can {
    match day_can {
        Can::Giap | Can::Ky => Can::Giap,   // 甲己 -> 甲子
        Can::At | Can::Canh => Can::Binh,   // 乙庚 -> 丙子
        Can::Binh | Can::Tan => Can::Mau,   // 丙辛 -> 戊子
        Can::Dinh | Can::Nham => Can::Canh, // 丁壬 -> 庚子
        Can::Mau | Can::Quy => Can::Nham,   // 戊癸 -> 壬子
    }
}

pub fn advance_can(c: Can, steps: i32) -> Can {
    let i = (c.index() as i32 + steps).rem_euclid(10) as u8;
    Can::from_index(i).unwrap()
}
