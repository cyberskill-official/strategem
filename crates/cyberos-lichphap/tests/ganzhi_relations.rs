use cyberos_lichphap::{
    can_chi_of, giap_ty_from_can_chi, khac, ngu_hanh_of_can, ngu_hanh_of_chi, quan_he, sinh,
    tam_hop_cua, Can, Chi, ChiQuanHe, GiapTy, NguHanh,
};

#[test]
fn round_trip_can_chi_giap_ty() {
    for c in Can::ALL {
        assert_eq!(Can::from_index(c.index()), Some(c));
        assert_eq!(Can::from_glyph(c.glyph()), Some(c));
    }
    for z in Chi::ALL {
        assert_eq!(Chi::from_index(z.index()), Some(z));
        assert_eq!(Chi::from_glyph(z.glyph()), Some(z));
    }
    for n in 0u8..60 {
        let g = GiapTy::new(n).unwrap();
        let (c, z) = can_chi_of(g);
        assert_eq!(giap_ty_from_can_chi(c, z).unwrap(), g);
    }
    // illegal pair 甲丑
    assert!(giap_ty_from_can_chi(Can::Giap, Chi::Suu).is_err());
}

#[test]
fn ty_and_ty2_never_conflated() {
    assert_ne!(Chi::Ty.glyph(), Chi::Ty2.glyph());
    assert_eq!(Chi::Ty.glyph(), "子");
    assert_eq!(Chi::Ty2.glyph(), "巳");
    assert_ne!(ngu_hanh_of_chi(Chi::Ty), ngu_hanh_of_chi(Chi::Ty2));
    assert_eq!(ngu_hanh_of_chi(Chi::Ty), NguHanh::Thuy);
    assert_eq!(ngu_hanh_of_chi(Chi::Ty2), NguHanh::Hoa);
}

#[test]
fn ngu_hanh_tables() {
    assert_eq!(ngu_hanh_of_can(Can::Giap), NguHanh::Moc);
    assert_eq!(ngu_hanh_of_can(Can::At), NguHanh::Moc);
    assert_eq!(ngu_hanh_of_can(Can::Binh), NguHanh::Hoa);
    assert_eq!(ngu_hanh_of_can(Can::Mau), NguHanh::Tho);
    assert_eq!(ngu_hanh_of_can(Can::Canh), NguHanh::Kim);
    assert_eq!(ngu_hanh_of_can(Can::Nham), NguHanh::Thuy);
    for z in [Chi::Thin, Chi::Tuat, Chi::Suu, Chi::Mui] {
        assert_eq!(ngu_hanh_of_chi(z), NguHanh::Tho);
    }
    assert_eq!(ngu_hanh_of_chi(Chi::Hoi), NguHanh::Thuy);
}

#[test]
fn sinh_khac_cycles() {
    assert!(sinh(NguHanh::Moc, NguHanh::Hoa));
    assert!(khac(NguHanh::Moc, NguHanh::Tho));
    assert!(!sinh(NguHanh::Moc, NguHanh::Tho));
    assert!(!khac(NguHanh::Moc, NguHanh::Hoa));
    // full cycle
    let order = [
        NguHanh::Moc,
        NguHanh::Hoa,
        NguHanh::Tho,
        NguHanh::Kim,
        NguHanh::Thuy,
    ];
    for i in 0..5 {
        assert!(sinh(order[i], order[(i + 1) % 5]));
        assert!(khac(order[i], order[(i + 2) % 5]));
    }
}

#[test]
fn relation_sets_exhaustive() {
    // luc xung sample
    assert!(quan_he(Chi::Ty, Chi::Ngo).contains(&ChiQuanHe::LucXung));
    // luc hop
    assert!(quan_he(Chi::Ty, Chi::Suu).contains(&ChiQuanHe::LucHop));
    // symmetry
    for a in Chi::ALL {
        for b in Chi::ALL {
            let mut x = quan_he(a, b);
            let mut y = quan_he(b, a);
            x.sort_by_key(|q| format!("{q:?}"));
            y.sort_by_key(|q| format!("{q:?}"));
            assert_eq!(x, y, "asymmetric {a:?} {b:?}");
        }
    }
    // empty pair (no relation) — 子寅 has no classical pair relation of listed sets
    // 子 and 寅: not hop/xung/hai/pha as pair (子 is with 丑 hop, 午 xung, 未 hai, 酉 pha)
    let empty = quan_he(Chi::Ty, Chi::Dan);
    assert!(empty.is_empty(), "unexpected {empty:?}");
    // tu hinh
    assert!(quan_he(Chi::Thin, Chi::Thin).contains(&ChiQuanHe::TuHinh));
    // hinh 子卯
    assert!(quan_he(Chi::Ty, Chi::Mao).contains(&ChiQuanHe::Hinh));
}

#[test]
fn tam_hop_consistent() {
    for z in Chi::ALL {
        let (a, b, phase) = tam_hop_cua(z);
        // each member returns same trine membership
        let (a2, b2, p2) = tam_hop_cua(a);
        assert_eq!(phase, p2);
        let members = [z, a, b];
        let members2 = [a, a2, b2];
        for m in members {
            assert!(members2.contains(&m) || m == a || m == b || m == z);
        }
        assert!(quan_he(z, a).contains(&ChiQuanHe::TamHop) || z == a);
        assert!(quan_he(z, b).contains(&ChiQuanHe::TamHop) || z == b);
    }
}

#[test]
fn serde_glyphs() {
    let c = Can::Giap;
    let s = serde_json::to_string(&c).unwrap();
    assert_eq!(s, "\"甲\"");
    let back: Can = serde_json::from_str(&s).unwrap();
    assert_eq!(back, c);
    let z = Chi::Ty2;
    assert_eq!(serde_json::to_string(&z).unwrap(), "\"巳\"");
    let g = giap_ty_from_can_chi(Can::Giap, Chi::Ty).unwrap();
    let gs = serde_json::to_string(&g).unwrap();
    assert_eq!(gs, "\"甲子\"");
    let gb: GiapTy = serde_json::from_str(&gs).unwrap();
    assert_eq!(gb, g);
}
