//! Calendar core (`cyberos-lichphap`). FR-CORE-001 solar terms + FR-CORE-007 ganzhi.

pub mod delta_t;
pub mod eot;
pub mod ganzhi;
pub mod relations;
pub mod solar;
pub mod tietkhi;
pub mod truesolar;

pub use delta_t::{delta_t_seconds, tt_jd_to_utc_jd, utc_jd_to_tt_jd};
pub use eot::{eot_at_date, equation_of_time_minutes};
pub use ganzhi::{can_chi_of, giap_ty_from_can_chi, Can, Chi, GanzhiError, GiapTy, NguHanh};
pub use relations::{
    bi_khac, duoc_sinh, khac, ngu_hanh_of_can, ngu_hanh_of_chi, quan_he, sinh, tam_hop_cua,
    ChiQuanHe,
};
pub use solar::{ang_diff, julian_day_utc, kinh_do_mat_troi};
pub use tietkhi::{
    solve_term_instant, term_def, tiet_khi_hien_hanh, tiet_khi_year, TermKind, TietKhi, NAMES,
};
pub use truesolar::{
    longitude_correction_minutes, standard_meridian_from_utc_offset_hours, true_solar_time,
    TrueSolarResult,
};
