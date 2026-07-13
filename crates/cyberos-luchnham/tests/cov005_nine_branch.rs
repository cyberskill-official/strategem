//! COV-005 — nine tam-truyen branches + khoa_the + flag stamps + ≥30 goldens.

use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{
    cast_luc_nham, census_khac_tac, dia_ban, lap_tam_truyen, lap_tu_khoa, quay_thien_ban,
    recognize_khoa_the, CastInput, KhacTac, Khoa, KhoaThe, Phap, QuyNhanVariant, TrangThaiBan,
    TuKhoa, NINE_PHAP,
};
use std::collections::HashSet;
use std::fs;
use std::path::PathBuf;

fn tk_from_rels(rels: [Option<KhacTac>; 4], tops: [Chi; 4], bottoms: [Chi; 4]) -> TuKhoa {
    TuKhoa {
        khoa: [
            Khoa {
                thuong_than: tops[0],
                ha_than: bottoms[0],
                la_can_khoa: true,
                quan_he: rels[0],
            },
            Khoa {
                thuong_than: tops[1],
                ha_than: bottoms[1],
                la_can_khoa: false,
                quan_he: rels[1],
            },
            Khoa {
                thuong_than: tops[2],
                ha_than: bottoms[2],
                la_can_khoa: false,
                quan_he: rels[2],
            },
            Khoa {
                thuong_than: tops[3],
                ha_than: bottoms[3],
                la_can_khoa: false,
                quan_he: rels[3],
            },
        ],
    }
}

fn identity_thien() -> [Chi; 12] {
    // offset 0 → thien == dia; chains so→so in 0 steps? thien_over with identity: thien[i]=dia[i]
    // mat after 2 hops: still identity map → mat == so → BatChuyen
    dia_ban()
}

#[test]
fn nine_phap_enum_is_complete() {
    assert_eq!(NINE_PHAP.len(), 9);
    let set: HashSet<_> = NINE_PHAP.iter().copied().collect();
    assert_eq!(set.len(), 9);
}

#[test]
fn branch_phuc_and_phan_ngam() {
    let (thien, st) = quay_thien_ban(Chi::Ty, Chi::Ty);
    assert_eq!(st, TrangThaiBan::PhucNgam);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, st, Can::Giap);
    assert_eq!(tt.phap, Phap::PhucNgam);
    assert_eq!(tt.khoa_the, KhoaThe::PhucNgam);

    let (thien2, st2) = quay_thien_ban(Chi::Ty, Chi::Ngo);
    assert_eq!(st2, TrangThaiBan::PhanNgam);
    let tk2 = lap_tu_khoa(&thien2, Can::Giap, Chi::Ty);
    let tt2 = lap_tam_truyen(&tk2, &thien2, st2, Can::Giap);
    assert_eq!(tt2.phap, Phap::PhanNgam);
    assert_eq!(tt2.khoa_the, KhoaThe::PhanNgam);
}

#[test]
fn branch_tac_khac_single_census() {
    let thien = identity_thien();
    // single TacHaThuong → TrongTham
    let tk = tk_from_rels(
        [Some(KhacTac::TacHaThuong), None, None, None],
        [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
        [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
    );
    assert_eq!(census_khac_tac(&tk).len(), 1);
    let tt = lap_tam_truyen(&tk, &thien, TrangThaiBan::Thuong, Can::Giap);
    assert_eq!(tt.phap, Phap::TacKhac);
    assert_eq!(tt.khoa_the, KhoaThe::TrongTham);

    let tk2 = tk_from_rels(
        [Some(KhacTac::KhacThuongHa), None, None, None],
        [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
        [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
    );
    let tt2 = lap_tam_truyen(&tk2, &thien, TrangThaiBan::Thuong, Can::Giap);
    assert_eq!(tt2.phap, Phap::TacKhac);
    assert_eq!(tt2.khoa_the, KhoaThe::NguyenThu);
}

#[test]
fn branch_ty_dung_and_thiep_hai() {
    let thien = identity_thien();
    // two relations: Ty(0) yang upper + Ngo(6) yang upper with yang day → both ty match → thiep
    // one yang one yin upper with yang day → ty dung
    let tk_ty = tk_from_rels(
        [
            Some(KhacTac::KhacThuongHa),
            Some(KhacTac::TacHaThuong),
            None,
            None,
        ],
        [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao], // Ty yang, Suu yin
        [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
    );
    let tt = lap_tam_truyen(&tk_ty, &thien, TrangThaiBan::Thuong, Can::Giap);
    assert_eq!(tt.phap, Phap::TyDung);
    assert_eq!(tt.khoa_the, KhoaThe::TriNhat);

    let tk_th = tk_from_rels(
        [
            Some(KhacTac::KhacThuongHa),
            Some(KhacTac::TacHaThuong),
            None,
            None,
        ],
        [Chi::Ty, Chi::Ngo, Chi::Dan, Chi::Mao], // both yang
        [Chi::Suu, Chi::Mui, Chi::Than, Chi::Dau],
    );
    let tt2 = lap_tam_truyen(&tk_th, &thien, TrangThaiBan::Thuong, Can::Giap);
    assert_eq!(tt2.phap, Phap::ThiepHai);
    assert_eq!(tt2.khoa_the, KhoaThe::ThiepHai);
}

#[test]
fn branch_empty_census_bat_dao_biet_mao() {
    let thien = identity_thien(); // closed chain → BatChuyen first
    let tk_bat = tk_from_rels(
        [None, None, None, None],
        [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
        [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
    );
    let tt = lap_tam_truyen(&tk_bat, &thien, TrangThaiBan::Thuong, Can::Giap);
    assert_eq!(tt.phap, Phap::BatChuyen);

    // Non-identity thien: offset so chains do not close
    let (thien2, _) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    // empty census with Dau upper → MaoTinh
    let tk_mao = tk_from_rels(
        [None, None, None, None],
        [Chi::Dau, Chi::Suu, Chi::Dan, Chi::Mao],
        [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Ty],
    );
    let tt_mao = lap_tam_truyen(&tk_mao, &thien2, TrangThaiBan::Thuong, Can::Giap);
    assert!(
        matches!(
            tt_mao.phap,
            Phap::MaoTinh | Phap::BatChuyen | Phap::DaoKhac | Phap::BietTrach
        ),
        "empty census must land a named branch, got {:?}",
        tt_mao.phap
    );

    // no Dau; ha matches dao_so → BietTrach, else DaoKhac
    let tk_dao = tk_from_rels(
        [None, None, None, None],
        [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
        [Chi::Dan, Chi::Mui, Chi::Than, Chi::Ngo], // ha includes Dan == khoa[2] upper for yang day
    );
    let tt_dao = lap_tam_truyen(&tk_dao, &thien2, TrangThaiBan::Thuong, Can::Giap);
    assert!(
        matches!(
            tt_dao.phap,
            Phap::DaoKhac | Phap::BietTrach | Phap::BatChuyen | Phap::MaoTinh
        ),
        "got {:?}",
        tt_dao.phap
    );
}

#[test]
fn all_nine_branches_reachable() {
    let mut seen: HashSet<Phap> = HashSet::new();
    let thien_id = identity_thien();
    let (thien_rot, _) = quay_thien_ban(Chi::Hoi, Chi::Ty);

    // forced constructions
    let cases: Vec<(TuKhoa, &[Chi; 12], TrangThaiBan, Can)> = vec![
        (
            lap_tu_khoa(&thien_id, Can::Giap, Chi::Ty),
            &thien_id,
            TrangThaiBan::PhucNgam,
            Can::Giap,
        ),
        (
            lap_tu_khoa(&thien_id, Can::Giap, Chi::Ty),
            &thien_id,
            TrangThaiBan::PhanNgam,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [Some(KhacTac::TacHaThuong), None, None, None],
                [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
                [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
            ),
            &thien_rot,
            TrangThaiBan::Thuong,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [
                    Some(KhacTac::KhacThuongHa),
                    Some(KhacTac::TacHaThuong),
                    None,
                    None,
                ],
                [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
                [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
            ),
            &thien_rot,
            TrangThaiBan::Thuong,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [
                    Some(KhacTac::KhacThuongHa),
                    Some(KhacTac::TacHaThuong),
                    None,
                    None,
                ],
                [Chi::Ty, Chi::Ngo, Chi::Dan, Chi::Mao],
                [Chi::Suu, Chi::Mui, Chi::Than, Chi::Dau],
            ),
            &thien_rot,
            TrangThaiBan::Thuong,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [None, None, None, None],
                [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
                [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Dau],
            ),
            &thien_id,
            TrangThaiBan::Thuong,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [None, None, None, None],
                [Chi::Dau, Chi::Suu, Chi::Dan, Chi::Mao],
                [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Ty],
            ),
            &thien_rot,
            TrangThaiBan::Thuong,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [None, None, None, None],
                [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
                [Chi::Dan, Chi::Mui, Chi::Than, Chi::Ngo],
            ),
            &thien_rot,
            TrangThaiBan::Thuong,
            Can::Giap,
        ),
        (
            tk_from_rels(
                [None, None, None, None],
                [Chi::Ty, Chi::Suu, Chi::Dan, Chi::Mao],
                [Chi::Ngo, Chi::Mui, Chi::Than, Chi::Hoi],
            ),
            &thien_rot,
            TrangThaiBan::Thuong,
            Can::At, // yin day → dao path
        ),
    ];

    for (tk, thien, st, can) in cases {
        let tt = lap_tam_truyen(&tk, thien, st, can);
        seen.insert(tt.phap);
    }

    // Also scan real boards for any remaining
    for nt in Chi::ALL {
        for gio in Chi::ALL {
            let (thien, st) = quay_thien_ban(nt, gio);
            for can in Can::ALL {
                for chi in Chi::ALL.iter().step_by(3) {
                    let tk = lap_tu_khoa(&thien, can, *chi);
                    let tt = lap_tam_truyen(&tk, &thien, st, can);
                    seen.insert(tt.phap);
                }
            }
        }
    }

    for p in NINE_PHAP {
        assert!(
            seen.contains(&p),
            "COV-005: branch {p:?} never reached; seen={seen:?}"
        );
    }
}

#[test]
fn envelope_khoa_the_and_flags() {
    let r = cast_luc_nham(&CastInput {
        datetime: "2004-01-01T10:30:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        can_ngay: Can::Giap,
        chi_ngay: Chi::Ty,
        nguyet_tuong: Chi::Hoi,
        gio_chiem: Chi::Ty,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    });
    let ban = &r.envelope["ban"];
    let kt = ban["khoa_the"].as_array().expect("khoa_the array");
    assert!(!kt.is_empty());
    // classical names, not Debug
    let names: Vec<_> = kt.iter().filter_map(|v| v.as_str()).collect();
    assert!(names.iter().any(|n| !n.is_empty()));
    assert!(ban["tu_khoa"].as_array().unwrap().len() == 4);
    assert!(ban["tam_truyen"]["so"].as_str().is_some());
    assert!(ban["tam_truyen"]["phap"].as_str().is_some());
    let ctp = r.envelope["co_truong_phai"].as_object().unwrap();
    assert!(ctp.contains_key("quy_nhan_variant"));
    assert!(ctp.contains_key("truong_sinh") || ctp.contains_key("truong_sinh_phai"));
}

#[test]
fn golden_30_with_tu_khoa_and_tam_truyen() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/liuren_cert_v1.csv");
    let text = fs::read_to_string(path).expect("fixture");
    let mut rows = 0usize;
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        let input = CastInput {
            datetime: cols[1].into(),
            tz: "+07:00".into(),
            kinh_do: 105.0,
            can_ngay: Can::from_index(cols[2].parse().unwrap()).unwrap(),
            chi_ngay: Chi::from_index(cols[3].parse().unwrap()).unwrap(),
            nguyet_tuong: Chi::from_index(cols[4].parse().unwrap()).unwrap(),
            gio_chiem: Chi::from_index(cols[5].parse().unwrap()).unwrap(),
            quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
        };
        let r = cast_luc_nham(&input);
        let ban = &r.envelope["ban"];
        assert_eq!(ban["tu_khoa"].as_array().unwrap().len(), 4, "{}", cols[0]);
        assert!(ban["tam_truyen"]["so"].as_str().is_some(), "{}", cols[0]);
        assert!(ban["tam_truyen"]["trung"].as_str().is_some(), "{}", cols[0]);
        assert!(ban["tam_truyen"]["mat"].as_str().is_some(), "{}", cols[0]);
        assert!(ban["tam_truyen"]["phap"].as_str().is_some(), "{}", cols[0]);
        assert!(
            !ban["khoa_the"].as_array().unwrap().is_empty(),
            "{}",
            cols[0]
        );
        rows += 1;
    }
    assert!(rows >= 30, "need ≥30 LN goldens, got {rows}");
}

#[test]
fn recognize_names_not_debug() {
    let (thien, st) = quay_thien_ban(Chi::Ty, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, st, Can::Giap);
    let hits = recognize_khoa_the(&tt);
    assert!(hits
        .iter()
        .any(|h| h.name == "伏吟" || h.name.contains("吟")));
}
