---
work_package_id: WP05
title: 'heliosCLI: Plugin System (Tier 1 + Tier 2)'
lane: planned
dependencies: []
subtasks: [T012, T013]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP05: heliosCLI — Plugin System (Tier 1 + Tier 2)

**Implementation command**: `spec-kitty implement WP05 --base WP03`

## Objective

Implement the two-tier plugin architecture for heliosCLI tools. Tier 1: compile-time native trait registration via `inventory` crate. Tier 2: runtime Extism/WASM plugins for user-defined tools.

## Context

- heliosCLI already has `DynamicToolSpec` as an ad-hoc extension point
- See `docs/governance/plugin_architecture_governance.md` for the two-tier microkernel decision
- Tier 1 is the primary mechanism for built-in tools; Tier 2 is for user/third-party extensions

## Subtasks

### T012: Tier 1 — ToolPlugin trait + inventory registration

**Steps**:
1. Add `inventory` crate to workspace dependencies
2. Define the `ToolPlugin` trait:
   ```rust
   pub trait ToolPlugin: Send + Sync + 'static {
       fn name(&self) -> &str;
       fn description(&self) -> &str;
       fn spec(&self) -> ToolSpec;
       fn execute(&self, input: serde_json::Value) -> Result<serde_json::Value>;
   }
   inventory::collect!(Box<dyn ToolPlugin>);
   ```
3. Create `plugin/` module in the core crate with:
   - `registry.rs` — `PluginRegistry` that collects all `inventory` submissions
   - `trait.rs` — `ToolPlugin` trait definition
4. Convert 1-2 existing built-in tools to use `ToolPlugin` trait as proof of concept
5. Wire registry into tool discovery/execution path

**Validation**: Built-in tools register and execute via the new trait

### T013: Tier 2 — Extism host for user tools

**Steps**:
1. Add `extism` crate to workspace dependencies
2. Create `plugin/wasm_host.rs`:
   - Load `.wasm` plugin files from a configurable directory (`~/.helios/plugins/`)
   - Validate plugin implements the ToolPlugin contract (check exported functions)
   - Wrap WASM plugin in a `WasmToolPlugin` that implements `ToolPlugin` trait
3. Implement sandbox constraints:
   - Memory limit per plugin (default: 256MB)
   - No filesystem access (use Extism PDK for controlled I/O)
   - Timeout per invocation (default: 30s)
4. Add plugin discovery: scan plugin directory on startup, load valid `.wasm` files
5. Merge WASM-loaded plugins into the same `PluginRegistry` as Tier 1

**Validation**:
- Create a minimal test `.wasm` plugin (e.g., a tool that returns a static response)
- Plugin loads, validates, and executes correctly
- Invalid/crashing plugins don't affect host

## Definition of Done

- [ ] `ToolPlugin` trait defined with inventory registration
- [ ] At least 1 built-in tool refactored to use the trait
- [ ] Extism host loads .wasm plugins from plugin directory
- [ ] WASM plugins are sandboxed (memory limit, timeout)
- [ ] Plugin registry merges both tiers
- [ ] Failing WASM plugin doesn't crash host

## Risks

- **Extism performance**: WASM invocation overhead may be noticeable for latency-sensitive tools. Benchmark the prototype.
- **inventory crate compatibility**: Ensure it works with the Cargo workspace structure and Bazel builds.

## Reviewer Guidance

- Verify sandbox constraints are properly enforced (test with a malicious plugin)
- Check that the ToolPlugin trait is general enough for diverse tool types
- Ensure error handling wraps all WASM host calls
