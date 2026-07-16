//! Canonical calendar flags. TASK-CORE-005.

use crate::derived::TruongSinhPhai;
use crate::pillars::LateZiHandling;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LichFlags {
    pub use_true_solar_time: bool,
    pub longitude_east: f64,
    pub tz_offset: String,
    pub zi_hour_day_rollover: String,
    pub late_zi_handling: LateZiHandling,
    pub truong_sinh_phai: TruongSinhPhai,
}

impl Default for LichFlags {
    fn default() -> Self {
        Self {
            use_true_solar_time: true,
            longitude_east: 106.7,
            tz_offset: "+07:00".into(),
            zi_hour_day_rollover: "23:00".into(),
            late_zi_handling: LateZiHandling::NextDay,
            truong_sinh_phai: TruongSinhPhai::AmDuong,
        }
    }
}

pub fn parse_tz_offset_hours(tz: &str) -> f64 {
    // "+07:00" / "-05:30"
    let s = tz.trim();
    let sign = if s.starts_with('-') { -1.0 } else { 1.0 };
    let body = s.trim_start_matches(['+', '-']);
    let mut parts = body.split(':');
    let h: f64 = parts.next().unwrap_or("0").parse().unwrap_or(0.0);
    let m: f64 = parts.next().unwrap_or("0").parse().unwrap_or(0.0);
    sign * (h + m / 60.0)
}
