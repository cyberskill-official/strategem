//! External oracle certification helpers (Wave W4).
//!
//! Loads CSV/JSON dumps from the workspace `oracle/` tree. Full dumps are
//! optional: when absent, callers MUST skip with an honest message rather than
//! inventing expected values or relabeling self-oracle goldens as kin*.

use std::fs;
use std::path::{Path, PathBuf};

/// Oracle dataset class under `oracle/<source>/{sample,full}/`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DatasetKind {
    /// Committed hand-verifiable classical rows — prove the harness, not full cert.
    Sample,
    /// Operator-supplied kin*/sxwnl dumps — gate when present, skip when absent.
    Full,
}

impl DatasetKind {
    pub fn dir_name(self) -> &'static str {
        match self {
            DatasetKind::Sample => "sample",
            DatasetKind::Full => "full",
        }
    }
}

/// Result of attempting to load an external dataset file.
#[derive(Debug)]
pub enum LoadOutcome {
    Ready {
        path: PathBuf,
        text: String,
        row_count: usize,
    },
    Absent {
        path: PathBuf,
        message: String,
    },
}

/// Workspace `oracle/` root (sibling of `crates/`).
pub fn workspace_oracle_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../oracle")
}

/// `oracle/<source>/<sample|full>/<file>`.
pub fn dataset_path(source: &str, kind: DatasetKind, file: &str) -> PathBuf {
    workspace_oracle_root()
        .join(source)
        .join(kind.dir_name())
        .join(file)
}

/// True when a path exists and contains at least one non-comment data line.
pub fn has_data_rows(path: &Path) -> bool {
    match fs::read_to_string(path) {
        Ok(text) => data_lines(&text).next().is_some(),
        Err(_) => false,
    }
}

/// Load CSV text if the file exists and has data rows; otherwise return Absent.
pub fn load_csv(path: &Path, source_label: &str) -> LoadOutcome {
    if !path.exists() {
        return LoadOutcome::Absent {
            path: path.to_path_buf(),
            message: skip_message(source_label, path, "file not present"),
        };
    }
    let text = match fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) => {
            return LoadOutcome::Absent {
                path: path.to_path_buf(),
                message: skip_message(source_label, path, &format!("unreadable: {e}")),
            };
        }
    };
    let row_count = data_lines(&text).count();
    if row_count == 0 {
        return LoadOutcome::Absent {
            path: path.to_path_buf(),
            message: skip_message(
                source_label,
                path,
                "file present but empty (no data rows; README placeholders only)",
            ),
        };
    }
    LoadOutcome::Ready {
        path: path.to_path_buf(),
        text,
        row_count,
    }
}

/// Non-empty lines that are not `#` comments and not a header row starting with
/// a known metadata key. Header detection: first non-comment line is treated as
/// header when it contains no digit-only field in column 0 / looks like names.
///
/// Callers that need the header should use [`csv_rows`] which skips the first
/// non-comment line when it looks like a header (contains letters and no
/// leading `#`).
pub fn data_lines(text: &str) -> impl Iterator<Item = &str> {
    text.lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
}

/// Yield `(line_no, columns)` for every data row after an optional CSV header.
///
/// The first non-comment line is treated as a header when it does **not** start
/// with a digit (id / numeric key). Comment lines are ignored.
pub fn csv_rows(text: &str) -> Vec<(usize, Vec<&str>)> {
    let mut out = Vec::new();
    let mut saw_header = false;
    for (idx, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let cols: Vec<&str> = line.split(',').map(str::trim).collect();
        if !saw_header {
            saw_header = true;
            let first = cols.first().copied().unwrap_or("");
            let looks_like_header = first.chars().any(|c| c.is_ascii_alphabetic())
                && !first.chars().next().is_some_and(|c| c.is_ascii_digit());
            if looks_like_header {
                continue;
            }
        }
        out.push((idx + 1, cols));
    }
    out
}

/// Honest skip banner for CI logs.
pub fn skip_message(source_label: &str, path: &Path, detail: &str) -> String {
    format!(
        "SKIP external oracle certification [{source_label}]: {detail}. \
         Expected dump at {}. Drop a real kin*/sxwnl dump there to enable the gate. \
         Self-oracle regression fixtures are NOT a substitute.",
        path.display()
    )
}

/// Require a committed sample dataset (always present in a healthy checkout).
pub fn require_sample(source: &str, file: &str) -> (PathBuf, String) {
    let path = dataset_path(source, DatasetKind::Sample, file);
    match load_csv(&path, &format!("{source} sample")) {
        LoadOutcome::Ready { path, text, .. } => (path, text),
        LoadOutcome::Absent { path, message } => {
            panic!(
                "committed sample fixture missing at {}: {message}",
                path.display()
            );
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn workspace_oracle_root_exists() {
        let root = workspace_oracle_root();
        assert!(
            root.join("README.md").exists(),
            "oracle/README.md must exist at {}",
            root.display()
        );
    }

    #[test]
    fn csv_rows_skips_comments_and_header() {
        let text = "# comment\nid,a,b\n1,x,y\n# skip\n2,p,q\n";
        let rows = csv_rows(text);
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0].1[0], "1");
        assert_eq!(rows[1].1[0], "2");
    }
}
