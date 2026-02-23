# User Stories: Teammate Subagent System + Dynamic Scaling

**Version**: 1.0  
**Date**: 2026-02-23  
**Project**: heliosHarness

---

## Table of Contents

1. [Developer Stories](#developer-stories)
2. [Operator Stories](#operator-stories)
3. [System Stories](#system-stories)

---

## Developer Stories

### US-101: Discover Available Teammates
**As a** developer  
**I want to** see all available teammate agents  
**So that** I know who I can delegate to

**Acceptance Criteria:**
- [ ] `harness teammates list` shows all teammates
- [ ] Each teammate shows name, role, description
- [ ] Teammates auto-discovered from `agents/` directory

**Example:**
```
$ harness teammates list
Available Teammates:
  • code-reviewer: Reviews code for bugs and style
  • test-writer: Writes unit and integration tests
  • security-auditor: Checks for security vulnerabilities
  • doc-generator: Generates documentation
```

---

### US-102: Delegate Task to Teammate
**As a** developer  
**I want to** delegate a subtask to a specialized teammate  
**So that** I can focus on high-level work while the teammate handles the details

**Acceptance Criteria:**
- [ ] `harness teammates delegate <teammate> <task>` creates delegation
- [ ] Delegation returns immediately with delegation ID
- [ ] Teammate executes in background
- [ ] Result available when complete

**Example:**
```
$ harness teammates delegate code-reviewer "Review the auth module"
Delegation created: del-abc123
Use 'harness teammates status del-abc123' to check progress
```

---

### US-103: Monitor Delegation Status
**As a** developer  
**I want to** check the status of my delegations  
**So that** I know what's running and what's done

**Acceptance Criteria:**
- [ ] `harness teammates status` shows all active delegations
- [ ] Status shows: pending, running, completed, failed
- [ ] Failed delegations show error message
- [ ] Completed delegations show result summary

**Example:**
```
$ harness teammates status
Active Delegations:
  del-abc123: code-reviewer - RUNNING (2m 34s)
  del-def456: test-writer - COMPLETED ✓
  del-ghi789: security-auditor - FAILED ✗ (timeout)
```

---

### US-104: Pass Context to Teammate
**As a** developer  
**I want to** provide context files to the teammate  
**So that** the teammate has relevant information

**Acceptance Criteria:**
- [ ] `-c/--context` flag accepts files or directories
- [ ] Context copied to teammate's work directory
- [ ] Multiple context sources supported

**Example:**
```
$ harness teammates delegate code-reviewer "Review auth" -c src/auth/ -c docs/api.md
```

---

### US-105: Set Timeout for Delegation
**As a** developer  
I want to set a maximum time for a delegation  
So that long-running tasks don't block indefinitely

**Acceptance Criteria:**
- [ ] `-t/--timeout` flag accepts duration (seconds or "5m")
- [ ] Delegation fails with timeout error if exceeded
- [ ] Default timeout: 30 minutes

**Example:**
```
$ harness teammates delegate test-writer "Write tests" -t 10m
```

---

## Operator Stories

### US-201: View Dynamic Scaling Status
**As an** operator  
**I want to** see the current concurrency limits and why  
**So that** I understand system behavior

**Acceptance Criteria:**
- [ ] `harness scaling info` shows current limit
- [ ] Shows resource utilization (CPU, memory, FD, load)
- [ ] Shows whether scaling is constrained
- [ ] Shows hysteresis state

**Example:**
```
$ harness scaling info
Dynamic Concurrency Limit: 12
  CPU: 45% (threshold: 80%)
  Memory: 62% (threshold: 85%)
  FD: 234/1024 (threshold: 80%)
  Load: 2.3 (threshold: 8.0)
Hysteresis: STABLE (last change: 5m ago)
```

---

### US-202: Monitor Queue Health
**As an** operator  
**I want to** see queue depth and backpressure status  
**So that** I know if system is overloaded

**Acceptance Criteria:**
- [ ] `harness queue status` shows queue metrics
- [ ] Shows current size, capacity, load %
- [ ] Shows if backpressure is active
- [ ] Shows priority distribution

**Example:**
```
$ harness queue status
Queue Status: BACKPRESSURE ACTIVE
  Size: 85/100 (85% capacity)
  HIGH priority: 12
  NORMAL priority: 65
  LOW priority: 8
Backpressure: Rejecting LOW priority tasks
```

---

### US-203: View Circuit Breaker Status
**As an** operator  
**I want to** see circuit breaker state per teammate type  
**So that** I know if teammates are failing

**Acceptance Criteria:**
- [ ] `harness breakers status` shows all breakers
- [ ] Shows state: CLOSED, OPEN, HALF_OPEN
- [ ] Shows failure count
- [ ] Shows time until retry

**Example:**
$ harness breakers status
Circuit Breakers:
  code-reviewer: CLOSED (2 failures, last: 2h ago)
  test-writer: OPEN (threshold: 5, retry in: 45s)
  security-auditor: HALF_OPEN (testing recovery)
```

---

### US-204: View Agent Health
**As an** operator  
**I want to** see health status of all running agents  
**So that** I can detect issues early

**Acceptance Criteria:**
- [ ] `harness health` shows all agents
- [ ] Shows: healthy, slow, unhealthy, crashed
- [ ] Shows response time
- [ ] Shows error count

**Example:**
```
$ harness health
Agent Health:
  agent-001: HEALTHY (resp: 120ms, errors: 0)
  agent-002: SLOW (resp: 2.3s, errors: 2)
  agent-003: UNHEALTHY (resp: timeout, errors: 5)
  agent-004: CRASHED (last: 10m ago)
```

---

## System Stories

### US-301: Auto-Scale Based on Resources
**As the** system  
**I want to** automatically adjust concurrency limits based on available resources  
**So that** I maximize utilization without overloading

**Acceptance Criteria:**
- [ ] Limits increase when resources available
- [ ] Limits decrease when resources constrained
- [ ] Hysteresis prevents rapid oscillation
- [ ] Minimum buffer (5%) always maintained

---

### US-302: Circuit Breaker Protection
**As the** system  
**I want to** stop sending tasks to failing teammates  
**So that** failures don't cascade

**Acceptance Criteria:**
- [ ] After 5 failures, circuit opens
- [ ] Requests fail fast in OPEN state
- [ ] After timeout, circuit half-opens
- [ ] After 3 successes, circuit closes

---

### US-303: Bulkhead Isolation
**As the** system  
**I want to** isolate resource consumption per task type  
**So that** one task type doesn't affect others

**Acceptance Criteria:**
- [ ] CPU tasks limited to CPU pool size
- [ ] I/O tasks limited to I/O pool size
- [ ] DB tasks limited to DB pool size
- [ ] Exhaustion in one pool doesn't affect others

---

### US-304: Graceful Degradation
**As the** system  
**I want to** reduce functionality instead of failing completely  
**So that** critical operations always work

**Acceptance Criteria:**
- [ ] When queue > 75%, reject LOW priority
- [ ] When queue > 90%, reject NORMAL priority
- [ ] CRITICAL always accepted if capacity exists
- [ ] Users receive appropriate error messages

---

## Resource Management Stories

### US-501: View Resource Status
**As an** operator  
**I want to** see current resource usage (CPU, memory, FD)  
**So that** I know if the system is healthy

**Acceptance Criteria:**
- [ ] `harness resources` shows CPU, memory, FD usage
- [ ] Shows per-agent breakdown
- [ ] Shows trends (up/down/stable)

**Example:**
```
$ harness resources
CPU: 45% | Memory: 5.4GB/8GB (68%) | FD: 234/1024 (23%)
```

### US-502: FD Leak Detection
**As an** operator  
**I want to** be alerted if file descriptors are leaking  
**So that** I can prevent system exhaustion

**Acceptance Criteria:**
- [ ] Automatic detection of FD leaks
- [ ] Alert at 80% of limit
- [ ] Auto-cleanup of leaked FDs

### US-503: Memory Pressure Response
**As an** operator  
**I want the system to** automatically scale down when memory is high  
**So that** the system doesn't crash

**Acceptance Criteria:**
- [ ] At 75% memory: warn and slow new work
- [ ] At 90% memory: stop new work, cleanup idle agents
- [ ] At 95% memory: force kill lowest priority agents

### US-504: Zombie Process Prevention
**As an** operator  
**I want** zombie processes to be automatically reaped  
**So that** resources are freed promptly

**Acceptance Criteria:**
- [ ] Detect zombie processes within 5s
- [ ] Automatic reaping
- [ ] Alert on repeated zombie creation

### US-505: Agent Process Health
**As an** operator  
**I want to** see health status of each agent process  
**So that** I know which agents are problematic

**Acceptance Criteria:**
- [ ] Show: HEALTHY, WARNING, CRITICAL per agent
- [ ] Show: memory growth trend
- [ ] Show: FD count per agent
- [ ] Auto-restart of CRITICAL agents

---

## Polish & QoL Stories

## Resource Management Stories

### US-401: Batch Delegation
**As a** developer  
**I want to** delegate the same task to multiple teammates simultaneously  
**So that** I can get parallel reviews/feedback

**Acceptance Criteria:**
- [ ] `--all` flag delegates to all teammates of a role
- [ ] Results aggregated in combined report
- [ ] Individual failures don't block others

**Example:**
```
$ harness teammates delegate --all reviewers "Review the auth module"
```

### US-402: Delegation Templates
**As a** developer  
**I want to** save and reuse delegation patterns  
**So that** I don't repeat myself for common tasks

**Acceptance Criteria:**
- [ ] `teammates template save <name> <template>` saves delegation
- [ ] `teammates template list` shows saved templates
- [ ] `teammates template run <name>` executes saved delegation

**Example:**
```
$ harness teammates template save code-review "Review PR {pr}" --teammate code-reviewer
$ harness teammates template run code-review --var pr=123
```

### US-403: Cascading Cancellation
**As a** developer  
**I want to** cancel a parent delegation and have all children cancelled  
**So that** I don't waste resources on unwanted work

**Acceptance Criteria:**
- [ ] `teammates cancel <id>` cancels delegation and children
- [ ] Confirmation shown before cancellation
- [ ] Partial results preserved for review

### US-404: Smart Retry
**As a** developer  
**I want to** have automatic retry with backoff for failed delegations  
**So that** transient failures don't require manual retry

**Acceptance Criteria:**
- [ ] Automatic retry on transient failures (timeout, rate limit)
- [ ] Exponential backoff (1s, 2s, 4s, 8s...)
- [ ] Max retries configurable (default: 3)
- [ ] `--no-retry` flag to disable

### US-405: Rich Progress Output
**As a** developer  
**I want to** see visual progress for long-running delegations  
**So that** I know something is happening

**Acceptance Criteria:**
- [ ] Spinner/progress bar during execution
- [ ] ETA calculation when possible
- [ ] Color-coded status (green=success, red=fail, yellow=running)

### US-406: Interactive Confirmation
**As a** developer  
**I want to** confirm before destructive operations  
**So that** I don't accidentally cancel important work

**Acceptance Criteria:**
- [ ] Confirmation prompt for cancel operations
- [ ] `--force` flag to skip confirmation
- [ ] `--yes` flag for automated scripts

### US-407: Auto-complete Teammate Names
**As a** developer  
**I want to** have tab-completion for teammate names  
**So that** I don't have to type full names

**Acceptance Criteria:**
- [ ] Shell completion for teammate IDs
- [ ] Fuzzy matching (e.g., "cod" → "code-reviewer")
- [ ] Shows alternatives if ambiguous

---

## Caching & Pre-warming Stories

### US-601: Multi-Level Cache
**As a** developer  
**I want** frequently accessed data to be cached  
**So that** subsequent requests are faster

**Acceptance Criteria:**
- [ ] L1 in-memory cache (TTLCache)
- [ ] L2 disk cache (diskcache)
- [ ] Automatic promotion L2 → L1 on hit
- [ ] Write-through to both levels

### US-602: Predictive Pre-warming
**As an** operator  
**I want** the system to pre-load likely-needed data  
**So that** first requests don't suffer cache misses

**Acceptance Criteria:**
- [ ] Configurable warming strategies
- [ ] Background daemon mode
- [ ] Predicts based on usage patterns

### US-603: Request Coalescing
**As a** developer  
**I want** simultaneous requests for the same resource to be coalesced  
**So that** we don't make duplicate calls

**Acceptance Criteria:**
- [ ] Multiple requests for same key wait for single fetch
- [ ] All waiters receive same result
- [ ] Timeout prevents indefinite wait

---

## Workflow & Integration Stories

### US-701: NATS Event Bus
**As a** architect  
**I want** agents to communicate via NATS  
**So that** we have reliable message delivery

**Acceptance Criteria:**
- [ ] NATS connection configured
- [ ] Publish/subscribe working
- [ ] JetStream for persistence

### US-702: Durable Task Execution
**As a** developer  
**I want** long-running tasks to survive process restarts  
**So that** I don't lose work

**Acceptance Criteria:**
- [ ] Integration with Temporal or similar
- [ ] Automatic retry with backoff
- [ ] Task state persisted

### US-703: Connection Pooling
**As an** operator  
**I want** HTTP connections to be reused  
**So that** we don't exhaust connection limits

**Acceptance Criteria:**
- [ ] Connection pool with limits
- [ ] HTTP/2 multiplexing enabled
- [ ] Graceful cleanup on shutdown

---

**Document Version**: 1.2  
**Status**: Ready for Implementation
