use cyberos_lichphap::{compute_pillars, day_pillar, year_pillar, LateZiHandling};

#[test]
fn year_turns_at_lap_xuan_1984() {
    // before Lap Xuan 1984 → prior year 癸亥; after → 甲子
    let before = year_pillar(1984, 2, 3);
    let after = year_pillar(1984, 2, 5);
    assert_eq!(before.glyph(), "癸亥");
    assert_eq!(after.glyph(), "甲子");
    // Jan 1 is not the boundary
    let jan = year_pillar(1984, 1, 1);
    assert_eq!(jan.glyph(), "癸亥");
}

#[test]
fn day_anchors() {
    assert_eq!(day_pillar(2000, 1, 1).glyph(), "戊午");
    assert_eq!(day_pillar(1949, 10, 1).glyph(), "甲子");
}

#[test]
fn day_continuous_across_month() {
    let a = day_pillar(2000, 1, 31);
    let b = day_pillar(2000, 2, 1);
    // consecutive days differ by one in sexagenary
    assert_ne!(a.glyph(), b.glyph());
}

#[test]
fn hour_uses_true_solar_and_zi_flags() {
    // late zi 23:30 next-day rollover
    let p = compute_pillars(
        2000,
        1,
        1,
        23,
        30,
        0,
        7.0,
        105.0,
        false,
        LateZiHandling::NextDay,
    );
    assert_eq!(p.hour.chi.glyph(), "子");
    // day advanced vs pure day_pillar(2000,1,1)
    let pure = day_pillar(2000, 1, 1);
    assert_ne!(p.day.glyph(), pure.glyph());

    let da = compute_pillars(
        2000,
        1,
        1,
        23,
        30,
        0,
        7.0,
        105.0,
        false,
        LateZiHandling::DaZi,
    );
    assert_eq!(da.day.glyph(), pure.glyph());
    assert_eq!(da.hour.chi.glyph(), "子");
}

#[test]
fn pillars_serialize_han() {
    let p = day_pillar(2000, 1, 1);
    assert_eq!(p.glyph(), "戊午");
    let j = serde_json::to_string(&p).unwrap();
    assert!(j.contains("戊") && j.contains("午"), "{j}");
}
