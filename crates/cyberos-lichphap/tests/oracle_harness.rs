//! Oracle harness (FR-CORE-006). Compares against committed self-generated fixtures.
//! External sxwnl/tyme4py only used offline via scripts/gen_oracle_fixtures.py — not Cargo deps.

use cyberos_lichphap::{
    day_pillar, eot_at_date, equation_of_time_minutes, julian_day_utc, solve_term_instant,
    term_def, tuan_khong, Can, Chi,
};
use std::fs;
use std::path::PathBuf;

#[derive(Default)]
struct OracleReport {
    max_term_delta_s: f64,
    boundary_cases_seen: u32,
    failures: Vec<String>,
}

#[test]
fn oracle_harness_terms_and_boundaries() {
    let mut report = OracleReport::default();
    let fix = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/tietkhi_ref_2020.csv");
    for line in fs::read_to_string(fix).unwrap().lines() {
        if line.starts_with('#') || line.trim().is_empty() {
            continue;
        }
        let mut p = line.split(',');
        let idx: u8 = p.next().unwrap().parse().unwrap();
        let ref_jd: f64 = p.next().unwrap().parse().unwrap();
        let got = solve_term_instant(term_def(idx).target_longitude, ref_jd);
        let d = (got - ref_jd).abs() * 86400.0;
        report.max_term_delta_s = report.max_term_delta_s.max(d);
        if d > 60.0 {
            report.failures.push(format!("term {idx} delta {d}s"));
        }
    }
    assert!(
        report.max_term_delta_s < 60.0,
        "max term delta {}s",
        report.max_term_delta_s
    );

    // Lap Xuan boundary: year pillar change 1984
    let y_before = cyberos_lichphap::year_pillar(1984, 2, 3).glyph();
    let y_after = cyberos_lichphap::year_pillar(1984, 2, 5).glyph();
    assert_ne!(y_before, y_after);
    report.boundary_cases_seen += 1;

    // 23:00 zi boundary via hour chi
    let p = cyberos_lichphap::compute_pillars(
        2000,
        1,
        1,
        23,
        30,
        0,
        7.0,
        105.0,
        false,
        cyberos_lichphap::LateZiHandling::NextDay,
    );
    assert_eq!(p.hour.chi.glyph(), "子");
    report.boundary_cases_seen += 1;

    // derived: tuan khong pin
    let (a, b) = tuan_khong(Can::Giap, Chi::Ty);
    assert_eq!((a.glyph(), b.glyph()), ("戌", "亥"));

    // true solar hand-calc style: EoT extrema non-trivial
    assert!(eot_at_date(2000, 2, 11.0) < -10.0);
    assert!(equation_of_time_minutes(julian_day_utc(2000, 11, 3.0)) > 10.0);

    // day pillar anchors
    assert_eq!(day_pillar(2000, 1, 1).glyph(), "戊午");
    assert_eq!(day_pillar(1949, 10, 1).glyph(), "甲子");

    assert!(report.boundary_cases_seen > 0);
    assert!(report.failures.is_empty(), "{:?}", report.failures);
}
