//! FR-TAT-005 cach cuc + bon tieu chi tests.

use cyberos_thaiat::{
    luan_bon_tieu_chi, map_to_envelope_cach_cuc, nhan_dien_cach_cuc, tinh_tam_tai, BatTuong,
    BienTheKich, Cach, DemToan, TamTai, ToanResult, TruongDoan,
};

fn bat(ta_adj: u8, thuy: u8, van: u8, chu_dai: u8, khach_dai: u8) -> BatTuong {
    // ta_adj unused — caller sets thai_at_ring separately
    let _ = ta_adj;
    BatTuong {
        van_xuong: van,
        thuy_kich: thuy,
        ke_than: 0,
        chu_dai_tuong: chu_dai,
        khach_dai_tuong: khach_dai,
        chu_tham_tuong: (chu_dai + 1) % 16,
        khach_tham_tuong: (khach_dai + 1) % 16,
        chu_toan: ToanResult {
            value: 12,
            label: TruongDoan::Truong,
        },
        khach_toan: ToanResult {
            value: 8,
            label: TruongDoan::Doan,
        },
        dem_toan: DemToan::TruocThaiAt,
    }
}

#[test]
fn yem_when_khach_same_palace() {
    let b = bat(5, 5, 0, 1, 5); // khach_dai = thuy = 5 = thai at
    let found = nhan_dien_cach_cuc(&b, 5);
    assert!(found.iter().any(|c| c.cach == Cach::Yem));
}

#[test]
fn kich_noi_ngoai() {
    let ta = 5u8;
    let noi = bat(ta, 6, 0, 1, 2); // after
    let f = nhan_dien_cach_cuc(&noi, ta);
    let k = f.iter().find(|c| c.cach == Cach::Kich).unwrap();
    assert_eq!(k.bien_the, Some(BienTheKich::NoiKich));

    let ngoai = bat(ta, 4, 0, 1, 2); // before
    let f2 = nhan_dien_cach_cuc(&ngoai, ta);
    let k2 = f2.iter().find(|c| c.cach == Cach::Kich).unwrap();
    assert_eq!(k2.bien_the, Some(BienTheKich::NgoaiKich));
}

#[test]
fn tam_tai_du_khuyet() {
    assert_eq!(tinh_tam_tai(true, true, true), TamTai::Du);
    assert_eq!(tinh_tam_tai(true, false, true), TamTai::Khuyet);
}

#[test]
fn no_verdict_field_and_envelope_map() {
    let b = bat(0, 8, 0, 0, 1);
    let cach = nhan_dien_cach_cuc(&b, 0);
    let facts = luan_bon_tieu_chi(&b, cach.clone(), true, true, true);
    let s = serde_json::to_value(&facts).unwrap();
    assert!(s.get("winner").is_none());
    assert!(s.get("verdict").is_none());
    assert!(s.get("hoa").is_some());
    let env = map_to_envelope_cach_cuc(&cach);
    for e in &env {
        assert!(!e.get("citations").unwrap().as_array().unwrap().is_empty());
    }
}

#[test]
fn pure_idempotent() {
    let b = bat(3, 3, 11, 1, 2);
    let a = nhan_dien_cach_cuc(&b, 3);
    let c = nhan_dien_cach_cuc(&b, 3);
    assert_eq!(a, c);
}
