//! In-memory pattern cache. TASK-RULE-003.

use crate::pattern::{Pattern, System};
use crate::repo::{PatternRepository, RepoError};
use std::collections::HashMap;
use std::sync::Mutex;

pub struct PatternCache<R: PatternRepository> {
    repo: R,
    cache: Mutex<HashMap<String, Vec<Pattern>>>,
    reads: Mutex<u32>,
}

impl<R: PatternRepository> PatternCache<R> {
    pub fn new(repo: R) -> Self {
        Self {
            repo,
            cache: Mutex::new(HashMap::new()),
            reads: Mutex::new(0),
        }
    }

    pub fn warm(&self, system: System) -> Result<(), RepoError> {
        let _ = self.active_for(system)?;
        Ok(())
    }

    pub fn active_for(&self, system: System) -> Result<Vec<Pattern>, RepoError> {
        let key = format!("{system:?}");
        {
            let guard = self.cache.lock().unwrap();
            if let Some(v) = guard.get(&key) {
                return Ok(v.clone());
            }
        }
        *self.reads.lock().unwrap() += 1;
        let rows = self.repo.active_for(system)?;
        self.cache.lock().unwrap().insert(key, rows.clone());
        Ok(rows)
    }

    pub fn invalidate(&self, system: System) {
        self.cache.lock().unwrap().remove(&format!("{system:?}"));
    }

    pub fn repo_reads(&self) -> u32 {
        *self.reads.lock().unwrap()
    }
}
