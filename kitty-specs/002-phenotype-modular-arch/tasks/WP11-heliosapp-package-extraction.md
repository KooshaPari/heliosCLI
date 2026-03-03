---
work_package_id: WP11
title: 'heliosApp: Package Extraction + Publishing'
lane: planned
dependencies: []
subtasks: [T034, T035, T036, T037, T038]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP11: heliosApp — Package Extraction + Publishing

**Implementation command**: `spec-kitty implement WP11 --base WP02`

## Objective

Extract `@helios/audit-core`, `@helios/protocol-types`, and `@helios/service-contracts` from heliosApp. Publish to npm/GitHub Packages. Refactor runtime to consume extracted packages.

## Context

- heliosApp (TypeScript) has audit/event-sourcing (~3K LOC), protocol types (~1K LOC), service interfaces
- These are reusable beyond heliosApp — audit-core especially (consumed by portage viewer, agentapi++)
- Shared TS repos scaffolded in WP02

## Subtasks

### T034: Extract @helios/audit-core

**Steps**:
1. Identify audit code in `apps/runtime/src/audit/`:
   - AuditEvent types, Ledger, SQLiteStore, ReplayEngine, Snapshot
2. Copy to `helios-audit-core/src/`:
   - `event.ts` — AuditEvent, EventType
   - `ledger.ts` — Ledger, append-only event store
   - `store.ts` — SQLiteStore (or abstract StoragePort)
   - `replay.ts` — ReplayEngine, snapshot management
3. Ensure no heliosApp-internal imports (Electron, UI, etc.)
4. Export all from `src/index.ts`

**Validation**: `pnpm build` succeeds; types exported correctly

### T035: Extract @helios/protocol-types

**Steps**:
1. Identify protocol types in `apps/runtime/src/protocol/types.ts`:
   - Envelope, Command, Event, Response types
2. Copy to `helios-protocol-types/src/`
3. Ensure alignment with phenotype-proto generated TS types (WP01)

**Validation**: `pnpm build` and `tsc --noEmit` pass

### T036: Extract @helios/service-contracts

**Steps**:
1. Identify service interfaces in runtime:
   - Service boundaries for agent, session, routing, audit
2. Create `helios-service-contracts/src/`:
   - Interface definitions (not implementations)
   - Shared error types
3. This enables hexagonal architecture in heliosApp runtime

**Validation**: `pnpm build` passes; interfaces exported

### T037: Publish packages

**Steps**:
1. Configure npm scope `@helios` (GitHub Packages or npm registry)
2. Add `publishConfig` to each package.json
3. Publish v0.1.0 of each package
4. Verify packages installable: `pnpm add @helios/audit-core@0.1.0`

**Validation**: Packages installable from registry

### T038: Refactor runtime to consume packages

**Steps**:
1. In heliosApp, add dependencies on published packages
2. Replace local imports with package imports:
   ```typescript
   // Before: import { AuditEvent } from '../audit/event'
   // After:  import { AuditEvent } from '@helios/audit-core'
   ```
3. Remove extracted source files from heliosApp
4. Run full test suite

**Validation**: heliosApp builds and all tests pass with external packages

## Definition of Done

- [ ] 3 packages extracted and published
- [ ] heliosApp consumes packages as dependencies
- [ ] No duplicated code between heliosApp and packages
- [ ] All heliosApp tests pass
- [ ] Package CI workflows green

## Risks

- **Circular deps**: audit-core may reference protocol-types. Define clear dep direction: protocol-types → audit-core (audit-core depends on protocol-types, not vice versa).
- **Electron-specific code**: Ensure no Electron APIs leak into shared packages.

## Reviewer Guidance

- Verify packages have no Electron/browser-specific imports
- Check dependency direction between the 3 packages
- Ensure published package versions are pinned in heliosApp
