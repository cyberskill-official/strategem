use cyberos_qimen::{dung_than, selection_table, LoaiCauHoi};

#[test]
fn table_nonempty_all_types() {
    for loai in [
        LoaiCauHoi::CauTai,
        LoaiCauHoi::SuNghiepCongDanh,
        LoaiCauHoi::HonNhan,
        LoaiCauHoi::KienTung,
        LoaiCauHoi::XuatHanh,
        LoaiCauHoi::BenhTat,
        LoaiCauHoi::CanhTranhChuKhach,
        LoaiCauHoi::HopTac,
    ] {
        assert!(!selection_table(loai).is_empty());
    }
}

#[test]
fn locate_mon() {
    let mon = [
        Some("Huu".into()),
        None,
        None,
        None,
        None,
        Some("Khai".into()),
        None,
        Some("Sinh".into()),
        None,
    ];
    let stars = vec!["ThienBong".into(); 9];
    let located = dung_than(LoaiCauHoi::CauTai, &mon, &stars);
    assert!(located
        .iter()
        .any(|d| d.symbol == "Khai" && d.cung == Some(6)));
    assert!(located
        .iter()
        .any(|d| d.symbol == "Sinh" && d.cung == Some(8)));
    // no meaning strings in output
    for d in &located {
        assert!(!d.symbol.is_empty());
    }
}
