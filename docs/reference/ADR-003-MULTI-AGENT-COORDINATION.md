# ADR-003: Multi-Agent Coordination Strategy

**Date**: 2026-02-23  
**Status**: Proposed  
**Author**: heliosHarness Team

## Context

When multiple teammate agents work concurrently, we need to:
1. Prevent Git lock conflicts
2. Isolate resource consumption
3. Handle conflicts gracefully
4. Ensure result aggregation

## Decision

We will implement a **Layered Coordination Strategy**:

```
┌─────────────────────────────────────────────┐
│            High-Level Coordination           │
│  (Task Queue, Priority, Backpressure)      │
├─────────────────────────────────────────────┤
│            Mid-Level Protection             │
│  (Circuit Breaker, Bulkhead)                │
├─────────────────────────────────────────────┤
│            Low-Level Isolation             │
│  (Git Worktrees, Private Index, Merge)     │
└─────────────────────────────────────────────┘
```

### 1. Task Queue (High-Level)

- Priority-based queue (CRITICAL > HIGH > NORMAL > LOW)
- Backpressure when queue > 75% full
- Graceful degradation: reject lower priority first

### 2. Circuit Breaker & Bulkhead (Mid-Level)

**Circuit Breaker**:
- Track failures per teammate type
- States: CLOSED → OPEN → HALF_OPEN → CLOSED
- Configurable: failure_threshold=5, timeout=60s

**Bulkhead**:
- Separate pools per resource type (CPU, I/O, DB)
- Semaphore-based concurrency control
- Prevents one agent from monopolizing resources

### 3. Git Isolation (Low-Level)

**Option A: Private GIT_INDEX_FILE**
- Each agent uses separate index file
- `GIT_INDEX_FILE=<agent>.index codex exec ...`
- Requires CAS reference updates

**Option B: Git Worktrees**
- Full directory isolation per agent
- `git worktree add <path> <branch>`
- Best for heavy modifications

**Option C: Mergiraf**
- AST-aware conflict resolution
- Better than text-based 3-way merge
- For when both modify same file

## Consequences

### Positive
- Multiple safety nets prevent cascading failures
- Flexible isolation levels (choose appropriate)
- Proven patterns from thegent

### Negative
- Complexity increases with each layer
- Must configure for workload

### Neutral
- Can start simple, add layers as needed

## References

- SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md (thegent)
- DYNAMIC_SCALING_AND_SELF_HEALING_PATTERNS.md (thegent)
