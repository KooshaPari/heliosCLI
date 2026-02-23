// Schema validation module
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Schema {
    pub name: String,
    pub commands: Vec<Command>,
}

#[derive(Serialize, Deserialize)]
pub struct Command {
    pub name: String,
    pub command: String,
}

impl Schema {
    pub fn validate(&self) -> Result<(), String> {
        if self.name.is_empty() {
            return Err("schema name required".to_string());
        }
        Ok(())
    }
}
