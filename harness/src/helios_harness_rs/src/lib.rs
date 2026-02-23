//! Helios Harness Rust Extension - Performance Critical Paths
//!
//! This module provides Rust implementations for:
//! - Fast resource sampling (sub-millisecond)
//! - High-performance LRU cache
//! - Zero-copy resource monitoring

use pyo3::prelude::*;
use pyo3::Bound;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

mod cache;
mod resources;

/// Initialize the extension module
#[pymodule]
fn helios_harness_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<resources::ResourceSampler>()?;
    m.add_class::<resources::ResourceSnapshot>()?;
    m.add_class::<cache::LruCache>()?;
    m.add_class::<cache::CacheStats>()?;
    Ok(())
}
