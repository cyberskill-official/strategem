use cyberos_rule::{evaluate, score_match, Cond, Pattern, Polarity, Status, System};
use serde_json::json;

fn chart() -> serde_json::Value {
    json!({
        "he": "ky_mon",
        "score": 0.8,
        "tags": ["a", "b"],
        "name": "hello world",
        "ban": { "star": "thanh_long" }
    })
}

#[test]
fn parse_and_reject() {
    let ok = Cond::from_json(&json!({
        "type": "and",
        "rules": [{ "field": "he", "operator": "eq", "value": "ky_mon" }]
    }))
    .unwrap();
    assert!(matches!(ok, Cond::And(_)));
    assert!(Cond::from_json(&json!({"type":"and","rules":[]})).is_err());
    assert!(Cond::from_json(&json!({"field":"x","operator":"nope","value":1})).is_err());
    assert!(Cond::from_json(&json!({"foo":1})).is_err());
}

#[test]
fn operators_truth_table() {
    let c = chart();
    let eq = Cond::from_json(&json!({"field":"he","operator":"eq","value":"ky_mon"})).unwrap();
    assert!(evaluate(&eq, &c));
    let inn =
        Cond::from_json(&json!({"field":"he","operator":"in","value":["ky_mon","x"]})).unwrap();
    assert!(evaluate(&inn, &c));
    let gte = Cond::from_json(&json!({"field":"score","operator":"gte","value":0.5})).unwrap();
    assert!(evaluate(&gte, &c));
    let lte = Cond::from_json(&json!({"field":"score","operator":"lte","value":0.9})).unwrap();
    assert!(evaluate(&lte, &c));
    let exists = Cond::from_json(&json!({"field":"ban.star","operator":"exists"})).unwrap();
    assert!(evaluate(&exists, &c));
    let contains =
        Cond::from_json(&json!({"field":"name","operator":"contains","value":"hello"})).unwrap();
    assert!(evaluate(&contains, &c));
    let contains_arr =
        Cond::from_json(&json!({"field":"tags","operator":"contains","value":"a"})).unwrap();
    assert!(evaluate(&contains_arr, &c));
    let missing = Cond::from_json(&json!({"field":"nope","operator":"eq","value":1})).unwrap();
    assert!(!evaluate(&missing, &c));
    let miss_exists = Cond::from_json(&json!({"field":"nope","operator":"exists"})).unwrap();
    assert!(!evaluate(&miss_exists, &c));
    let nested = Cond::from_json(&json!({
        "type": "not",
        "rule": {
            "type": "or",
            "rules": [
                {"field":"he","operator":"eq","value":"luc_nham"},
                {"field":"score","operator":"gte","value":0.99}
            ]
        }
    }))
    .unwrap();
    assert!(evaluate(&nested, &c));
    // type mismatch gte
    let bad = Cond::from_json(&json!({"field":"he","operator":"gte","value":1})).unwrap();
    assert!(!evaluate(&bad, &c));
}

#[test]
fn score_match_and_determinism() {
    let p = Pattern {
        id: "p1".into(),
        system: System::Qimen,
        name: "Test".into(),
        name_han: None,
        conditions: json!({"field":"he","operator":"eq","value":"ky_mon"}),
        polarity: Polarity::Cat,
        meaning_classical: "c".into(),
        meaning_modern: "m".into(),
        citations: vec!["cite".into()],
        version: 1,
        confidence: 0.9,
        status: Status::Active,
    };
    let c = chart();
    let a = score_match(&p, &c).unwrap();
    assert_eq!(a.score, Some(0.9));
    assert_eq!(a.citations, vec!["cite"]);
    for _ in 0..1000 {
        assert_eq!(score_match(&p, &c), Some(a.clone()));
    }
    let p2 = Pattern {
        conditions: json!({"field":"he","operator":"eq","value":"nope"}),
        ..p
    };
    assert!(score_match(&p2, &c).is_none());
}
