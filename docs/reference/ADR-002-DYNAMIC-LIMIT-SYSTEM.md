# ADR-002: Dynamic Thread Limit System

**Date**: 2026-02-23  
**Status**: Proposed  
**Author**: heliosHarness Team

## Context

The current implementation uses fixed thread/concurrency limits. This leads to:
- Under-utilization when resources available
- Overload when fixed limit too high
- No adaptation to workload changes
- Manual tuning required

We need a dynamic system that:
- Scales with available resources (CPU, memory, FD, load average)
- Uses hysteresis to prevent thrashing
- Provides safety buffers (minimum + discretionary)
- Supports prediction for growth

## Decision

We will implement a **Resource-Based Dynamic Limit System** with hysteresis control:

```
Resources ──▶ Sampling ──▶ Hysteresis ──▶ Limit Calc ──▶ Executor
(CPU, Mem,    (1-5 sec)   Controller    (5% min +    (Semaphore)
 FD, Load)                 (upper/lower)  15% disc)
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| min_buffer | 0.05 | 5% hard limit (prevents crashes) |
| discretionary_buffer | 0.15 | 15% soft limit (allows scaling) |
| hysteresis_upper | 0.80 | Scale up threshold |
| hysteresis_lower | 0.60 | Scale down threshold |
| dwell_time | 30s | Time to wait before changing limit |

### Limit Calculation

```
effective_limit = min(
    running_count,
    floor(available_resources * (1 - min_buffer)),
    floor(available_resources * (1 - discretionary_buffer))
)
```

## Consequences

### Positive
- Automatically scales with system capacity
- Prevents crashes with minimum buffer
- Hysteresis prevents thrashing
- No manual tuning needed
- Proven pattern from thegent (load_based_limits)

### Negative
- Slightly more complex than fixed limits
- Requires reliable resource sampling
- May need tuning for specific workloads

### Neutral
- Platform-specific resource sampling (psutil / native)

## Alternatives Considered

1. **Fixed limit with manual adjustment** - Current approach, not adaptive
2. **Purely reactive (queue-based)** - Doesn't prevent overload
3. **ML-based prediction** - Over-engineered for current needs

## Implementation Notes

- Use `psutil` for cross-platform resource sampling
- Implement `thegent-resources` Rust binary for performance (optional)
- Sample resources every 1-5 seconds
- Apply hysteresis before changing limit

## References

- DYNAMIC_SCALING_AND_SELF_HEALING_PATTERNS.md (thegent)
- load_based_limits_api.md (thegent)
