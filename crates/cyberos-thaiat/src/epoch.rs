use crate::flags::Epoch;

/// Base offsets for tich nien.
pub fn tich_nien_raw(nam_ce: i32, epoch: Epoch) -> u64 {
    match epoch {
        Epoch::KimKinh => 10_153_917u64 + nam_ce as u64,
        Epoch::CoDien => {
            // anchored 1_937_281 at 724 CE
            let delta = nam_ce as i64 - 724;
            (1_937_281i64 + delta) as u64
        }
    }
}
