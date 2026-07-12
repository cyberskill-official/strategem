//! Condition DSL AST. FR-RULE-002.

use serde_json::Value;
use thiserror::Error;

#[derive(Debug, Clone, PartialEq)]
pub enum Op {
    Eq,
    In,
    Gte,
    Lte,
    Exists,
    Contains,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Cond {
    And(Vec<Cond>),
    Or(Vec<Cond>),
    Not(Box<Cond>),
    Leaf {
        field: String,
        op: Op,
        value: Option<Value>,
    },
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum DslError {
    #[error("invalid condition: {0}")]
    Invalid(String),
}

impl Cond {
    pub fn from_json(v: &Value) -> Result<Self, DslError> {
        let obj = v
            .as_object()
            .ok_or_else(|| DslError::Invalid("must be object".into()))?;
        if let Some(t) = obj.get("type").and_then(|x| x.as_str()) {
            match t {
                "and" | "or" => {
                    let rules = obj
                        .get("rules")
                        .and_then(|r| r.as_array())
                        .ok_or_else(|| DslError::Invalid("rules array required".into()))?;
                    if t == "and" && rules.is_empty() {
                        return Err(DslError::Invalid("empty and".into()));
                    }
                    let mut kids = Vec::new();
                    for r in rules {
                        kids.push(Cond::from_json(r)?);
                    }
                    return Ok(if t == "and" {
                        Cond::And(kids)
                    } else {
                        Cond::Or(kids)
                    });
                }
                "not" => {
                    let inner = obj
                        .get("rule")
                        .or_else(|| obj.get("rules").and_then(|r| r.as_array()?.first()))
                        .ok_or_else(|| DslError::Invalid("not needs rule".into()))?;
                    return Ok(Cond::Not(Box::new(Cond::from_json(inner)?)));
                }
                _ => return Err(DslError::Invalid(format!("unknown type {t}"))),
            }
        }
        if let Some(field) = obj.get("field").and_then(|f| f.as_str()) {
            let op_s = obj
                .get("operator")
                .or_else(|| obj.get("op"))
                .and_then(|o| o.as_str())
                .unwrap_or("eq");
            let op = match op_s {
                "eq" => Op::Eq,
                "in" => Op::In,
                "gte" => Op::Gte,
                "lte" => Op::Lte,
                "exists" => Op::Exists,
                "contains" => Op::Contains,
                other => return Err(DslError::Invalid(format!("unknown operator {other}"))),
            };
            return Ok(Cond::Leaf {
                field: field.to_string(),
                op,
                value: obj.get("value").cloned(),
            });
        }
        Err(DslError::Invalid("need type or field".into()))
    }
}
