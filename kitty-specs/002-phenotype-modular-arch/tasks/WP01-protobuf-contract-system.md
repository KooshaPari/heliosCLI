---
work_package_id: "WP01"
title: "Protobuf Contract System (phenotype-proto)"
lane: "planned"
dependencies: []
subtasks: ["T001", "T002", "T003", "T004", "T005"]
history:
  - date: "2026-03-03"
    event: "created"
    by: "spec-kitty.tasks"
---

# WP01: Protobuf Contract System (phenotype-proto)

**Implementation command**: `spec-kitty implement WP01`

## Objective

Create the `phenotype-proto` repository containing all shared Protobuf type definitions for the Phenotype ecosystem. Configure `buf` for multi-language codegen (Rust, Go, Python, TypeScript) and add CI for lint + breaking change detection.

This is the **critical path foundation** — audit event integration across all 6 repos depends on these proto definitions existing.

## Context

- Currently zero cross-repo type sharing; each repo defines its own session, agent, audit types
- Target: single source of truth in Protobuf, codegen to all 4 languages
- Consumers: all 6 Phenotype repos (heliosCLI, cliproxyapi++, thegent, heliosApp, portage, agentapi++)
- See `kitty-specs/002-phenotype-modular-arch/research.md` Decision 2 and `docs/governance/plugin_architecture_governance.md`

## Subtasks

### T001: Create `phenotype-proto` repo with buf config

**Purpose**: Bootstrap the proto repo with buf.build toolchain.

**Steps**:
1. Create new repo `phenotype-proto` (GitHub via `gh repo create`)
2. Initialize `buf.yaml` at repo root:
   ```yaml
   version: v2
   modules:
     - path: proto
   lint:
     use:
       - STANDARD
   breaking:
     use:
       - FILE
   ```
3. Create directory structure:
   ```
   phenotype-proto/
   ├── proto/
   │   ├── domain/v1/    # Domain types
   │   └── plugin/v1/    # Plugin contracts
   ├── buf.yaml
   ├── buf.gen.yaml      # Codegen config (T004)
   ├── buf.lock
   └── README.md
   ```
4. Add `.gitignore` for generated output dirs (`gen/`)

**Files**: New repo — all files new
**Validation**: `buf lint` passes on empty proto structure

### T002: Define domain/v1/ protos

**Purpose**: Define shared domain types used across all repos.

**Steps**:
1. Create `proto/domain/v1/session.proto`:
   ```protobuf
   syntax = "proto3";
   package domain.v1;

   message Session {
     string id = 1;
     string agent_id = 2;
     SessionStatus status = 3;
     google.protobuf.Timestamp created_at = 4;
     google.protobuf.Timestamp updated_at = 5;
     map<string, string> metadata = 6;
   }

   enum SessionStatus {
     SESSION_STATUS_UNSPECIFIED = 0;
     SESSION_STATUS_ACTIVE = 1;
     SESSION_STATUS_COMPLETED = 2;
     SESSION_STATUS_FAILED = 3;
   }
   ```

2. Create `proto/domain/v1/agent.proto`:
   - `Agent` message: id, name, type (enum: codex, helios, cursor, crew, etc.), capabilities, config
   - `AgentCapability` enum

3. Create `proto/domain/v1/routing.proto`:
   - `RoutingRule` message: id, agent_id, pattern, priority, conditions
   - `RoutingDecision` message: selected_agent, reason, latency_ms

4. Create `proto/domain/v1/audit.proto`:
   - `AuditEvent` message: id, timestamp, source_repo, event_type, actor, payload (google.protobuf.Any), correlation_id, parent_event_id
   - `EventType` enum: SESSION_CREATED, SESSION_COMPLETED, AGENT_ROUTED, TOOL_EXECUTED, TRIAL_STARTED, TRIAL_COMPLETED, etc.
   - This is the **core event schema** consumed by WP12

**Files**:
- `proto/domain/v1/session.proto` (~40 lines)
- `proto/domain/v1/agent.proto` (~50 lines)
- `proto/domain/v1/routing.proto` (~35 lines)
- `proto/domain/v1/audit.proto` (~60 lines)

**Validation**: `buf lint` passes on all domain protos

### T003: Define plugin/v1/ protos

**Purpose**: Define plugin contract types for the two-tier plugin architecture.

**Steps**:
1. Create `proto/plugin/v1/executor.proto`:
   - `ExecutorContract` message: name, version, supported_models, capabilities
   - `ExecuteRequest` / `ExecuteResponse` messages
   - `StreamChunk` message for streaming responses

2. Create `proto/plugin/v1/tool.proto`:
   - `ToolSpec` message: name, description, parameters (JSON schema as string), return_type
   - `ToolInvocation` / `ToolResult` messages

3. Create `proto/plugin/v1/adapter.proto`:
   - `AdapterContract` message: name, version, port_type, capabilities
   - `AdapterHealth` message for lifecycle management

**Files**:
- `proto/plugin/v1/executor.proto` (~70 lines)
- `proto/plugin/v1/tool.proto` (~50 lines)
- `proto/plugin/v1/adapter.proto` (~40 lines)

**Validation**: `buf lint` passes; no breaking changes detected

### T004: Configure buf generate for 4 languages

**Purpose**: Set up codegen so `buf generate` produces idiomatic types in Rust (prost), Go (protoc-gen-go), Python (betterproto), TypeScript (ts-proto).

**Steps**:
1. Create `buf.gen.yaml`:
   ```yaml
   version: v2
   managed:
     enabled: true
     override:
       - file_option: go_package_prefix
         value: github.com/KooshaPari/phenotype-proto/gen/go
   plugins:
     - remote: buf.build/protocolbuffers/go
       out: gen/go
       opt: paths=source_relative
     - remote: buf.build/community/neoeinstein-prost
       out: gen/rust
     - local: protoc-gen-ts_proto
       out: gen/ts
       opt:
         - outputServices=false
         - esModuleInterop=true
     - local: python-betterproto
       out: gen/python
   ```
2. Run `buf generate` and verify output in `gen/{go,rust,ts,python}/`
3. Ensure generated types compile in each language (basic smoke test)
4. Add `gen/` to `.gitignore` — consumers run `buf generate` themselves or consume published packages

**Files**: `buf.gen.yaml` (~30 lines)
**Validation**: `buf generate` succeeds; generated Go compiles with `go build`, Rust with `cargo check`, TS with `tsc`, Python with `python -c "import ..."`

### T005: CI: buf lint + buf breaking

**Purpose**: Prevent proto regressions.

**Steps**:
1. Create `.github/workflows/proto-ci.yml`:
   - Trigger on push/PR to `main`
   - Steps: checkout, install buf, `buf lint`, `buf breaking --against .git#branch=main`
   - Add `buf generate` step to verify codegen works
2. Add branch protection requiring this workflow

**Files**: `.github/workflows/proto-ci.yml` (~40 lines)
**Validation**: CI passes on initial commit; intentional breaking change is caught

## Definition of Done

- [ ] phenotype-proto repo exists on GitHub with all proto files
- [ ] `buf lint` passes with zero warnings
- [ ] `buf generate` produces compilable types in all 4 languages
- [ ] CI workflow runs lint + breaking checks on every PR
- [ ] README documents repo purpose, structure, and usage

## Risks

- **betterproto Python codegen quality**: May need to fall back to standard protoc-gen-python if betterproto has issues. Test early.
- **ts-proto configuration**: Many options; ensure esModuleInterop and paths match heliosApp's tsconfig.
- **prost Rust codegen**: Ensure generated types derive Serialize/Deserialize if needed (may need prost-serde or manual impls).

## Reviewer Guidance

- Verify proto field numbering follows conventions (no gaps, no reuse)
- Check that AuditEvent schema is general enough for all 6 repos' event types
- Ensure buf.gen.yaml plugins are pinned to specific versions for reproducibility
