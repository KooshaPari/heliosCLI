//! # arch_test - Architectural Tests
pub mod boundary;
pub mod tdd;
pub mod proptest_patterns;
pub use boundary::BoundaryEnforcer;
pub use tdd::TestDriven;
pub use proptest_patterns::PropertyTest;
