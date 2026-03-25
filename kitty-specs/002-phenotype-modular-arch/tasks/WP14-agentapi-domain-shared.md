---
work_package_id: WP14
title: 'agentapi++: Domain Extraction + Shared Consumption'
lane: planned
dependencies: []
subtasks: [T045, T046]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP14: agentapi++ — Domain Extraction + Shared Consumption

**Implementation command**: `spec-kitty implement WP14 --base WP07`

## Objective

Extract `internal/domain/` package with formal domain entities from agentapi++. Consume `phenotype-go-authkit` and `phenotype-go-httpkit` shared packages.

## Context

- agentapi++ is small (~3K LOC) — too small for full hexagonal, but needs domain layer
- Auth and HTTP patterns shared with cliproxyapi++ (extracted in WP07)
- See plan.md Lane 6

## Subtasks

### T045: Extract internal/domain/ package

**Steps**:
1. Create `internal/domain/`:
   - `agent.go` — Agent entity with ID, name, type, capabilities
   - `session.go` — Session entity with lifecycle state
   - `routing.go` — RoutingRule, RoutingDecision
   - `benchmark.go` — BenchmarkData (if applicable)
2. Move entity definitions from handler code into domain types
3. Handlers reference domain types instead of inline structs

**Validation**: `go build ./...` passes; handlers use domain types

### T046: Consume shared Go packages

**Steps**:
1. Add dependencies:
   ```
   go get github.com/KooshaPari/phenotype-go-authkit
   go get github.com/KooshaPari/phenotype-go-httpkit
   ```
2. Replace local auth logic with authkit imports
3. Replace local HTTP helpers with httpkit imports
4. Remove duplicated local code

**Validation**: `go build ./...` and `go test ./...` pass

## Definition of Done

- [ ] internal/domain/ package with Agent, Session, RoutingRule entities
- [ ] authkit and httpkit consumed as dependencies
- [ ] No duplicated auth/HTTP code
- [ ] All tests pass

## Reviewer Guidance

- Verify domain types align with phenotype-proto definitions
- Check that shared package versions are pinned
