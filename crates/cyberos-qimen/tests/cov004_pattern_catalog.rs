//! COV-004 — ≥40 named patterns in catalog; ≥15 high-priority detections.

use cyberos_qimen::{
    bo_dia_ban_raw, detect_cach_cuc, dinh_cuc, pattern_catalog, sao_mon_than, truc_phu_truc_su,
    DingjuMethod, PanMethod, Stem, YinYangPan, ZhongGongKy,
};
use std::collections::HashSet;

const HIGH_PRIORITY: &[&str] = &[
    "qimen_thanh_long_hoi_dau",
    "qimen_phi_dieu_diet_huyet",
    "qimen_thanh_long_tron",
    "qimen_bach_ho_xuong_cuong",
    "qimen_chu_tuoc_dau_giang",
    "qimen_dang_xa_yeu_kieu",
    "qimen_thai_bach_nhap_huynh",
    "qimen_huynh_nhap_thai_bach",
    "qimen_dai_cach",
    "qimen_tieu_cach",
    "qimen_thanh_long_chiet_tuc",
    "qimen_thanh_long_hoa_dao",
    "qimen_bach_ho_xuat_linh",
    "qimen_chu_tuoc_vuong_mon",
    "qimen_dang_xa_van_hoa",
];

fn glyph_to_stem(g: &str) -> Stem {
    match g {
        "戊" => Stem::Mau,
        "己" => Stem::Ky,
        "庚" => Stem::Canh,
        "辛" => Stem::Tan,
        "壬" => Stem::Nham,
        "癸" => Stem::Quy,
        "丁" => Stem::Dinh,
        "丙" => Stem::Binh,
        "乙" => Stem::At,
        _ => panic!("unknown stem glyph {g}"),
    }
}

#[test]
fn catalog_has_at_least_40_named_with_citations() {
    let cat = pattern_catalog();
    assert!(
        cat.len() >= 40,
        "COV-004 requires ≥40 named patterns, got {}",
        cat.len()
    );
    for row in cat {
        assert!(!row.id.is_empty());
        assert!(!row.name.is_empty());
        assert!(!row.citations.is_empty(), "{} missing citations", row.id);
        assert!(!row.sky.is_empty() && !row.earth.is_empty());
    }
}

#[test]
fn detect_at_least_15_high_priority_on_goldens() {
    let dia = bo_dia_ban_raw(1, true);
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let mut tps = truc_phu_truc_su(&dia, 0, 0, 1, PanMethod::Zhuan, ZhongGongKy::Khon2);
    tps.xoay = 1; // avoid phuc ngam noise
    let ban = sao_mon_than(&tps, &d, YinYangPan::Duong);

    let mut found: HashSet<String> = HashSet::new();
    for id in HIGH_PRIORITY {
        let row = pattern_catalog()
            .iter()
            .find(|r| r.id == *id)
            .unwrap_or_else(|| panic!("missing high-priority pattern {id}"));
        // place sky over earth at palace 1 by overriding thien_ban[0] and finding earth palace
        let earth_p = (1u8..=9)
            .find(|p| dia.at_palace(*p) == glyph_to_stem(&row.earth))
            .expect("earth stem on dia");
        tps.thien_ban[(earth_p - 1) as usize] = glyph_to_stem(&row.sky);
        let hits = detect_cach_cuc(&ban, &dia, &tps);
        assert!(
            hits.iter().any(|h| h.id == *id && h.cung == Some(earth_p)),
            "expected detect {id} at cung {earth_p}; hits={hits:?}"
        );
        // polarity must come from catalog match, not invent
        let hit = hits.iter().find(|h| h.id == *id).unwrap();
        assert!(!hit.name.is_empty());
        assert!(hit.score.is_some());
        found.insert((*id).into());
    }
    assert!(
        found.len() >= 15,
        "COV-004 requires ≥15 high-priority detections, got {}",
        found.len()
    );
}

#[test]
fn no_polarity_without_rule_match_empty_am() {
    let dia = bo_dia_ban_raw(1, true);
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let tps = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let ban = sao_mon_than(&tps, &d, YinYangPan::Am);
    let hits = detect_cach_cuc(&ban, &dia, &tps);
    assert!(hits.is_empty(), "am lineage must not invent patterns");
}
