//! Cross-system ChartSet + qualified paths — FR-RULE-004.

use crate::dsl::{Cond, Op};
use crate::path::get_path;
use serde_json::Value;
use std::collections::BTreeMap;

/// System he keys used as path qualifiers.
pub const HE_KEYS: &[&str] = &["ky_mon", "luc_nham", "thai_at"];

#[derive(Debug, Clone)]
pub struct ChartSet {
    pub charts: BTreeMap<String, Value>,
    pub primary: String,
}

impl ChartSet {
    pub fn single(he: impl Into<String>, la_so: Value) -> Self {
        let he = he.into();
        let mut charts = BTreeMap::new();
        charts.insert(he.clone(), la_so);
        Self {
            charts,
            primary: he,
        }
    }

    pub fn get(&self, he: &str) -> Option<&Value> {
        self.charts.get(he)
    }
}

/// Split optional `<he>:` qualifier from a path.
/// Returns (Some(he), rest) or (None, full_path).
pub fn split_he_qualifier(path: &str) -> Result<(Option<String>, &str), String> {
    if let Some((head, rest)) = path.split_once(':') {
        if HE_KEYS.contains(&head) {
            return Ok((Some(head.to_string()), rest));
        }
        // unknown qualifier that looks like he: is an error if head has no dots
        if !head.contains('.') && head.chars().all(|c| c.is_ascii_alphanumeric() || c == '_') {
            return Err(format!("unknown he qualifier: {head}"));
        }
    }
    Ok((None, path))
}

/// Resolve a (possibly qualified) path against a chart set.
/// Absent chart or field → None (leaf evaluates to false / exists test).
pub fn resolve_in_set<'a>(path: &str, set: &'a ChartSet) -> Option<&'a Value> {
    let (he, rest) = split_he_qualifier(path).ok()?;
    let chart = match he {
        Some(h) => set.get(&h)?,
        None => set.get(&set.primary)?,
    };
    get_path(chart, rest)
}

/// Evaluate a condition tree over a chart set. Total and pure.
pub fn evaluate_set(cond: &Cond, set: &ChartSet) -> bool {
    match cond {
        Cond::And(xs) => xs.iter().all(|c| evaluate_set(c, set)),
        Cond::Or(xs) => xs.iter().any(|c| evaluate_set(c, set)),
        Cond::Not(c) => !evaluate_set(c, set),
        Cond::Leaf { field, op, value } => eval_leaf_set(field, op, value.as_ref(), set),
    }
}

fn eval_leaf_set(field: &str, op: &Op, value: Option<&Value>, set: &ChartSet) -> bool {
    // invalid qualifier → defined false (total evaluator, no panic)
    if split_he_qualifier(field).is_err() {
        return false;
    }
    let got = resolve_in_set(field, set);
    if op == &Op::Exists {
        return got.is_some() && !got.unwrap().is_null();
    }
    let Some(got) = got else {
        return false;
    };
    let Some(want) = value else {
        return false;
    };
    match op {
        Op::Eq => got == want,
        Op::In => want
            .as_array()
            .map(|a| a.iter().any(|x| x == got))
            .unwrap_or(false),
        Op::Contains => match (got, want) {
            (Value::String(s), Value::String(sub)) => s.contains(sub.as_str()),
            (Value::Array(a), v) => a.iter().any(|x| x == v),
            _ => false,
        },
        Op::Gte => cmp_ord(got, want).is_some_and(|o| o != std::cmp::Ordering::Less),
        Op::Lte => cmp_ord(got, want).is_some_and(|o| o != std::cmp::Ordering::Greater),
        Op::Exists => unreachable!(),
    }
}

fn cmp_ord(a: &Value, b: &Value) -> Option<std::cmp::Ordering> {
    match (a, b) {
        (Value::Number(x), Value::Number(y)) => {
            let xf = x.as_f64()?;
            let yf = y.as_f64()?;
            xf.partial_cmp(&yf)
        }
        (Value::String(x), Value::String(y)) => Some(x.cmp(y)),
        _ => None,
    }
}

#[cfg(test)]
mod unit {
    use super::*;
    use serde_json::json;

    #[test]
    fn split_ok() {
        let (h, r) = split_he_qualifier("ky_mon:cach_cuc").unwrap();
        assert_eq!(h.as_deref(), Some("ky_mon"));
        assert_eq!(r, "cach_cuc");
        let (h2, r2) = split_he_qualifier("ban.door").unwrap();
        assert!(h2.is_none());
        assert_eq!(r2, "ban.door");
    }
}
