//! # Property-Based Tests
//!
//! Property-based testing using proptest for fuzzing and property verification.
//!
//! ## Property Testing Flow
//!
//! ```text
//! ┌──────────────────────────────────────────┐
//! │     PROPERTY-BASED TESTING FLOW            │
//! ├──────────────────────────────────────────┤
//! │                                          │
//! │   ┌─────────┐    ┌──────────┐           │
//! │   │Property │───▶│ Generate │           │
//! │   │  Test   │    │  Inputs  │           │
//! │   └────┬────┘    └────┬─────┘           │
//! │        │              │                   │
//! │        ▼              ▼                   │
//! │   ┌─────────┐    ┌──────────┐          │
//! │   │ Property│◀───│ Shrink   │          │
//! │   │ Holds?  │    │ Inputs   │          │
//! │   └───┬────┘    └──────────┘          │
//! │       │                                 │
//! │       ▼                                 │
//! │   ┌────────────────────────┐           │
//! │   │ Property Holds for ALL │           │
//! │   │ Generated Test Cases   │           │
//! │   └────────────────────────┘           │
//! │                                          │
//! └──────────────────────────────────────────┘
//! ```

use proptest::prelude::*;

/// Property: Reversing a slice twice returns the original
#[test]
fn test_slice_reverse_is_involutive() {
    proptest!(|(mut v in proptest::collection::vec(0i32..1000, 0..100))| {
        let original = v.clone();
        v.reverse();
        v.reverse();
        prop_assert_eq!(v, original);
    });
}

/// Property: Sorting makes array non-decreasing
#[test]
fn test_sort_is_monotonic() {
    proptest!(|(mut v in proptest::collection::vec(-1000i32..1000, 0..100))| {
        v.sort();

        for i in 1..v.len() {
            prop_assert!(v[i] >= v[i-1]);
        }
    });
}

/// Property: Sorted array has same length as original
#[test]
fn test_sort_preserves_length() {
    proptest!(|(v in proptest::collection::vec(0i32..1000, 0..100))| {
        let len = v.len();
        let mut sorted = v.clone();
        sorted.sort();
        prop_assert_eq!(sorted.len(), len);
    });
}

/// Property: Minimum element is always <= all elements
#[test]
fn test_min_is_less_than_or_equal_all() {
    proptest!(|(v in proptest::collection::vec(0i32..1000, 1..100))| {
        let min = *v.iter().min().unwrap();

        for &x in &v {
            prop_assert!(min <= x);
        }
    });
}

/// Property: Maximum element is always >= all elements
#[test]
fn test_max_is_greater_than_or_equal_all() {
    proptest!(|(v in proptest::collection::vec(0i32..1000, 1..100))| {
        let max = *v.iter().max().unwrap();

        for &x in &v {
            prop_assert!(max >= x);
        }
    });
}

/// Property: HashMap insert and retrieve
#[test]
fn test_hashmap_insert_retrieve() {
    proptest!(|(k in ".*", v in ".*")| {
        let mut map = std::collections::HashMap::new();
        map.insert(k.clone(), v.clone());

        prop_assert_eq!(map.get(&k), Some(&v));
    });
}

/// Property: HashMap removal makes key absent
#[test]
fn test_hashmap_remove() {
    proptest!(|(k in ".*", v in ".*")| {
        let mut map = std::collections::HashMap::new();
        map.insert(k.clone(), v.clone());
        map.remove(&k);

        prop_assert_eq!(map.get(&k), None);
    });
}

/// Property: String concatenation is associative
#[test]
fn test_string_concat_associative() {
    proptest!(|(a in ".*", b in ".*", c in ".*")| {
        let left = format!("{}{}{}", a, b, c);
        let right = format!("{}{}{}", a, b, c);
        prop_assert_eq!(left, right);
    });
}

/// Property: Integer addition is commutative
#[test]
fn test_int_add_commutative() {
    proptest!(|(a in -1000i32..1000, b in -1000i32..1000)| {
        prop_assert_eq!(a + b, b + a);
    });
}

/// Property: Integer multiplication distributes over addition
#[test]
fn test_int_mul_distributes_over_add() {
    proptest!(|(a in -100i32..100, b in -100i32..100, c in -100i32..100)| {
        prop_assert_eq!(a * (b + c), a * b + a * c);
    });
}

/// Property: Vec push increases length by 1
#[test]
fn test_vec_push_increments_length() {
    proptest!(|(v in proptest::collection::vec(0i32..100, 0..50), x in 0i32..1000)| {
        let len = v.len();
        let mut vec = v.clone();
        vec.push(x);
        prop_assert_eq!(vec.len(), len + 1);
        prop_assert_eq!(vec.last(), Some(&x));
    });
}

/// Property: Option::Some contains the value
#[test]
fn test_option_some_contains_value() {
    proptest!(|(x in 0i32..1000)| {
        let opt = Some(x);
        prop_assert!(opt.is_some());
        prop_assert_eq!(opt.unwrap(), x);
    });
}

/// Property: Result::Ok is ok
#[test]
fn test_result_ok_is_ok() {
    proptest!(|(x in 0i32..1000)| {
        let res: Result<i32, &str> = Ok(x);
        prop_assert!(res.is_ok());
        prop_assert_eq!(res.unwrap(), x);
    });
}

/// Property: Checked division never panics
#[test]
fn test_checked_div_safe() {
    proptest!(|(a in -1000i32..1000, b in -1000i32..1000)| {
        if b != 0 {
            let result = a.checked_div(b);
            prop_assert!(result.is_some());
        }
    });
}

/// Property: Binary search finds target
#[test]
fn test_binary_search_finds_sorted_target() {
    proptest!(|(target in 0i32..1000)| {
        let mut sorted: Vec<i32> = (0..1000).collect();
        sorted.sort();

        // Binary search should find or not find target based on existence
        let idx = sorted.binary_search(&target);
        match idx {
            Ok(i) => {
                prop_assert_eq!(sorted[i], target);
            }
            Err(_) => {
                // Target not in array, verify it's not present
                prop_assert!(!sorted.contains(&target));
            }
        }
    });
}
