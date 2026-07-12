use cyberos_lichphap::{
    can_chi_of, season_of_chi, truong_sinh_stage, tuan_khong, vuong_suy, Can, Chi, GiapTy, NguHanh,
    Season, TruongSinhPhai, VuongSuy,
};

#[test]
fn tuan_khong_closed_form_and_pins() {
    // 甲子 -> 戌 亥
    let (a, b) = tuan_khong(Can::Giap, Chi::Ty);
    assert_eq!(
        (a.glyph(), b.glyph()),
        ("戌", "亥"),
        "got {} {}",
        a.glyph(),
        b.glyph()
    );
    // 甲午 -> 辰 巳
    let (a, b) = tuan_khong(Can::Giap, Chi::Ngo);
    assert_eq!((a.glyph(), b.glyph()), ("辰", "巳"));

    // exhaustive: all 60 pairs produce two distinct branches
    for n in 0u8..60 {
        let (c, z) = can_chi_of(GiapTy::new(n).unwrap());
        let (x, y) = tuan_khong(c, z);
        assert_ne!(x, y);
    }
}

#[test]
fn vuong_suy_xuan_pin() {
    assert_eq!(vuong_suy(Season::Xuan, NguHanh::Moc), VuongSuy::Vuong);
    assert_eq!(vuong_suy(Season::Xuan, NguHanh::Kim), VuongSuy::Tu2);
    assert_eq!(vuong_suy(Season::Xuan, NguHanh::Tho), VuongSuy::Tu);
    assert_eq!(season_of_chi(Chi::Dan), Season::Xuan);
}

#[test]
fn truong_sinh_am_duong_pins() {
    // 甲 at 亥 is TruongSinh forward
    assert_eq!(
        truong_sinh_stage(Can::Giap, Chi::Hoi, TruongSinhPhai::AmDuong),
        cyberos_lichphap::TruongSinhStage::TruongSinh
    );
    // 辛 at 子 is TruongSinh backward start
    assert_eq!(
        truong_sinh_stage(Can::Tan, Chi::Ty, TruongSinhPhai::AmDuong),
        cyberos_lichphap::TruongSinhStage::TruongSinh
    );
}

#[test]
fn schools_differ_for_some_stem() {
    // 甲 am_duong start 亥; ngu_hanh Moc also 亥 — pick 乙
    // 乙 am_duong start 午 reverse; ngu_hanh Moc start 亥
    let am = truong_sinh_stage(Can::At, Chi::Hoi, TruongSinhPhai::AmDuong);
    let nh = truong_sinh_stage(Can::At, Chi::Hoi, TruongSinhPhai::NguHanh);
    assert_ne!(am, nh, "flag must change positions");
}
