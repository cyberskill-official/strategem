use crate::pattern::{Pattern, Status};
use serde_json::Value;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationError {
    pub field: String,
    pub message: String,
}

impl ValidationError {
    pub fn new(field: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            field: field.into(),
            message: message.into(),
        }
    }
}

pub fn validate_pattern(v: &Value) -> Result<Pattern, Vec<ValidationError>> {
    let mut errors = Vec::new();

    let pattern: Pattern = match serde_json::from_value(v.clone()) {
        Ok(p) => p,
        Err(e) => {
            errors.push(ValidationError::new("_", e.to_string()));
            return Err(errors);
        }
    };

    if pattern.version < 1 {
        errors.push(ValidationError::new("version", "must be >= 1"));
    }
    if !(0.0..=1.0).contains(&pattern.confidence) {
        errors.push(ValidationError::new("confidence", "must be in [0.0, 1.0]"));
    }

    if let Err(e) = shallow_conditions(&pattern.conditions) {
        errors.push(e);
    }

    if pattern.status == Status::Active && pattern.citations.is_empty() {
        errors.push(ValidationError::new(
            "citations",
            "active patterns require non-empty citations",
        ));
    }

    if errors.is_empty() {
        Ok(pattern)
    } else {
        Err(errors)
    }
}

fn shallow_conditions(c: &Value) -> Result<(), ValidationError> {
    let obj = c
        .as_object()
        .ok_or_else(|| ValidationError::new("conditions", "must be a non-empty JSON object"))?;
    if obj.is_empty() {
        return Err(ValidationError::new(
            "conditions",
            "must be a non-empty JSON object",
        ));
    }
    let has_type = obj
        .get("type")
        .and_then(|t| t.as_str())
        .is_some_and(|t| matches!(t, "and" | "or" | "not"));
    let has_field = obj.contains_key("field");
    if !has_type && !has_field {
        return Err(ValidationError::new(
            "conditions",
            "must have connective type (and|or|not) or a field key",
        ));
    }
    Ok(())
}
