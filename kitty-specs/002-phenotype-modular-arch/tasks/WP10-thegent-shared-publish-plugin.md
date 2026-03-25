---
work_package_id: WP10
title: 'thegent: Shared Publish + Plugin System + Re-export'
lane: planned
dependencies: []
subtasks: [T028, T029, T030, T031, T033]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP10: thegent — Shared Publish + Plugin System + Re-export Layer

**Implementation command**: `spec-kitty implement WP10 --base WP09`

## Objective

Publish thegent-infra internals to `phenotype-py-infra` shared repo. Formalize the AdapterPort pattern. Implement Tier 1 (entry_points) and Tier 2 (Extism) plugin system. Make `src/thegent/` a thin re-export layer.

## Context

- thegent-infra extracted in WP09 (~11K LOC, zero thegent-specific deps)
- phenotype-py-infra repo scaffolded in WP02
- thegent has 15+ adapters with informal AdapterPort pattern — formalize for plugin registration
- `src/thegent/` should become thin re-exports over packages

## Subtasks

### T028: Publish to phenotype-py-infra

**Steps**:
1. Copy thegent-infra source to `phenotype-py-infra/src/phenotype_py_infra/`
2. Set up pyproject.toml with proper metadata, version 0.1.0
3. In thegent, replace local thegent-infra with `phenotype-py-infra` dependency
4. In portage (future, WP13), will also consume this

**Validation**: `uv pip install -e ./phenotype-py-infra && pytest`

### T029: Formalize AdapterPort pattern

**Steps**:
1. Define `AdapterPort` as a `typing.Protocol`:
   ```python
   class AdapterPort(Protocol):
       def name(self) -> str: ...
       def capabilities(self) -> list[str]: ...
       def execute(self, request: AdapterRequest) -> AdapterResponse: ...
       def health(self) -> HealthStatus: ...
   ```
2. Audit all existing adapters in thegent-agents; ensure they conform
3. Add type checking enforcement (pyright/mypy strict mode on adapter modules)

**Validation**: All adapters pass type checking against AdapterPort

### T030: Tier 1 — entry_points registration

**Steps**:
1. Add `entry_points` configuration in pyproject.toml for each adapter:
   ```toml
   [project.entry-points."thegent.adapters"]
   codex = "thegent_agents.adapters.codex:CodexAdapter"
   cursor = "thegent_agents.adapters.cursor:CursorAdapter"
   ```
2. Create adapter registry that discovers via `importlib.metadata.entry_points()`
3. Wire registry into agent orchestration path

**Validation**: Adapters discoverable via entry_points; no hardcoded adapter list

### T031: Tier 2 — Extism host for user skills

**Steps**:
1. Add `extism` Python SDK dependency
2. Create `thegent-skills/plugin_host.py`:
   - Load .wasm skill plugins from `~/.thegent/plugins/`
   - Validate plugin exports match AdapterPort contract
   - Sandbox: memory limit, timeout, no fs access
3. Register WASM skills alongside native entry_points
4. Create test .wasm skill

**Validation**: Test WASM skill loads and executes; failure doesn't crash host

### T033: Make src/thegent/ a thin re-export layer

**Steps**:
1. Replace all business logic in `src/thegent/` with re-exports from packages:
   ```python
   # src/thegent/__init__.py
   from thegent_core import *
   from thegent_config import *
   # etc.
   ```
2. Preserve backward compatibility — existing `from thegent import X` must still work
3. Add deprecation warnings for direct `src/thegent/` imports if desired

**Validation**: `from thegent import X` works for all public APIs; `src/thegent/` has minimal code

## Definition of Done

- [ ] phenotype-py-infra contains thegent-infra code and is consumable
- [ ] AdapterPort formalized as typing.Protocol
- [ ] entry_points registration replaces hardcoded adapter discovery
- [ ] Extism host loads .wasm skill plugins
- [ ] src/thegent/ is thin re-export layer
- [ ] All tests pass

## Risks

- **entry_points discovery performance**: First call may be slow. Consider caching.
- **Backward compatibility**: Re-export layer must not break existing imports. Test thoroughly.

## Reviewer Guidance

- Verify phenotype-py-infra has no thegent-specific types
- Check AdapterPort is general enough for all adapter types
- Ensure re-export layer covers all public APIs
