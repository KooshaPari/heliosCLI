---
work_package_id: WP13
title: 'portage: Ports, Plugins, Shared Consumption'
lane: planned
dependencies: []
subtasks: [T040, T042, T043, T044]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP13: portage — Ports, Plugins, Shared Consumption

**Implementation command**: `spec-kitty implement WP13 --base WP10`

## Objective

Formalize portage's extension points as `typing.Protocol` ports. Implement benchmark adapter plugin registry (Tier 1 via entry_points, Tier 2 via Extism). Consume `phenotype-py-infra` for shared utilities.

## Context

- portage has ~40 benchmark adapters with informal patterns
- Shares infrastructure needs with thegent (file ops, subprocess, cache)
- phenotype-py-infra published in WP10
- See plan.md Lane 5

## Subtasks

### T040: Formalize ports via typing.Protocol

**Steps**:
1. Define port protocols in `portage/ports/`:
   ```python
   class ExecutorPort(Protocol):
       def run_trial(self, config: TrialConfig) -> TrialResult: ...

   class ReporterPort(Protocol):
       def report(self, results: list[TrialResult]) -> Report: ...

   class LoaderPort(Protocol):
       def load_benchmark(self, path: str) -> BenchmarkSpec: ...
   ```
2. Ensure existing implementations conform
3. Add pyright strict mode on port modules

**Validation**: Type checking passes on all port implementations

### T042: Tier 1 — benchmark adapter plugin registry

**Steps**:
1. Add entry_points for each adapter in pyproject.toml
2. Create registry discovering adapters via `importlib.metadata`
3. Replace hardcoded adapter list with registry discovery

**Validation**: All 40 adapters discoverable via entry_points

### T043: Tier 2 — Extism host for user adapters

**Steps**:
1. Add extism Python SDK
2. Create plugin host loading .wasm adapters from `~/.portage/plugins/`
3. Validate against ExecutorPort contract
4. Sandbox constraints: memory, timeout, no fs

**Validation**: Test WASM adapter loads and executes

### T044: Consume phenotype-py-infra

**Steps**:
1. Add `phenotype-py-infra` dependency to portage
2. Replace local utility code with shared imports (subprocess, file ops, cache)
3. Remove duplicated utility code

**Validation**: `pytest` passes with shared dependency

## Definition of Done

- [ ] typing.Protocol ports formalized for executor, reporter, loader
- [ ] Entry_points registry replaces hardcoded adapter discovery
- [ ] Extism host prototype for .wasm adapters
- [ ] phenotype-py-infra consumed, local duplicates removed
- [ ] All tests pass

## Reviewer Guidance

- Verify port protocols are minimal (not over-specified)
- Check adapter migration didn't break any benchmark workflows
