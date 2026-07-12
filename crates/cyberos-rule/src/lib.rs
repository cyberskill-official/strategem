//! Pattern-as-data (FR-RULE-001).

pub mod pattern;
pub mod seed;
pub mod validate;
pub mod version;

pub use pattern::{Pattern, Polarity, Status, System};
pub use seed::{load_seed, SeedError};
pub use validate::{validate_pattern, ValidationError};
