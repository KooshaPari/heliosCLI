# Performance Optimization WBS (Work Breakdown Structure)

**Phase 1: Memory Safety & Leak Prevention**
**Duration**: Weeks 1-2 (10 days)

---

## 1.1 Subprocess Resource Management (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 1.1.1 | Audit all Popen calls in codebase | Backend | 2h |
| 1.1.2 | Create context manager wrapper for Popen | Backend | 4h |
| 1.1.3 | Add finally blocks to impl.py | Backend | 2h |
| 1.1.4 | Add finally blocks to run_execution_core | Backend | 2h |
| 1.1.5 | Add finally blocks to cli_git_log_ops | Backend | 2h |
| 1.1.6 | Add FD count metrics to benchmark | Backend | 2h |
| 1.1.7 | Code review and merge | Backend | 2h |

---

## 1.2 HTTP Connection Pooling (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 1.2.1 | Create shared httpx.Client singleton | Backend | 3h |
| 1.2.2 | Implement connection pool limits | Backend | 2h |
| 1.2.3 | Add keep-alive configuration | Backend | 1h |
| 1.2.4 | Update all HTTP calls to use pool | Backend | 4h |
| 1.2.5 | Add connection metrics | Backend | 2h |
| 1.2.6 | Test and verify | Backend | 2h |

---

## 1.3 Bounded Cache Implementation (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 1.3.1 | Audit existing caches (TTLCache, etc) | Backend | 2h |
| 1.3.2 | Implement BoundedCache class | Backend | 4h |
| 1.3.3 | Add max_size enforcement | Backend | 2h |
| 1.3.4 | Migrate TeammateManager to bounded | Backend | 4h |
| 1.3.5 | Add cache hit/miss metrics | Backend | 2h |
| 1.3.6 | Document cache eviction policy | Backend | 1h |

---

## 1.4 Memory Profiling in Benchmark (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 1.4.1 | Add memory_profiler to dependencies | DevOps | 1h |
| 1.4.2 | Instrument benchmark runner | Backend | 3h |
| 1.4.3 | Add @profile decorators to key funcs | Backend | 2h |
| 1.4.4 | Generate memory reports | Backend | 2h |
| 1.4.5 | Integrate with CI pipeline | DevOps | 4h |
| 1.4.6 | Document interpretation guide | Backend | 2h |

---

## 1.5 Leak Detection in CI (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 1.5.1 | Add leak detection test suite | DevOps | 3h |
| 1.5.2 | Implement subprocess leak test | Backend | 3h |
| 1.5.3 | Implement FD leak test | Backend | 3h |
| 1.5.4 | Add to GitHub Actions | DevOps | 3h |
| 1.5.5 | Configure alerts on failure | DevOps | 2h |

---

# Phase 2: CPU Optimization & Profiling
**Duration**: Weeks 3-4 (10 days)

---

## 2.1 Perf Profiling Integration (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 2.1.1 | Create perf profiling script | DevOps | 3h |
| 2.1.2 | Add to benchmark runner | Backend | 3h |
| 2.1.3 | Configure flamegraph output | DevOps | 2h |
| 2.1.4 | Add to CI for release builds | DevOps | 4h |
| 2.1.5 | Document interpretation | Backend | 2h |

---

## 2.2 Instruments Profiling (macOS) (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 2.2.1 | Create Instruments trace template | DevOps | 3h |
| 2.2.2 | Add time profiler to benchmark | Backend | 4h |
| 2.2.3 | Add allocations profiler | Backend | 3h |
| 2.2.4 | Document macOS profiling guide | Backend | 4h |

---

## 2.3 Async Event Loop Reuse (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 2.3.1 | Audit all asyncio.run() calls | Backend | 2h |
| 2.3.2 | Create AsyncRunner singleton | Backend | 4h |
| 2.3.3 | Refactor apps to use shared loop | Backend | 6h |
| 2.3.4 | Add lifecycle management | Backend | 4h |
| 2.3.5 | Test concurrent operations | Backend | 2h |

---

## 2.4 CPU Hotspot Detection in CI (1 day)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 2.4.1 | Create hotspot detection script | DevOps | 3h |
| 2.4.2 | Add threshold alerts | DevOps | 2h |
| 2.4.3 | Configure in CI pipeline | DevOps | 3h |

---

## 2.5 SIMD JSON Parsing (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 2.5.1 | Benchmark current JSON parsing | Backend | 2h |
| 2.5.2 | Add simd-json dependency | Backend | 2h |
| 2.5.3 | Implement SIMD parser wrapper | Backend | 4h |
| 2.5.4 | Benchmark comparison | Backend | 2h |
| 2.5.5 | Document when to use | Backend | 2h |

---

# Phase 3: Network & Latency Optimization
**Duration**: Weeks 5-6 (10 days)

---

## 3.1 HTTP Connection Pooling (2 days) [Already in Phase 1.2]

---

## 3.2 Request Batching (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 3.2.1 | Identify batchable API calls | Backend | 2h |
| 3.2.2 | Implement batch queue | Backend | 4h |
| 3.2.3 | Add flush timeout | Backend | 2h |
| 3.2.4 | Update LLM client to use batching | Backend | 6h |
| 3.2.5 | Benchmark improvement | Backend | 2h |
| 3.2.6 | Document usage | Backend | 2h |

---

## 3.3 Response Streaming (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 3.3.1 | Audit non-streaming endpoints | Backend | 2h |
| 3.3.2 | Implement streaming handler | Backend | 6h |
| 3.3.3 | Add backpressure handling | Backend | 4h |
| 3.3.4 | Update benchmark to measure | Backend | 2h |
| 3.3.5 | Test with LLM API | Backend | 2h |

---

## 3.4 Circuit Breakers (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 3.4.1 | Implement CircuitBreaker class | Backend | 4h |
| 3.4.2 | Add failure tracking | Backend | 2h |
| 3.4.3 | Implement state machine | Backend | 3h |
| 3.4.4 | Add to all external API calls | Backend | 5h |
| 3.4.5 | Configure thresholds | Backend | 2h |
| 3.4.6 | Add monitoring dashboard | DevOps | 2h |

---

# Phase 4: Multi-Agent Orchestration
**Duration**: Weeks 7-10 (20 days)

---

## 4.1 Teammate Registry (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.1.1 | Design Teammate data model | Backend | 3h |
| 4.1.2 | Implement TeammateRegistry class | Backend | 6h |
| 4.1.3 | Add CRUD operations | Backend | 4h |
| 4.1.4 | Implement persistence | Backend | 4h |
| 4.1.5 | Add query capabilities | Backend | 3h |
| 4.1.6 | Write tests | Backend | 4h |
| 4.1.7 | Document API | Backend | 2h |

---

## 4.2 Delegation Protocol (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.2.1 | Design delegation message format | Backend | 3h |
| 4.2.2 | Implement DelegationProtocol class | Backend | 6h |
| 4.2.3 | Add async delegation support | Backend | 4h |
| 4.2.4 | Implement timeout handling | Backend | 4h |
| 4.2.5 | Add result aggregation | Backend | 4h |
| 4.2.6 | Write tests | Backend | 3h |

---

## 4.3 Codex CLI Executor (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.3.1 | Design Executor interface | Backend | 3h |
| 4.3.2 | Implement CodexExecutor class | Backend | 8h |
| 4.3.3 | Add process management | Backend | 4h |
| 4.3.4 | Implement output streaming | Backend | 4h |
| 4.3.5 | Add error handling | Backend | 3h |
| 4.3.6 | Write integration tests | Backend | 4h |

---

## 4.4 Circuit Breaker Coordination (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.4.1 | Extend CircuitBreaker for agents | Backend | 4h |
| 4.4.2 | Add per-agent state tracking | Backend | 4h |
| 4.4.3 | Implement cross-agent failures | Backend | 4h |
| 4.4.4 | Add recovery coordination | Backend | 4h |

---

## 4.5 Queue-Based Execution (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.5.1 | Implement TaskQueue class | Backend | 5h |
| 4.5.2 | Add priority support | Backend | 3h |
| 4.5.3 | Implement backpressure | Backend | 4h |
| 4.5.4 | Add persistence | Backend | 4h |
| 4.5.5 | Write tests | Backend | 2h |

---

## 4.6 Bulkhead Pattern (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.6.1 | Implement Bulkhead class | Backend | 4h |
| 4.6.2 | Add thread pool isolation | Backend | 4h |
| 4.6.3 | Implement resource limits | Backend | 4h |
| 4.6.4 | Add monitoring | Backend | 2h |
| 4.6.5 | Write tests | Backend | 2h |

---

## 4.7 Fan-Out to Subagents (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.7.1 | Design fan-out protocol | Backend | 3h |
| 4.7.2 | Implement FanOutExecutor | Backend | 6h |
| 4.7.3 | Add result aggregation | Backend | 4h |
| 4.7.4 | Implement error handling | Backend | 4h |
| 4.7.5 | Add load balancing | Backend | 4h |
| 4.7.6 | Benchmark parallel execution | Backend | 3h |

---

## 4.8 Dynamic Subagent Spawning (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 4.8.1 | Design Subagent lifecycle | Backend | 3h |
| 4.8.2 | Implement SubagentPool | Backend | 8h |
| 4.8.3 | Add isolation (sandbox) | Backend | 6h |
| 4.8.4 | Implement resource limits | Backend | 4h |
| 4.8.5 | Add cleanup on exit | Backend | 3h |
| 4.8.6 | Write tests | Backend | 4h |

---

# Phase 5: Context Engineering
**Duration**: Weeks 11-14 (20 days)

---

## 5.1 File Buffering System (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 5.1.1 | Design ScratchpadFileSystem | Backend | 4h |
| 5.1.2 | Implement write_file tool | Backend | 5h |
| 5.1.3 | Implement read_file tool | Backend | 4h |
| 5.1.4 | Add pointer management | Backend | 3h |
| 5.1.5 | Implement auto-cleanup | Backend | 3h |
| 5.1.6 | Write tests | Backend | 3h |

---

## 5.2 Context Compaction Engine (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 5.2.1 | Design CompactionStrategy interface | Backend | 3h |
| 5.2.2 | Implement Summarizer | Backend | 6h |
| 5.2.3 | Implement PriorityFilter | Backend | 4h |
| 5.2.4 | Add window management | Backend | 5h |
| 5.2.5 | Implement incremental compaction | Backend | 4h |
| 5.2.6 | Benchmark token reduction | Backend | 2h |

---

## 5.3 Planning → Execution Separation (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 5.3.1 | Design Planner interface | Backend | 3h |
| 5.3.2 | Implement make_plan tool | Backend | 6h |
| 5.3.3 | Implement execute_step tool | Backend | 5h |
| 5.3.4 | Add dynamic update_plan tool | Backend | 5h |
| 5.3.5 | Add plan state management | Backend | 3h |
| 5.3.6 | Write integration tests | Backend | 2h |

---

## 5.4 Verification Loops (3 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 5.4.1 | Design Verifier interface | Backend | 3h |
| 5.4.2 | Implement SchemaValidator | Backend | 4h |
| 5.4.3 | Implement TestRunner | Backend | 6h |
| 5.4.4 | Add retry logic | Backend | 4h |
| 5.4.5 | Implement escalation path | Backend | 3h |
| 5.4.6 | Write tests | Backend | 4h |

---

## 5.5 Dynamic Plan Updates (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 5.5.1 | Implement plan version tracking | Backend | 4h |
| 5.5.2 | Add diff detection | Backend | 4h |
| 5.5.3 | Implement re-planning trigger | Backend | 4h |
| 5.5.4 | Add to benchmark | Backend | 2h |

---

## 5.6 Session Persistence (2 days)

### Tasks
| ID | Subtask | Owner | Hours |
|----|---------|-------|-------|
| 5.6.1 | Design SessionStore interface | Backend | 3h |
| 5.6.2 | Implement FileSessionStore | Backend | 5h |
| 5.6.3 | Add serialization | Backend | 4h |
| 5.6.4 | Implement resume logic | Backend | 4h |
| 5.6.5 | Write tests | Backend | 2h |

---

# Summary

| Phase | Days | Tasks | Total Hours |
|-------|------|-------|-------------|
| Phase 1 | 10 | 30 | ~120h |
| Phase 2 | 10 | 24 | ~100h |
| Phase 3 | 10 | 20 | ~90h |
| Phase 4 | 20 | 46 | ~200h |
| Phase 5 | 16 | 37 | ~160h |
| **Total** | **66** | **157** | **~670h** |

**Estimated**: ~17 weeks (4 months) for full implementation

---

*WBS created 2026-02-23*
