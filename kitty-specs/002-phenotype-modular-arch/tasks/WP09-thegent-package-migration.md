---
work_package_id: "WP09"
title: "thegent: Package Migration Completion"
lane: "planned"
dependencies: []
subtasks: ["T024", "T025", "T026", "T027"]
history:
  - date: "2026-03-03"
    event: "created"
    by: "spec-kitty.tasks"
---

# WP09: thegent — Package Migration Completion

**Implementation command**: `spec-kitty implement WP09`

## Objective

Complete thegent's partial migration from monolithic `src/thegent/` to `packages/thegent-*`. Extract config, infra, governance packages. Merge protocols+mcp.

## Context

- thegent is ~60% migrated; `packages/` already contains thegent-core, thegent-cli, thegent-agents, thegent-execution, thegent-sync, thegent-audit, thegent-planning, thegent-observability, thegent-skills
- Remaining in `src/thegent/`: config*.py (~500 LOC), infra/ (~11K LOC), governance/ (~13K LOC)
- thegent-protocols and thegent-mcp exist separately but overlap — merge into single thegent-mcp
- See `kitty-specs/002-phenotype-modular-arch/research.md` Decision 4

## Subtasks

### T024: Extract thegent-config

**Steps**:
1. Identify config files: `src/thegent/config.py`, `src/thegent/config_schema.py`, related
2. Create `packages/thegent-config/`:
   - `pyproject.toml` with package metadata
   - `src/thegent_config/__init__.py` — re-exports
   - Move config schemas, validation, loading logic
3. Update `src/thegent/` imports to use `thegent-config`
4. Add to workspace `pyproject.toml`

**Validation**: `uv sync && pytest packages/thegent-config/`

### T025: Extract thegent-infra

**Steps**:
1. Identify infra code: `src/thegent/infra/` (~11K LOC)
   - Fast YAML, subprocess runner, file ops, IPC bridge, cache
2. Create `packages/thegent-infra/`:
   - Preserve module structure from `infra/`
   - Ensure zero thegent-specific imports (this is the reusable layer)
3. Update all `src/thegent/` and `packages/*/` imports
4. This package will later be published as `phenotype-py-infra` (WP10)

**Validation**: `pytest packages/thegent-infra/` passes; no thegent-specific deps

### T026: Extract thegent-governance

**Steps**:
1. Identify: `src/thegent/governance/` (~13K LOC) — policy engine, HITL, escalation
2. Create `packages/thegent-governance/`
3. Move governance code; update imports
4. May depend on thegent-core for domain types

**Validation**: `pytest packages/thegent-governance/`

### T027: Merge thegent-protocols + thegent-mcp

**Steps**:
1. Audit overlap between `packages/thegent-protocols/` and `packages/thegent-mcp/`
2. Merge into single `packages/thegent-mcp/`:
   - Combine protocol definitions with MCP implementation
   - Remove thegent-protocols package
3. Update all imports from thegent-protocols → thegent-mcp
4. Update workspace pyproject.toml

**Validation**: `pytest packages/thegent-mcp/` passes; no references to thegent-protocols remain

## Definition of Done

- [ ] thegent-config extracted and passing tests
- [ ] thegent-infra extracted with zero thegent-specific deps
- [ ] thegent-governance extracted and passing tests
- [ ] thegent-protocols merged into thegent-mcp
- [ ] All workspace tests pass (`pytest`)
- [ ] `src/thegent/` is significantly smaller

## Risks

- **Import cycles**: Governance may depend on config which depends on core. Map dependency graph before extracting.
- **Test fixtures**: Some tests may use fixtures from `src/thegent/` that need to move with their packages.

## Reviewer Guidance

- Verify thegent-infra has truly zero thegent-specific imports (grep for `thegent`)
- Check dependency direction: infra should be at the bottom (no upward deps)
- Ensure merged thegent-mcp covers all protocol+MCP functionality
