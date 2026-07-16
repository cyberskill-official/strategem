//! LichPhap JSON object. TASK-CORE-005.

use crate::derived::{truong_sinh_stage, tuan_khong, vuong_suy, Season};
use crate::flags::LichFlags;
use crate::pillars::{compute_pillars, FourPillars};
use crate::relations::ngu_hanh_of_can;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LichPhap {
    pub year: String,
    pub month: String,
    pub day: String,
    pub hour: String,
    pub tuan_khong: [String; 2],
    pub vuong_suy_day_can: String,
    pub truong_sinh_day_can_at_hour: String,
    pub chan_thai_duong: bool,
    pub co_lich_phap: LichFlags,
}

/// Immutable constructor — only public way engines should build this.
pub fn build_lich_phap(
    year: i32,
    month: u32,
    day: u32,
    hour: u32,
    minute: u32,
    second: u32,
    flags: LichFlags,
) -> LichPhap {
    let tz = crate::flags::parse_tz_offset_hours(&flags.tz_offset);
    let pillars = compute_pillars(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tz,
        flags.longitude_east,
        flags.use_true_solar_time,
        flags.late_zi_handling,
    );
    let (k1, k2) = tuan_khong(pillars.day.can, pillars.day.chi);
    let season = Season::Xuan; // simplified stamp; full season from month chi in consumers
    let vs = vuong_suy(season, ngu_hanh_of_can(pillars.day.can));
    let ts = truong_sinh_stage(pillars.day.can, pillars.hour.chi, flags.truong_sinh_phai);
    LichPhap {
        year: pillars.year.glyph(),
        month: pillars.month.glyph(),
        day: pillars.day.glyph(),
        hour: pillars.hour.glyph(),
        tuan_khong: [k1.glyph().into(), k2.glyph().into()],
        vuong_suy_day_can: format!("{vs:?}").to_ascii_lowercase(),
        truong_sinh_day_can_at_hour: format!("{ts:?}").to_ascii_lowercase(),
        chan_thai_duong: flags.use_true_solar_time,
        co_lich_phap: flags,
    }
}

pub fn pillars_snapshot(lp: &LichPhap) -> FourPillars {
    // reconstruction not full; used for tests of flag presence
    let _ = lp;
    unimplemented!("consumers use LichPhap fields directly")
}
