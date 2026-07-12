//! Calendar core (`cyberos-lichphap`). FR-CORE-007: ganzhi + relations.

pub mod ganzhi;
pub mod relations;

pub use ganzhi::{can_chi_of, giap_ty_from_can_chi, Can, Chi, GanzhiError, GiapTy, NguHanh};
pub use relations::{
    bi_khac, duoc_sinh, khac, ngu_hanh_of_can, ngu_hanh_of_chi, quan_he, sinh, tam_hop_cua,
    ChiQuanHe,
};
