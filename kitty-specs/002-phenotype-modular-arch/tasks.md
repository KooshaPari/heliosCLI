# Work Packages: Phenotype Ecosystem Modularization & Plugin Architecture

**Feature**: 002-phenotype-modular-arch
**Generated**: 2026-03-03
**Total Subtasks**: 47 | **Work Packages**: 15

---

## Subtask Registry

| ID | Description | Lane | Parallel | WP |
|----|-------------|------|----------|----|
| T001 | Create `phenotype-proto` repo with buf config | L0 | — | WP01 |
| T002 | Define `domain/v1/` protos (session, agent, routing, audit) | L0 | [P] | WP01 |
| T003 | Define `plugin/v1/` protos (executor, tool, adapter) | L0 | [P] | WP01 |
| T004 | Configure `buf generate` for Rust, Go, Python, TypeScript | L0 | — | WP01 |
| T005 | CI: buf lint + buf breaking on phenotype-proto | L0 | — | WP01 |
| T006 | Create empty shared Go repos (authkit, executor-core, httpkit) | L0 | [P] | WP02 |
| T007 | Create empty shared repos (rs-protocol, py-infra, audit-core, protocol-types) | L0 | [P] | WP02 |
| T008 | Merge codex-rs + helios-rs into single Cargo workspace | L1 | — | WP03 |
| T009 | Gate variant code behind feature flags | L1 | — | WP03 |
| T010 | Remove helios-rs directory, update CI | L1 | — | WP03 |
| T011 | Extract protocol crate to `phenotype-rs-protocol` | L1 | — | WP04 |
| T012 | Implement Tier 1 plugin: `ToolPlugin` trait + `inventory` | L1 | — | WP05 |
| T013 | Prototype Tier 2 plugin: Extism host for user tools | L1 | — | WP05 |
| T014 | Emit audit events from codex-core session lifecycle | L1 | — | WP12 |
| T015 | Extract `sdk/executor-core`: ExecutorInterface, BaseExecutor | L2 | — | WP06 |
| T016 | Refactor 15 executors to use executor-core base | L2 | — | WP06 |
| T017 | Extract auth logic to `phenotype-go-authkit` | L2 | — | WP07 |
| T018 | Extract HTTP helpers to `phenotype-go-httpkit` | L2 | — | WP07 |
| T019 | Implement Tier 1 plugin: Executor interface + init() | L2 | — | WP08 |
| T020 | Prototype Tier 2 plugin: Extism host for executor .wasm | L2 | — | WP08 |
| T021 | Translator matrix builder codegen | L2 | — | WP08 |
| T022 | Formalize executor + translator as hexagonal ports | L2 | — | WP08 |
| T023 | Emit audit events from proxy routing | L2 | — | WP12 |
| T024 | Extract `thegent-config` from src/thegent/config*.py | L3 | [P] | WP09 |
| T025 | Extract `thegent-infra` from src/thegent/infra/ | L3 | [P] | WP09 |
| T026 | Extract `thegent-governance` from src/thegent/governance/ | L3 | [P] | WP09 |
| T027 | Merge thegent-protocols + thegent-mcp into thegent-mcp | L3 | [P] | WP09 |
| T028 | Publish thegent-infra internals to `phenotype-py-infra` | L3 | — | WP10 |
| T029 | Formalize AdapterPort pattern across adapters | L3 | — | WP10 |
| T030 | Implement Tier 1 plugin: entry_points registration | L3 | — | WP10 |
| T031 | Prototype Tier 2 plugin: Extism host for user skills | L3 | — | WP10 |
| T032 | Emit audit events from agent execution lifecycle | L3 | — | WP12 |
| T033 | Make src/thegent/ a thin re-export layer | L3 | — | WP10 |
| T034 | Extract `@helios/audit-core` from apps/runtime/src/audit/ | L4 | [P] | WP11 |
| T035 | Extract `@helios/protocol-types` from protocol/types.ts | L4 | [P] | WP11 |
| T036 | Extract service interfaces to `@helios/service-contracts` | L4 | [P] | WP11 |
| T037 | Publish TS packages to npm/GitHub Packages | L4 | — | WP11 |
| T038 | Refactor runtime to consume extracted packages | L4 | — | WP11 |
| T039 | Implement aggregated audit trail view | L4 | — | WP15 |
| T040 | Formalize ports: typing.Protocol for executor, reporter, loader | L5 | — | WP13 |
| T041 | Emit trial events: TrialStarted, TrialCheckpoint, TrialCompleted | L5 | — | WP12 |
| T042 | Implement benchmark adapter plugin registry (Tier 1) | L5 | — | WP13 |
| T043 | Prototype Tier 2 plugin: Extism host for adapters | L5 | — | WP13 |
| T044 | Consume `phenotype-py-infra` for shared utilities | L5 | — | WP13 |
| T045 | Extract internal/domain/ package: Agent, Session, RoutingRule | L6 | — | WP14 |
| T046 | Consume phenotype-go-authkit + httpkit | L6 | — | WP14 |
| T047 | Emit routing audit events: AgentRouted, SessionCreated | L6 | — | WP12 |

---

## Work Package Summary

### Phase 1: Foundation

#### WP01 — Protobuf Contract System (phenotype-proto)
- **Priority**: P0 (critical path — blocks audit events in all repos)
- **Subtasks**: T001, T002, T003, T004, T005 (5 tasks)
- **Dependencies**: None
- **Estimated prompt**: ~350 lines
- **Implementation**: `spec-kitty implement WP01`

Create phenotype-proto repo, define domain and plugin protos, configure buf codegen for 4 languages, add CI.

#### WP02 — Shared Package Scaffolding
- **Priority**: P0 (blocks shared package extraction)
- **Subtasks**: T006, T007 (2 tasks)
- **Dependencies**: None
- **Estimated prompt**: ~200 lines
- **Implementation**: `spec-kitty implement WP02`

Create 7 empty shared package repos with proper structure, README, CI, and package manager config.

### Phase 2: Per-Repo Internal Restructuring (all parallel)

#### WP03 — heliosCLI: codex/helios Workspace Merge
- **Priority**: P0 (highest impact — eliminates ~50 redundant crates)
- **Subtasks**: T008, T009, T010 (3 tasks)
- **Dependencies**: None
- **Estimated prompt**: ~400 lines
- **Implementation**: `spec-kitty implement WP03`

Merge codex-rs + helios-rs into single Cargo workspace with feature flags. Remove helios-rs.

#### WP04 — heliosCLI: Protocol Extraction to Shared Repo
- **Priority**: P1
- **Subtasks**: T011 (1 task — but complex, ~300 lines of guidance)
- **Dependencies**: WP02, WP03
- **Estimated prompt**: ~250 lines
- **Implementation**: `spec-kitty implement WP04 --base WP03`

Extract protocol crate types to phenotype-rs-protocol shared repo.

#### WP05 — heliosCLI: Plugin System (Tier 1 + Tier 2)
- **Priority**: P2
- **Subtasks**: T012, T013 (2 tasks)
- **Dependencies**: WP03
- **Estimated prompt**: ~350 lines
- **Implementation**: `spec-kitty implement WP05 --base WP03`

Implement ToolPlugin trait with inventory registration (Tier 1), prototype Extism host (Tier 2).

#### WP06 — cliproxyapi++: Executor Core Extraction
- **Priority**: P1
- **Subtasks**: T015, T016 (2 tasks)
- **Dependencies**: None
- **Estimated prompt**: ~400 lines
- **Implementation**: `spec-kitty implement WP06`

Extract sdk/executor-core with shared base, refactor 15 executors to use it.

#### WP07 — cliproxyapi++: Shared Package Extraction (authkit + httpkit)
- **Priority**: P1
- **Subtasks**: T017, T018 (2 tasks)
- **Dependencies**: WP02
- **Estimated prompt**: ~300 lines
- **Implementation**: `spec-kitty implement WP07 --base WP02`

Extract auth logic to phenotype-go-authkit, HTTP helpers to phenotype-go-httpkit.

#### WP08 — cliproxyapi++: Plugin System + Hexagonal Ports
- **Priority**: P2
- **Subtasks**: T019, T020, T021, T022 (4 tasks)
- **Dependencies**: WP06
- **Estimated prompt**: ~450 lines
- **Implementation**: `spec-kitty implement WP08 --base WP06`

Tier 1 + Tier 2 executor plugins, translator matrix builder, hexagonal port formalization.

#### WP09 — thegent: Package Migration Completion
- **Priority**: P1
- **Subtasks**: T024, T025, T026, T027 (4 tasks)
- **Dependencies**: None
- **Estimated prompt**: ~400 lines
- **Implementation**: `spec-kitty implement WP09`

Extract config, infra, governance packages. Merge protocols+mcp.

#### WP10 — thegent: Shared Publish + Plugin System + Re-export Layer
- **Priority**: P2
- **Subtasks**: T028, T029, T030, T031, T033 (5 tasks)
- **Dependencies**: WP02, WP09
- **Estimated prompt**: ~450 lines
- **Implementation**: `spec-kitty implement WP10 --base WP09`

Publish to phenotype-py-infra, formalize AdapterPort, plugin registration, Extism prototype, thin re-export layer.

#### WP11 — heliosApp: Package Extraction + Publishing
- **Priority**: P1
- **Subtasks**: T034, T035, T036, T037, T038 (5 tasks)
- **Dependencies**: WP02
- **Estimated prompt**: ~400 lines
- **Implementation**: `spec-kitty implement WP11 --base WP02`

Extract audit-core, protocol-types, service-contracts. Publish. Refactor runtime to consume.

### Phase 3: Cross-Repo Audit Events

#### WP12 — Audit Event Integration (All Repos)
- **Priority**: P1 (requires proto codegen from WP01)
- **Subtasks**: T014, T023, T032, T041, T047 (5 tasks)
- **Dependencies**: WP01
- **Estimated prompt**: ~500 lines
- **Implementation**: `spec-kitty implement WP12 --base WP01`

Emit structured audit events from heliosCLI, cliproxyapi++, thegent, portage, agentapi++.

### Phase 4: Remaining Plugin Systems + Shared Consumption

#### WP13 — portage: Ports, Plugins, Shared Consumption
- **Priority**: P2
- **Subtasks**: T040, T042, T043, T044 (4 tasks)
- **Dependencies**: WP10 (for phenotype-py-infra)
- **Estimated prompt**: ~350 lines
- **Implementation**: `spec-kitty implement WP13 --base WP10`

Formalize typing.Protocol ports, benchmark adapter plugin registry, Extism prototype, consume phenotype-py-infra.

#### WP14 — agentapi++: Domain Extraction + Shared Consumption
- **Priority**: P2
- **Subtasks**: T045, T046 (2 tasks)
- **Dependencies**: WP07
- **Estimated prompt**: ~250 lines
- **Implementation**: `spec-kitty implement WP14 --base WP07`

Extract internal/domain/ package, consume authkit + httpkit.

### Phase 5: Integration

#### WP15 — heliosApp: Aggregated Audit Trail View
- **Priority**: P3
- **Subtasks**: T039 (1 task — UI + data integration)
- **Dependencies**: WP11, WP12
- **Estimated prompt**: ~250 lines
- **Implementation**: `spec-kitty implement WP15 --base WP12`

Implement aggregated audit trail view consuming events from all repos.

---

## Dependency DAG

```
WP01 ──────────────────────────────▶ WP12 ──▶ WP15
WP02 ──▶ WP04, WP07, WP10, WP11 ──────────▶ WP15
WP03 ──▶ WP04, WP05
WP06 ──▶ WP08
WP09 ──▶ WP10 ──▶ WP13
WP07 ──▶ WP14
```

## Parallelization Opportunities

**Batch A** (no deps, fully parallel): WP01, WP02, WP03, WP06, WP09
**Batch B** (after Batch A): WP04, WP05, WP07, WP08, WP10, WP11, WP12
**Batch C** (after Batch B): WP13, WP14, WP15

**Maximum parallelism**: 5 agents in Batch A, 7 in Batch B, 3 in Batch C.

## MVP Scope

**WP01 + WP03** are the highest-impact starting points:
- WP01 unblocks the entire audit event integration across all repos
- WP03 eliminates ~50 redundant crate definitions (biggest single LOC reduction)
