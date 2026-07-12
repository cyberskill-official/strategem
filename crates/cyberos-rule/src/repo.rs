//! Pattern repositories (seed + stub). FR-RULE-003.

use crate::pattern::{Pattern, Status, System};
use crate::seed::{load_seed, SeedError};
use std::path::Path;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RepoError {
    #[error("seed: {0}")]
    Seed(#[from] SeedError),
    #[error("invalid pattern: {0}")]
    Invalid(String),
}

pub trait PatternRepository {
    fn active_for(&self, system: System) -> Result<Vec<Pattern>, RepoError>;
}

pub struct SeedRepository {
    patterns: Vec<Pattern>,
}

impl SeedRepository {
    pub fn load(dir: impl AsRef<Path>) -> Result<Self, RepoError> {
        Ok(Self {
            patterns: load_seed(dir)?,
        })
    }

    pub fn from_patterns(patterns: Vec<Pattern>) -> Self {
        Self { patterns }
    }
}

impl PatternRepository for SeedRepository {
    fn active_for(&self, system: System) -> Result<Vec<Pattern>, RepoError> {
        Ok(self
            .patterns
            .iter()
            .filter(|p| p.status == Status::Active)
            .filter(|p| p.system == system || p.system == System::All)
            .cloned()
            .collect())
    }
}

/// Stub holding the same rows a Postgres table would return.
pub struct StubPgRepository {
    patterns: Vec<Pattern>,
}

impl StubPgRepository {
    pub fn new(patterns: Vec<Pattern>) -> Self {
        Self { patterns }
    }
}

impl PatternRepository for StubPgRepository {
    fn active_for(&self, system: System) -> Result<Vec<Pattern>, RepoError> {
        for p in &self.patterns {
            if p.version < 1 {
                return Err(RepoError::Invalid(format!("bad version for {}", p.id)));
            }
        }
        SeedRepository::from_patterns(self.patterns.clone()).active_for(system)
    }
}
