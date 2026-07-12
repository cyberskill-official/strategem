use crate::pattern::Pattern;
use crate::validate::validate_pattern;
use std::fs;
use std::path::Path;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum SeedError {
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("json: {0}")]
    Json(#[from] serde_json::Error),
    #[error("validation failed for pattern id={id}: {detail}")]
    Validation { id: String, detail: String },
}

pub fn load_seed(dir: impl AsRef<Path>) -> Result<Vec<Pattern>, SeedError> {
    let dir = dir.as_ref();
    let mut all = Vec::new();
    let mut files: Vec<_> = fs::read_dir(dir)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "json"))
        .collect();
    files.sort();
    for path in files {
        let text = fs::read_to_string(&path)?;
        let rows: Vec<serde_json::Value> = serde_json::from_str(&text)?;
        for row in rows {
            let id = row
                .get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("<missing>")
                .to_string();
            match validate_pattern(&row) {
                Ok(p) => all.push(p),
                Err(errs) => {
                    let detail = errs
                        .iter()
                        .map(|e| format!("{}: {}", e.field, e.message))
                        .collect::<Vec<_>>()
                        .join("; ");
                    return Err(SeedError::Validation { id, detail });
                }
            }
        }
    }
    Ok(all)
}
