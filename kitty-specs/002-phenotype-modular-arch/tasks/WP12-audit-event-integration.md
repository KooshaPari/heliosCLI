---
work_package_id: WP12
title: Audit Event Integration (All Repos)
lane: planned
dependencies: []
subtasks: [T014, T023, T032, T041, T047]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP12: Audit Event Integration (All Repos)

**Implementation command**: `spec-kitty implement WP12 --base WP01`

## Objective

Emit structured audit events from all 6 repos using the shared AuditEvent schema from phenotype-proto. Each repo emits events at its key state-changing operations.

## Context

- AuditEvent proto defined in WP01 (`proto/domain/v1/audit.proto`)
- Each repo consumes generated types via buf codegen
- Events follow CQRS pattern — write-side only (read-side aggregation in WP15)
- See `kitty-specs/002-phenotype-modular-arch/spec.md` FR-5

## Subtasks

### T014: heliosCLI — session lifecycle audit events

**Repo**: heliosCLI (Rust)

**Steps**:
1. Add `phenotype-proto` generated Rust types as dependency (via `phenotype-rs-protocol` or direct prost include)
2. Emit events at key lifecycle points in codex-core:
   - `SessionCreated` — when a new coding session starts
   - `ToolExecuted` — when a tool is invoked
   - `SessionCompleted` / `SessionFailed` — on session end
3. Create `audit/` module:
   - `emitter.rs` — `AuditEmitter` trait + stdout/file implementations
   - `events.rs` — helper functions to construct AuditEvent with correct fields
4. Wire emitter into session manager

**Validation**: Running a coding session produces audit events in structured format

### T023: cliproxyapi++ — routing audit events

**Repo**: cliproxyapi++ (Go)

**Steps**:
1. Add phenotype-proto generated Go types
2. Emit events at routing decisions:
   - `RequestReceived` — incoming proxy request
   - `ExecutorSelected` — routing decision made
   - `ResponseForwarded` — response sent to client
   - `ExecutorFailed` — executor error with fallback/retry info
3. Create `internal/audit/` package:
   - `emitter.go` — AuditEmitter interface + implementations
   - `events.go` — event construction helpers
4. Wire into request handler middleware

**Validation**: Proxied requests produce audit trail

### T032: thegent — agent execution audit events

**Repo**: thegent (Python)

**Steps**:
1. Add phenotype-proto generated Python types (betterproto)
2. Emit events at agent execution lifecycle:
   - `AgentStarted` — agent begins execution
   - `StepExecuted` — individual step completed
   - `GovernanceDecision` — policy engine decision (approve/escalate/deny)
   - `AgentCompleted` / `AgentFailed` — execution end
3. Create `thegent-audit/emitter.py`:
   - `AuditEmitter` protocol + implementations
4. Wire into run execution core

**Validation**: Agent execution produces structured audit events

### T041: portage — trial execution audit events

**Repo**: portage (Python)

**Steps**:
1. Add phenotype-proto generated Python types
2. Emit events:
   - `TrialStarted` — benchmark trial begins
   - `TrialCheckpoint` — intermediate measurement
   - `TrialCompleted` — trial finishes with results
3. Wire into trial execution engine

**Validation**: Running a benchmark trial produces audit events

### T047: agentapi++ — routing audit events

**Repo**: agentapi++ (Go)

**Steps**:
1. Add phenotype-proto generated Go types
2. Emit events:
   - `AgentRouted` — request routed to agent
   - `SessionCreated` — new session established
3. Wire into request handlers

**Validation**: API requests produce audit events

## Definition of Done

- [ ] All 5 repos emit structured AuditEvent following the proto schema
- [ ] Events include correlation_id for cross-repo tracing
- [ ] Each repo's emitter is behind an interface (swappable backends)
- [ ] Events are parseable by @helios/audit-core (WP15)
- [ ] Existing tests pass in all repos

## Risks

- **Proto codegen in each language**: Ensure generated types work correctly in each ecosystem. Test imports early.
- **Event volume**: Audit emitters should support async/batched emission to avoid performance impact.
- **Correlation ID propagation**: Need convention for passing correlation IDs across service boundaries (HTTP headers, gRPC metadata).

## Reviewer Guidance

- Verify event types cover the key state changes per repo
- Check correlation_id is propagated at service boundaries
- Ensure emitter implementations are non-blocking (don't slow down hot paths)
- Verify proto imports work correctly in each language
