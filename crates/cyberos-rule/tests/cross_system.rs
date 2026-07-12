//! FR-RULE-004 cross-system evaluation tests.

use cyberos_rule::{evaluate, evaluate_set, resolve_in_set, score_set, ChartSet, Cond, Pattern};
use serde_json::json;

#[test]
fn single_chart_parity() {
    let chart = json!({"he": "ky_mon", "ban": {"door": "Khai"}});
    let set = ChartSet::single("ky_mon", chart.clone());
    let cond =
        Cond::from_json(&json!({"field": "ban.door", "operator": "eq", "value": "Khai"})).unwrap();
    assert_eq!(evaluate(&cond, &chart), evaluate_set(&cond, &set));
}

#[test]
fn qualified_path_two_charts() {
    let mut set = ChartSet {
        charts: Default::default(),
        primary: "ky_mon".into(),
    };
    set.charts.insert(
        "ky_mon".into(),
        json!({"cach_cuc": ["青龍返首"], "ban": {}}),
    );
    set.charts
        .insert("luc_nham".into(), json!({"tam_truyen": [{"than": "六合"}]}));
    let cond = Cond::from_json(&json!({
        "type": "and",
        "weight": 1.5,
        "rules": [
            {"field": "ky_mon:cach_cuc", "operator": "contains", "value": "青龍返首"},
            {"field": "luc_nham:tam_truyen.0.than", "operator": "in", "value": ["六合", "青龍"]}
        ]
    }))
    .unwrap();
    assert!(evaluate_set(&cond, &set));
    // missing chart → false, no panic
    let only_qm = ChartSet::single("ky_mon", set.charts["ky_mon"].clone());
    assert!(!evaluate_set(&cond, &only_qm));
}

#[test]
fn resolve_absent_is_none() {
    let set = ChartSet::single("ky_mon", json!({"ban": {}}));
    assert!(resolve_in_set("luc_nham:tam_truyen.0.than", &set).is_none());
    assert!(resolve_in_set("ky_mon:missing.path", &set).is_none());
}

#[test]
fn score_set_emits_cach_cuc() {
    let set = ChartSet::single("ky_mon", json!({"he": "ky_mon", "x": 1}));
    let p = Pattern {
        id: "cross_agree".into(),
        name: "agree".into(),
        name_han: None,
        system: cyberos_rule::System::All,
        conditions: json!({"field": "he", "operator": "eq", "value": "ky_mon", "weight": 2.0}),
        polarity: cyberos_rule::Polarity::Cat,
        confidence: 0.5,
        citations: vec!["c1".into()],
        status: cyberos_rule::Status::Active,
        version: 1,
        meaning_classical: "classical".into(),
        meaning_modern: "modern".into(),
    };
    let cc = score_set(&p, &set).expect("match");
    assert_eq!(cc.id, "cross_agree");
    assert!((cc.score.unwrap() - 1.0).abs() < 1e-5); // 0.5 * 2.0
}

#[test]
fn fixture_qimen_liuren_file() {
    let raw = include_str!("fixtures/chart_set_qimen_liuren.json");
    let v: serde_json::Value = serde_json::from_str(raw).unwrap();
    let mut set = ChartSet {
        charts: Default::default(),
        primary: "ky_mon".into(),
    };
    set.charts.insert("ky_mon".into(), v["ky_mon"].clone());
    set.charts.insert("luc_nham".into(), v["luc_nham"].clone());
    let cond = Cond::from_json(&v["condition"]).unwrap();
    assert!(evaluate_set(&cond, &set));
}
