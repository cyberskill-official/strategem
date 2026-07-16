//! Deterministic condition evaluation. TASK-RULE-002.

use crate::dsl::{Cond, Op};
use crate::path::get_path;
use serde_json::Value;

pub fn evaluate(cond: &Cond, chart: &Value) -> bool {
    match cond {
        Cond::And(xs) => xs.iter().all(|c| evaluate(c, chart)),
        Cond::Or(xs) => xs.iter().any(|c| evaluate(c, chart)),
        Cond::Not(c) => !evaluate(c, chart),
        Cond::Leaf { field, op, value } => eval_leaf(field, op, value.as_ref(), chart),
    }
}

fn eval_leaf(field: &str, op: &Op, value: Option<&Value>, chart: &Value) -> bool {
    let got = get_path(chart, field);
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
