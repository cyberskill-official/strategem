//! COV-006 — TaiYi cach_cuc emission + chu/khach toan always + flag combos.

use cyberos_thaiat::{cast_thai_at, Cap, CastInput, DemToan, Epoch, TatFlags};

fn base_input(flags: TatFlags) -> CastInput {
    CastInput {
        nam_ce: 2004,
        year_chi_idx: 0,
        datetime: "2004-01-01T00:00:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        flags,
    }
}

#[test]
fn cac_toan_and_chu_khach_always_present() {
    let r = cast_thai_at(&base_input(TatFlags::default()));
    let ban = &r.envelope["ban"];
    let ct = &ban["cac_toan"];
    assert!(ct.get("chu_toan").is_some());
    assert!(ct.get("khach_toan").is_some());
    assert!(ct.get("chu_truong_doan").is_some());
    assert!(ct.get("khach_truong_doan").is_some());
    let ck = &ban["chu_khach"];
    assert!(ck.get("chu_toan").is_some());
    assert!(ck.get("khach_toan").is_some());
    // note is not a victory verdict
    let note = ck["note"].as_str().unwrap_or("");
    assert!(note.contains("not a victory") || note.contains("positional"));
}

#[test]
fn epoch_and_dem_toan_flag_combinations() {
    for epoch in [Epoch::KimKinh, Epoch::CoDien] {
        for dem in [DemToan::TruocThaiAt, DemToan::SauThaiAt] {
            for duong in [true, false] {
                let f = TatFlags {
                    epoch,
                    dem_toan: dem,
                    duong_don: duong,
                    cap: Cap::Nien,
                };
                let r = cast_thai_at(&base_input(f));
                assert_eq!(r.envelope["he"], "thai_at");
                let ctp = r.envelope["co_truong_phai"].as_object().unwrap();
                assert!(ctp.contains_key("epoch"));
                assert!(ctp.contains_key("dem_toan"));
                let ban = &r.envelope["ban"];
                assert!(
                    ban["cac_toan"]["chu_toan"].is_number()
                        || ban["cac_toan"]["chu_toan"].is_i64()
                        || ban["cac_toan"]["chu_toan"].as_u64().is_some()
                        || ban["cac_toan"]["chu_toan"].as_i64().is_some()
                        || ban["cac_toan"]["chu_toan"].is_number()
                );
                // cach_cuc is array (may be empty when no classical condition)
                assert!(r.envelope["cach_cuc"].is_array());
            }
        }
    }
}

#[test]
fn golden_years_may_emit_nonempty_cach_when_conditions_met() {
    // Scan several years — at least one should yield non-empty cach_cuc
    // when classical adjacency/opposition holds (not a hard fail if sparse).
    let mut any_nonempty = false;
    let mut always_has_toan = true;
    for year in [1984, 1996, 2004, 2012, 2020, 2024] {
        for ychi in 0u8..12 {
            let r = cast_thai_at(&CastInput {
                nam_ce: year,
                year_chi_idx: ychi,
                datetime: format!("{year}-06-01T12:00:00"),
                tz: "+07:00".into(),
                kinh_do: 105.0,
                flags: TatFlags::default(),
            });
            let ban = &r.envelope["ban"];
            if ban["cac_toan"]["chu_toan"].is_null() {
                always_has_toan = false;
            }
            if let Some(arr) = r.envelope["cach_cuc"].as_array() {
                if !arr.is_empty() {
                    any_nonempty = true;
                    // entries carry classical name + citations, no victory verdict field
                    let e = &arr[0];
                    assert!(e.get("name").is_some() || e.get("id").is_some());
                    assert!(e.get("winner").is_none());
                }
            }
        }
    }
    assert!(always_has_toan, "chu/khach toan must always be present");
    assert!(
        any_nonempty,
        "COV-006 expects ≥1 golden year/chi with non-empty cach_cuc"
    );
}
