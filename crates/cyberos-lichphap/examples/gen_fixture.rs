fn main() {
    use cyberos_lichphap::{julian_day_utc, solve_term_instant, term_def};
    println!("# idx,jd_utc  // 2020 solar terms reference (self-consistent FR-CORE-001)");
    for i in 0u8..24 {
        let t = term_def(i).target_longitude;
        let guess = julian_day_utc(2020, 2, 4.0) + (i as f64) * (365.2422 / 24.0);
        let jd = solve_term_instant(t, guess);
        println!("{},{:.10}", i, jd);
    }
}
