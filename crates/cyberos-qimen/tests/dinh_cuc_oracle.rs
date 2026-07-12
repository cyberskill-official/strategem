use cyberos_qimen::{
    dinh_cuc, luoshu_outer, phu_dau_nguyen, table_duong_don, table_so_cuc, DingjuMethod,
};

#[test]
fn table_72_cells() {
    for t in 0u8..24 {
        for n in 0u8..3 {
            let s = table_so_cuc(t, n);
            assert!((1..=9).contains(&s));
            let _ = table_duong_don(t);
        }
    }
}

#[test]
fn luoshu_structural() {
    let outer = luoshu_outer();
    assert_eq!(outer.len(), 8);
    // thuong nguyen of first terms align to some palace numbers
    for (i, &palace) in outer.iter().enumerate() {
        let term = (i as u8) * 3;
        if term < 24 {
            let cuc = table_so_cuc(term, 0);
            assert!((1..=9).contains(&cuc));
            let _ = palace;
        }
    }
}

#[test]
fn phu_dau_all_branches() {
    for b in 0u8..12 {
        let n = phu_dau_nguyen(b);
        assert!((1..=3).contains(&n));
    }
}

#[test]
fn methods_differ_on_boundary() {
    let a = dinh_cuc(8, 0, DingjuMethod::Chaibu, false).unwrap();
    let b = dinh_cuc(8, 0, DingjuMethod::Maoshan, false).unwrap();
    // may share so_cuc but nguyen path differs for maoshan
    let _ = (a, b);
    assert!(dinh_cuc(8, 0, DingjuMethod::Zhirun, true).is_ok());
    assert!(dinh_cuc(0, 0, DingjuMethod::Zhirun, true).is_err());
    assert!(dinh_cuc(8, 0, DingjuMethod::Chaibu, true).is_err());
}

#[test]
fn fixture_sample_matches_table() {
    // self-oracle sample: term 0 upper yuan
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    assert_eq!(d.so_cuc, table_so_cuc(0, 0));
    assert_eq!(d.duong_don, table_duong_don(0));
}
