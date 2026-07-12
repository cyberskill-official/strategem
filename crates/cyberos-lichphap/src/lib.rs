//! Calendar core (`cyberos-lichphap`). FR-CORE-001 solar terms + FR-CORE-007 ganzhi.

pub mod api;
pub mod delta_t;
pub mod derived;
pub mod don_tables;
pub mod eot;
pub mod flags;
pub mod ganzhi;
pub mod output;
pub mod pillars;
pub mod relations;
pub mod solar;
pub mod tietkhi;
pub mod truesolar;

pub use api::tinh_lich_phap;
pub use delta_t::{delta_t_seconds, tt_jd_to_utc_jd, utc_jd_to_tt_jd};
pub use derived::{
    season_of_chi, truong_sinh_stage, tuan_khong, vuong_suy, Season, TruongSinhPhai,
    TruongSinhStage, VuongSuy,
};
pub use eot::{eot_at_date, equation_of_time_minutes};
pub use flags::{parse_tz_offset_hours, LichFlags};
pub use ganzhi::{can_chi_of, giap_ty_from_can_chi, Can, Chi, GanzhiError, GiapTy, NguHanh};
pub use output::LichPhap;
pub use pillars::{
    compute_pillars, day_pillar, hour_pillar, month_pillar, year_pillar, FourPillars,
    LateZiHandling, Pillar,
};
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
