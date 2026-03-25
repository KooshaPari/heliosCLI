---
work_package_id: WP04
title: 'heliosCLI: Protocol Extraction to Shared Repo'
lane: planned
dependencies: []
subtasks: [T011]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP04: heliosCLI — Protocol Extraction to Shared Repo

**Implementation command**: `spec-kitty implement WP04 --base WP03`

## Objective

Extract the `protocol` crate types from the heliosCLI Cargo workspace to the `phenotype-rs-protocol` shared repo. heliosCLI then consumes it as a dependency.

## Context

- `phenotype-rs-protocol` repo scaffolded in WP02
- heliosCLI workspace merged in WP03
- The protocol crate contains: ModelConfig, ToolSpec, MessageHistory, ApprovalPolicy (~8K LOC)
- Consumers: heliosCLI (today), future Rust-based agents

## Subtasks

### T011: Extract protocol crate to phenotype-rs-protocol

**Steps**:
1. Identify the protocol crate in the merged workspace (likely `codex-rs/core/` or a dedicated `protocol` crate)
2. Copy relevant types to `phenotype-rs-protocol/src/`:
   - `lib.rs` — re-exports
   - `model.rs` — ModelConfig, model-related types
   - `tool.rs` — ToolSpec, DynamicToolSpec
   - `message.rs` — MessageHistory, conversation types
   - `policy.rs` — ApprovalPolicy, approval-related types
3. Add dependencies to `phenotype-rs-protocol/Cargo.toml` (serde, prost if proto-generated)
4. In heliosCLI, replace local protocol types with `phenotype-rs-protocol` dependency:
   ```toml
   [dependencies]
   phenotype-rs-protocol = { git = "https://github.com/KooshaPari/phenotype-rs-protocol", branch = "main" }
   ```
5. Update all `use protocol::*` imports across heliosCLI crates
6. Remove the local protocol crate from heliosCLI workspace

**Files**:
- `phenotype-rs-protocol/src/*.rs` (new, ~8K LOC total)
- `phenotype-rs-protocol/Cargo.toml` (updated deps)
- heliosCLI `Cargo.toml` (workspace members, add git dep)
- All heliosCLI files importing protocol types (import path updates)

**Validation**:
- `cargo build` in phenotype-rs-protocol succeeds
- `cargo build --workspace` in heliosCLI succeeds with external dep
- `cargo test --workspace` passes

## Definition of Done

- [ ] phenotype-rs-protocol contains all shared protocol types
- [ ] heliosCLI consumes phenotype-rs-protocol as git dependency
- [ ] Local protocol crate removed from heliosCLI workspace
- [ ] All tests pass in both repos
- [ ] No duplicate type definitions remain

## Risks

- **Circular dependencies**: Protocol types may reference heliosCLI-internal types. Extract only types with no internal deps; leave heliosCLI-specific extensions in the local codebase.
- **Breaking API surface**: Consumer imports change. Search all `use` statements.

## Reviewer Guidance

- Verify extracted types have no dependencies on heliosCLI internals
- Check that the shared crate's public API is minimal and well-documented
