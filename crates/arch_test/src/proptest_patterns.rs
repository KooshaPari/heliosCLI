//! Property-based testing patterns
#[derive(Debug, Clone)] pub struct PropertyTest { pub name: String, pub iterations: u32 }
impl PropertyTest { pub fn new(name: impl Into<String>) -> Self { Self { name: name.into(), iterations: 256 } } }
pub mod strategies {
    use proptest::prelude::*;
    pub fn valid_utf8() -> impl Strategy<Value = String> { ".*" }
    pub fn positive_int() -> impl Strategy<Value = u32> { any::<u32>().prop_filter("positive", |&n| n > 0) }
    pub fn identifier() -> impl Strategy<Value = String> { "[a-z][a-z0-9_]{0,63}" }
}
pub mod invariants {
    pub fn check<T>(value: &T, inv: impl Fn(&T) -> bool, name: &str) -> Result<(), String> {
        if inv(value) { Ok(()) } else { Err(format!("Invariant violated: {}", name)) }
    }
}
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn test_invariant() { assert!(invariants::check(&42, |v| *v > 0, "positive").is_ok()); }
}
