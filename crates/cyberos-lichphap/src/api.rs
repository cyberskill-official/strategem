//! Public calendar API entrypoint. TASK-CORE-005.

use crate::flags::LichFlags;
use crate::output::{build_lich_phap, LichPhap};

/// Canonical entry: compute `lich_phap` for envelope slot.
pub fn tinh_lich_phap(
    year: i32,
    month: u32,
    day: u32,
    hour: u32,
    minute: u32,
    second: u32,
    flags: LichFlags,
) -> LichPhap {
    build_lich_phap(year, month, day, hour, minute, second, flags)
}
