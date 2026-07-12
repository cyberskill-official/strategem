use cyberos_thaiat::{cast_thai_at, Cap, CastInput, DemToan, Epoch, TatFlags};

fn input(flags: TatFlags) -> CastInput {
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
fn default_cast_envelope() {
    let r = cast_thai_at(&input(TatFlags::default()));
    assert_eq!(r.envelope["he"], "thai_at");
    assert_eq!(r.envelope["envelope_version"], 1);
    assert_eq!(r.ban.tich.tich_nien, 10_155_921);
    assert_eq!(r.ban.tich.nhap_cuc, 33);
    assert_ne!(r.ban.seat.thai_at_cung, 5);
    assert!(r.envelope["ban"]["thap_luc_than"].as_array().unwrap().len() == 16);
    assert!(!r.cache_key.is_empty());
}

#[test]
fn epoch_flag_changes_tich() {
    let a = TatFlags {
        epoch: Epoch::KimKinh,
        ..Default::default()
    };
    let b = TatFlags {
        epoch: Epoch::CoDien,
        ..Default::default()
    };
    let ra = cast_thai_at(&input(a));
    let rb = cast_thai_at(&input(b));
    assert_ne!(ra.ban.tich.tich_nien, rb.ban.tich.tich_nien);
    assert_ne!(
        ra.envelope["co_truong_phai"]["epoch"],
        rb.envelope["co_truong_phai"]["epoch"]
    );
}

#[test]
fn dem_toan_stamped() {
    let f = TatFlags {
        dem_toan: DemToan::SauThaiAt,
        ..Default::default()
    };
    let r = cast_thai_at(&input(f));
    assert_eq!(r.envelope["co_truong_phai"]["dem_toan"], "sau_thai_at");
}

#[test]
fn reproducible_cache_key() {
    let f = TatFlags::default();
    let a = cast_thai_at(&input(f));
    let b = cast_thai_at(&input(f));
    assert_eq!(a.cache_key, b.cache_key);
    assert_eq!(a.envelope["ban"], b.envelope["ban"]);
}

#[test]
fn cap_matrix() {
    for cap in [Cap::Nien, Cap::Nguyet, Cap::Nhat, Cap::Thoi] {
        let f = TatFlags {
            cap,
            ..Default::default()
        };
        let r = cast_thai_at(&input(f));
        assert_eq!(r.envelope["he"], "thai_at");
    }
}
