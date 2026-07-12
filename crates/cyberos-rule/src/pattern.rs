use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum System {
    Qimen,
    Liuren,
    Taiyi,
    All,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Polarity {
    Cat,
    Hung,
    Trung,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum Status {
    #[default]
    Active,
    Draft,
    Deprecated,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Pattern {
    pub id: String,
    pub system: System,
    pub name: String,
    #[serde(default)]
    pub name_han: Option<String>,
    pub conditions: serde_json::Value,
    pub polarity: Polarity,
    pub meaning_classical: String,
    pub meaning_modern: String,
    #[serde(default)]
    pub citations: Vec<String>,
    pub version: u32,
    pub confidence: f32,
    #[serde(default)]
    pub status: Status,
}

impl Pattern {
    pub fn stamp(&self) -> (String, u32) {
        (self.id.clone(), self.version)
    }
}
