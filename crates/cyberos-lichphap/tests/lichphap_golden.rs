use cyberos_lichphap::{tinh_lich_phap, LateZiHandling, LichFlags, TruongSinhPhai};

#[test]
fn all_six_flags_present_and_defaults() {
    let flags = LichFlags::default();
    let lp = tinh_lich_phap(2004, 1, 1, 10, 30, 0, flags.clone());
    let j = serde_json::to_value(&lp).unwrap();
    let co = j.get("co_lich_phap").unwrap();
    for key in [
        "use_true_solar_time",
        "longitude_east",
        "tz_offset",
        "zi_hour_day_rollover",
        "late_zi_handling",
        "truong_sinh_phai",
    ] {
        assert!(co.get(key).is_some(), "missing {key}");
    }
    assert_eq!(co["tz_offset"], "+07:00");
    assert_eq!(co["zi_hour_day_rollover"], "23:00");
    assert!(lp.chan_thai_duong);
    assert!(!lp.year.is_empty() && !lp.day.is_empty() && !lp.hour.is_empty());
}

#[test]
fn flag_flip_true_solar_changes_hour_only_when_needed() {
    let mut a = LichFlags::default();
    a.use_true_solar_time = true;
    let mut b = a.clone();
    b.use_true_solar_time = false;
    let la = tinh_lich_phap(2004, 1, 1, 10, 30, 0, a);
    let lb = tinh_lich_phap(2004, 1, 1, 10, 30, 0, b);
    assert_ne!(la.chan_thai_duong, lb.chan_thai_duong);
    // pillars may differ in hour
    assert_eq!(la.year, lb.year);
    assert_eq!(
        la.co_lich_phap.longitude_east,
        lb.co_lich_phap.longitude_east
    );
}

#[test]
fn reproduction_from_flags() {
    let flags = LichFlags {
        use_true_solar_time: true,
        longitude_east: 106.7,
        tz_offset: "+07:00".into(),
        zi_hour_day_rollover: "23:00".into(),
        late_zi_handling: LateZiHandling::NextDay,
        truong_sinh_phai: TruongSinhPhai::NguHanh,
    };
    let a = tinh_lich_phap(2004, 1, 1, 10, 30, 0, flags.clone());
    let b = tinh_lich_phap(2004, 1, 1, 10, 30, 0, flags);
    assert_eq!(a, b);
}
