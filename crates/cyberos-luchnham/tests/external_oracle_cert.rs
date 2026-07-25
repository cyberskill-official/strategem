//! W4 external oracle certification — LiuRen / kinliuren.
//!
//! - `sample/` rows always run (classical 伏吟 / 返吟 pins; harness proof).
//! - `full/` kinliuren dump gates at 100% when present; otherwise SKIP (honest).

use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{
    khoa_the_from_method, lap_tam_truyen, lap_tu_khoa, quay_thien_ban, KhoaThe, Phap,
};
use cyberos_oracle_cert::{
    csv_rows, dataset_path, load_csv, require_sample, DatasetKind, LoadOutcome,
};

fn parse_chi(s: &str) -> Chi {
    match s {
        "Ty" => Chi::Ty,
        "Suu" => Chi::Suu,
        "Dan" => Chi::Dan,
        "Mao" => Chi::Mao,
        "Thin" => Chi::Thin,
        "Ty2" => Chi::Ty2,
        "Ngo" => Chi::Ngo,
        "Mui" => Chi::Mui,
        "Than" => Chi::Than,
        "Dau" => Chi::Dau,
        "Tuat" => Chi::Tuat,
        "Hoi" => Chi::Hoi,
        other => panic!("unknown Chi romanizer {other:?}"),
    }
}

fn parse_can(s: &str) -> Can {
    match s {
        "Giap" => Can::Giap,
        "At" => Can::At,
        "Binh" => Can::Binh,
        "Dinh" => Can::Dinh,
        "Mau" => Can::Mau,
        "Ky" => Can::Ky,
        "Canh" => Can::Canh,
        "Tan" => Can::Tan,
        "Nham" => Can::Nham,
        "Quy" => Can::Quy,
        other => panic!("unknown Can romanizer {other:?}"),
    }
}

fn parse_phap(s: &str) -> Phap {
    match s {
        "PhucNgam" => Phap::PhucNgam,
        "PhanNgam" => Phap::PhanNgam,
        "ThiepHai" => Phap::ThiepHai,
        "TacKhac" => Phap::TacKhac,
        "TyDung" => Phap::TyDung,
        "BatChuyen" => Phap::BatChuyen,
        "BietTrach" => Phap::BietTrach,
        "DaoKhac" => Phap::DaoKhac,
        "MaoTinh" => Phap::MaoTinh,
        other => panic!("unknown Phap {other:?}"),
    }
}

fn phap_consistent_with_khoa(phap: Phap, khoa: KhoaThe) -> bool {
    match phap {
        Phap::PhucNgam => matches!(khoa, KhoaThe::PhucNgam),
        Phap::PhanNgam => matches!(khoa, KhoaThe::PhanNgam),
        Phap::ThiepHai => matches!(khoa, KhoaThe::ThiepHai),
        Phap::TacKhac
        | Phap::TyDung
        | Phap::BatChuyen
        | Phap::BietTrach
        | Phap::DaoKhac
        | Phap::MaoTinh => true,
    }
}

fn assert_khoa_the_rows(text: &str, label: &str) {
    let rows = csv_rows(text);
    assert!(!rows.is_empty(), "{label}: expected at least one data row");
    for (line_no, cols) in rows {
        assert!(
            cols.len() >= 6,
            "{label} line {line_no}: need ≥6 cols, got {}",
            cols.len()
        );
        let nt = parse_chi(cols[0]);
        let gio = parse_chi(cols[1]);
        let can = parse_can(cols[2]);
        let day = parse_chi(cols[3]);
        let exp_phap = parse_phap(cols[4]);
        let exp_han = cols[5];

        let (thien, state) = quay_thien_ban(nt, gio);
        let tk = lap_tu_khoa(&thien, can, day);
        let tt = lap_tam_truyen(&tk, &thien, state, can);
        assert_eq!(tt.phap, exp_phap, "{label} line {line_no}: phap mismatch");
        assert!(
            phap_consistent_with_khoa(tt.phap, tt.khoa_the),
            "{label} line {line_no}: khoa_the {:?} inconsistent with phap {:?}",
            tt.khoa_the,
            tt.phap
        );
        let hit = khoa_the_from_method(&tt);
        assert_eq!(
            hit.name, exp_han,
            "{label} line {line_no}: Han khoa_the name mismatch"
        );
    }
}

#[test]
fn kinliuren_sample_harness_matches_classical_pins() {
    let (_path, text) = require_sample("kinliuren", "khoa_the.csv");
    assert_khoa_the_rows(&text, "kinliuren sample");
}

#[test]
fn kinliuren_full_dump_gates_or_skips_honestly() {
    let path = dataset_path("kinliuren", DatasetKind::Full, "khoa_the.csv");
    match load_csv(&path, "kinliuren full") {
        LoadOutcome::Absent { message, .. } => {
            eprintln!("{message}");
        }
        LoadOutcome::Ready {
            text, row_count, ..
        } => {
            assert_khoa_the_rows(&text, "kinliuren full");
            eprintln!("kinliuren full certification: {row_count} rows matched 100%");
        }
    }
}
