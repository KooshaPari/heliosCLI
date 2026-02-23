# Functional Requirements: Teammate Subagent System + Dynamic Scaling

**Version**: 1.0  
**Date**: 2026-02-23  
**Project**: heliosHarness

---

## Table of Contents

1. [Teammate System Requirements](#teammate-system-requirements)
2. [Dynamic Scaling Requirements](#dynamic-scaling-requirements)
3. [Coordination Requirements](#coordination-requirements)
4. [Observability Requirements](#observability-requirements)
5. [Non-Functional Requirements](#non-functional-requirements)

---

## Teammate System Requirements

### FR-101: Teammate Registry
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-101.1 | System shall support auto-discovery of teammates from `agents/` directory | MUST | Teammates discovered automatically on startup |
| FR-101.2 | System shall support YAML configuration for teammate definitions | MUST | Valid YAML files load without error |
| FR-101.3 | System shall support at least 4 default roles: coder, reviewer, tester, researcher | MUST | Default teammates available out-of-box |
| FR-101.4 | System shall allow listing all available teammates | MUST | `teammates list` returns all teammates |
| FR-101.5 | System shall allow querying specific teammate by ID | MUST | `teammates info <id>` returns details |

### FR-102: Delegation Protocol
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-102.1 | System shall support async delegation of tasks to teammates | MUST | Delegation returns immediately, executes in background |
| FR-102.2 | System shall support passing context to teammate | MUST | Context files available in teammate workdir |
| FR-102.3 | System shall track delegation status (pending, running, completed, failed) | MUST | Status queryable at any time |
| FR-102.4 | System shall support timeout for delegations | MUST | Delegation fails after timeout if not complete |
| FR-102.5 | System shall support priority levels for delegations | SHOULD | CRITICAL, HIGH, NORMAL, LOW priorities supported |

### FR-103: Codex CLI Integration
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-103.1 | System shall execute Codex CLI commands | MUST | Codex CLI invoked successfully |
| FR-103.2 | System shall provide isolated work directory per teammate | MUST | Each teammate works in separate directory |
| FR-103.3 | System shall capture Codex CLI output | MUST | Output captured and stored |
| FR-103.4 | System shall handle Codex CLI errors gracefully | MUST | Errors captured and reported |
| FR-103.5 | System shall support configurable Codex CLI profiles | SHOULD | Profiles can be specified in config |

---

## Dynamic Scaling Requirements

### FR-201: Resource Monitoring
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-201.1 | System shall monitor CPU utilization | MUST | CPU % reported accurately |
| FR-201.2 | System shall monitor memory utilization | MUST | Memory % reported accurately |
| FR-201.3 | System shall monitor file descriptor count | MUST | FD count reported accurately |
| FR-201.4 | System shall monitor system load average | MUST | Load avg reported accurately |
| FR-201.5 | System shall sample resources at configurable interval | MUST | Default 1-5 seconds, configurable |

### FR-202: Dynamic Limits
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-202.1 | System shall compute dynamic limit based on resources | MUST | Limit adjusts with resource availability |
| FR-202.2 | System shall enforce minimum buffer (5%) | MUST | Never exceeds 95% resource utilization |
| FR-202.3 | System shall support discretionary buffer (15%) | SHOULD | Soft limit for aggressive scaling |
| FR-202.4 | System shall use hysteresis to prevent thrashing | MUST | Upper/lower thresholds + dwell time |
| FR-202.5 | System shall support manual limit override | SHOULD | CLI flag to set fixed limit |

### FR-203: Backpressure
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-203.1 | System shall reject tasks when queue > 75% | MUST | 503 or appropriate error returned |
| FR-203.2 | System shall prioritize critical tasks during backpressure | MUST | CRITICAL always accepted if capacity exists |
| FR-203.3 | System shall implement graceful degradation | SHOULD | Reduce functionality instead of fail |
| FR-203.4 | System shall provide queue metrics | MUST | Size, capacity, load % available |

---

## Coordination Requirements

### FR-301: Circuit Breaker
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-301.1 | System shall track failures per teammate type | MUST | Failure count maintained |
| FR-301.2 | System shall open circuit after threshold | MUST | Fail fast after 5 failures (configurable) |
| FR-301.3 | System shall test recovery in half-open state | MUST | Test after timeout (default 60s) |
| FR-301.4 | System shall close circuit after successes | MUST | Close after 3 successes |

### FR-302: Bulkhead
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-302.1 | System shall isolate CPU-bound tasks | MUST | Separate pool for CPU tasks |
| FR-302.2 | System shall isolate I/O-bound tasks | MUST | Separate pool for I/O tasks |
| FR-302.3 | System shall isolate database tasks | MUST | Separate pool for DB tasks |
| FR-302.4 | System shall reject when bulkhead exhausted | MUST | Appropriate error returned |

### FR-303: Git Coordination
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-303.1 | System shall support private Git index per agent | SHOULD | GIT_INDEX_FILE isolation |
| FR-303.2 | System shall support Git worktrees | SHOULD | Full directory isolation |
| FR-303.3 | System shall detect conflicts | MUST | Conflicts identified before merge |
| FR-303.4 | System shall support AST-aware merge | SHOULD | Mergiraf integration |

---

## Observability Requirements

### FR-401: Metrics
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-401.1 | System shall export circuit breaker metrics | MUST | State, failures, state changes |
| FR-401.2 | System shall export bulkhead metrics | MUST | Active count, utilization, rejected |
| FR-401.3 | System shall export health metrics | MUST | Uptime, checks passed/failed |
| FR-401.4 | System shall export queue metrics | MUST | Size, capacity, load % |
| FR-401.5 | System shall support Prometheus format | SHOULD | /metrics endpoint available |

### FR-402: Logging
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-402.1 | System shall use structured JSON logging | MUST | JSON format with fields |
| FR-402.2 | System shall log delegation events | MUST | Start, complete, fail logged |
| FR-402.3 | System shall log scaling events | MUST | Scale up/down logged |
| FR-402.4 | System shall log circuit breaker state changes | MUST | State transitions logged |

### FR-403: CLI Commands
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-403.1 | `teammates list` shall list all teammates | MUST | Shows ID, name, role |
| FR-403.2 | `teammates delegate <teammate> <task>` shall delegate | MUST | Returns delegation ID |
| FR-403.3 | `teammates status` shall show swarm status | MUST | Shows active delegations |
| FR-403.4 | `scaling info` shall show dynamic limits | MUST | Shows current limit and resources |
| FR-403.5 | `queue status` shall show queue state | MUST | Shows size, capacity, load % |

---

## Non-Functional Requirements

### Performance
| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Resource sampling latency | < 100ms |
| NFR-2 | Delegation start latency | < 500ms |
| NFR-3 | Status query latency | < 50ms |

### Reliability
| ID | Requirement | Target |
|----|-------------|--------|
| NFR-4 | Uptime | > 99.9% |
| NFR-5 | Graceful degradation | No data loss on overload |

### Security
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-6 | Teammate isolation | MUST |
| NFR-7 | No credential leakage | MUST |

### Robustness
| ID | Requirement | Priority | Target |
|----|-------------|----------|--------|
| NFR-8 | Lazy agent initialization | MUST | Zero overhead when idle |
| NFR-9 | Agent process reuse | MUST | <2MB memory per idle agent |
| NFR-10 | Fast checkpoint/restore | MUST | <1s recovery |
| NFR-11 | Cascading cancellation | SHOULD | Cancel children on parent cancel |
| NFR-12 | Circuit breaker per teammate | MUST | Prevent cascade failures |
| NFR-13 | Input sanitization | MUST | Prevent injection |

### Performance Budgets
| ID | Operation | Target | Max |
|----|-----------|--------|-----|
| NFR-14 | Delegate start | <100ms | <500ms |
| NFR-15 | Status query | <10ms | <50ms |
| NFR-16 | Queue enqueue | <5ms | <20ms |
| NFR-17 | Resource sample | <50ms | <100ms |

### Optimization
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-18 | Lock-free queue operations | SHOULD |
| NFR-19 | Connection pooling | SHOULD |
| NFR-20 | Batch resource sampling | SHOULD |

### Resource Management
| ID | Requirement | Priority | Threshold |
|----|-------------|----------|------------|
| NFR-21 | FD limit per agent | MUST | 100 soft, 1000 hard |
| NFR-22 | FD monitoring | MUST | Alert at 80% |
| NFR-23 | Memory limit per agent | MUST | 256MB RSS max |
| NFR-24 | Memory pressure handling | MUST | Scale down at 90% |
| NFR-25 | Leak detection | MUST | FD + memory tracking |
| NFR-26 | Process health monitoring | MUST | Check every 10s |
| NFR-27 | Zombie process prevention | MUST | Reap within 5s |
| NFR-28 | Thread limit per agent | MUST | 50 max |

### Monitoring
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-29 | Real-time resource dashboard | SHOULD |
| NFR-30 | Historical resource graphs | SHOULD |
| NFR-31 | Alert on resource anomaly | SHOULD |

### Caching & Pre-warming
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-32 | Multi-level cache (L1/L2) | SHOULD |
| NFR-33 | Predictive pre-warming | SHOULD |
| NFR-34 | Frecency cache | SHOULD |
| NFR-35 | Request coalescing | SHOULD |

### Workflow Integration
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-36 | NATS JetStream support | SHOULD |
| NFR-37 | Temporal workflow integration | SHOULD |
| NFR-38 | Durable task execution | SHOULD |

### Network Optimization
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-39 | Connection pooling | SHOULD |
| NFR-40 | HTTP/2 multiplexing | SHOULD |
| NFR-41 | Request batching | SHOULD |
| NFR-42 | Adaptive timeouts | SHOULD |

---

**Document Version**: 1.2  
**Status**: Approved for Implementation
