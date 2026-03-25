---
work_package_id: "WP03"
title: "heliosCLI: codex/helios Workspace Merge"
lane: "planned"
dependencies: []
subtasks: ["T008", "T009", "T010"]
history:
  - date: "2026-03-03"
    event: "created"
    by: "spec-kitty.tasks"
---

# WP03: heliosCLI — codex/helios Workspace Merge

**Implementation command**: `spec-kitty implement WP03`

## Objective

Merge the dual codex-rs + helios-rs Cargo workspaces (134 crates, ~80% identical) into a single workspace with feature flags. Eliminate ~50 redundant crate definitions. Both `codex` and `helios` binaries continue to build and pass tests.

## Context

- heliosCLI currently has 67 crates in codex-rs/ and 67 near-identical crates in helios-rs/
- helios-rs was forked from codex-rs; differences are primarily branding and a few runtime-specific behaviors
- Research finding E001 confirmed merge via feature flags is the correct approach
- See `kitty-specs/002-phenotype-modular-arch/research.md` Decision 3

**Key constraint**: Both `cargo build --features codex-runtime` and `cargo build --features helios-runtime` must produce working binaries after this WP.

## Subtasks

### T008: Merge into single Cargo workspace

**Purpose**: Combine two workspace roots into one.

**Steps**:
1. **Audit differences** between codex-rs/ and helios-rs/:
   - Run `diff -rq codex-rs/ helios-rs/` to identify files that actually differ
   - Categorize: (a) identical files, (b) branding-only diffs, (c) behavioral diffs
   - Expected: ~80% identical, ~15% branding, ~5% behavioral

2. **Create unified workspace** at `codex-rs/` (keep codex-rs as the canonical location):
   - Update root `Cargo.toml` workspace members to include all unique crates
   - For identical crates: keep single copy in codex-rs/
   - For branding diffs: parameterize via feature flags or build-time config
   - For behavioral diffs: use `#[cfg(feature = "...")]` (see T009)

3. **Update internal crate dependencies**:
   - All `path = "../helios-rs/..."` references → point to unified locations
   - Verify `cargo check --workspace` passes

**Files**:
- `Cargo.toml` (workspace root — updated members list)
- Various `*/Cargo.toml` (path dependency updates)

**Validation**: `cargo check --workspace` succeeds with all crates resolving

### T009: Gate variant code behind feature flags

**Purpose**: Use Cargo features to select codex vs helios runtime behavior.

**Steps**:
1. Define features in the relevant binary/lib crate Cargo.toml:
   ```toml
   [features]
   default = ["helios-runtime"]
   codex-runtime = []
   helios-runtime = []
   ```

2. Gate variant-specific code:
   ```rust
   #[cfg(feature = "codex-runtime")]
   mod codex_specifics { /* ... */ }

   #[cfg(feature = "helios-runtime")]
   mod helios_specifics { /* ... */ }
   ```

3. Gate branding constants:
   ```rust
   #[cfg(feature = "codex-runtime")]
   pub const BINARY_NAME: &str = "codex";

   #[cfg(feature = "helios-runtime")]
   pub const BINARY_NAME: &str = "helios";
   ```

4. Ensure no `#[cfg]` blocks contain more than ~50 lines; if larger, extract to separate modules

**Files**: Primarily binary entry points and any crate with runtime-specific behavior
**Validation**:
- `cargo build --features codex-runtime` produces working codex binary
- `cargo build --features helios-runtime` produces working helios binary
- `cargo test --workspace` passes for both feature sets

### T010: Remove helios-rs, update CI

**Purpose**: Delete the redundant workspace directory and update CI to build both variants.

**Steps**:
1. Verify all helios-rs code is accounted for in the merged workspace
2. Delete `helios-rs/` directory entirely
3. Update `.github/workflows/rust-ci.yml`:
   - Add matrix strategy to build both variants:
     ```yaml
     strategy:
       matrix:
         features: [codex-runtime, helios-runtime]
     steps:
       - run: cargo build --features ${{ matrix.features }}
       - run: cargo test --features ${{ matrix.features }}
     ```
4. Update `BUILD.bazel` if Bazel targets reference helios-rs paths
5. Update any scripts in `scripts/` that reference helios-rs

**Files**:
- Delete `helios-rs/` (entire directory)
- `.github/workflows/rust-ci.yml` (update)
- `BUILD.bazel` / `MODULE.bazel` (update if needed)
- `scripts/*` (update references)

**Validation**:
- `helios-rs/` no longer exists
- CI passes for both feature variants
- `cargo test --workspace` passes
- Bazel build still works

## Definition of Done

- [ ] Single Cargo workspace with all unique crates
- [ ] `cargo build --features codex-runtime` produces codex binary
- [ ] `cargo build --features helios-runtime` produces helios binary
- [ ] All existing tests pass for both variants
- [ ] helios-rs/ directory deleted
- [ ] CI updated to test both variants
- [ ] ~50 fewer crate definitions than before

## Risks

- **Subtle behavioral differences**: Some helios-rs changes may be more than branding. The diff audit in T008 step 1 is critical — do not skip it.
- **Bazel integration**: Bazel BUILD files may have hardcoded helios-rs paths. Check `MODULE.bazel` and all `BUILD.bazel` files.
- **Test isolation**: Some tests may implicitly depend on which variant is active. Run full test suite under both feature flags.

## Reviewer Guidance

- Verify the diff audit was thorough — every helios-rs file accounted for
- Check that feature flags are mutually exclusive where needed
- Ensure no `#[cfg]` blocks duplicate large amounts of code (extract to modules instead)
- Confirm CI matrix covers both variants
