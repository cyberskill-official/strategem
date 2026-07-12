use cyberos_thaiat::{
    an_thai_at, compute_tich_nien, is_chinh_cung, palace_to_ring, Epoch, LoaiThan, THAP_LUC_THAN,
};

#[test]
fn sixteen_ring_order() {
    assert_eq!(THAP_LUC_THAN.len(), 16);
    assert_eq!(THAP_LUC_THAN[0].han, "地主");
    assert_eq!(THAP_LUC_THAN[0].chi, "子");
    assert_eq!(THAP_LUC_THAN[8].han, "大威");
    assert_eq!(THAP_LUC_THAN[14].han, "陰德");
    assert_eq!(THAP_LUC_THAN[15].han, "大義");
}

#[test]
fn chinh_gian_split() {
    let chinh: Vec<_> = THAP_LUC_THAN
        .iter()
        .filter(|t| t.loai == LoaiThan::ChinhCung)
        .collect();
    let gian: Vec<_> = THAP_LUC_THAN
        .iter()
        .filter(|t| t.loai == LoaiThan::GianThan)
        .collect();
    assert_eq!(chinh.len(), 8);
    assert_eq!(gian.len(), 8);
    for r in [0u8, 2, 4, 6, 8, 10, 12, 14] {
        assert!(is_chinh_cung(r));
    }
    for r in [1u8, 3, 5, 7, 9, 11, 13, 15] {
        assert!(!is_chinh_cung(r));
    }
}

#[test]
fn seat_always_chinh_cung() {
    for y in 1950..2050 {
        let tn = compute_tich_nien(y, Epoch::KimKinh);
        for duong in [true, false] {
            let seat = an_thai_at(&tn, duong);
            assert_ne!(seat.thai_at_cung, 5);
            assert!(is_chinh_cung(seat.thai_at_ring), "year {y} ring {}", seat.thai_at_ring);
        }
    }
}

#[test]
fn palace_mapping() {
    assert_eq!(palace_to_ring(1), 14);
    assert_eq!(palace_to_ring(8), 0);
    assert_eq!(palace_to_ring(5), 10);
}
