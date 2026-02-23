# ADR-001: Teammate System Architecture

**Date**: 2026-02-23  
**Status**: Proposed  
**Author**: heliosHarness Team

## Context

We need to implement a teammate/subagent system in heliosHarness, inspired by Claude Code's teammates feature and adapted for Codex CLI. This system must support:
- Multiple specialized teammates (coder, reviewer, tester, researcher)
- Async delegation with status tracking
- Safe multi-agent coordination
- Resource-aware execution

## Decision

We will implement a **Registry + Delegation Protocol + Executor** architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    TeammateManager                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │   Teammate  │  │ Delegation  │  │  Codex CLI     │  │
│  │  Registry   │──│  Protocol   │──│   Executor     │  │
│  └─────────────┘  └─────────────┘  └────────────────┘  │
│         │                │                  │            │
│         ▼                ▼                  ▼            │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Coordination Layer                  │    │
│  │  (Circuit Breaker, Bulkhead, Queue)            │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Consequences

### Positive
- Clear separation of concerns
- Extensible for future executor types (not just Codex)
- Testable components in isolation
- Follows proven patterns from thegent

### Negative
- Additional complexity vs. simple implementation
- Requires careful coordination to avoid conflicts

### Neutral
- May need to adjust based on Codex CLI API evolution

## Alternatives Considered

1. **Direct Codex CLI invocation** - Simpler but less flexible
2. **MCP-based subagents** - More complex setup, better isolation
3. **Full thegent integration** - Would require tight coupling

## References

- TEAMMATES_RESEARCH_AND_PLAN.md (thegent)
- Codex CLI subagent research (web)
