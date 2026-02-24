# Product Friction Points & Customer Pain Points Analysis

**Date:** 2026-02-23  
**Focus:** Deep dive into customer pain points, product friction

---

## Executive Summary

This document compiles customer complaints, friction points, and product issues from all cloned repositories to inform heliosHarness development priorities.

---

## 1. Goose (block/goose)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| Autonomous mode by default | **Critical** | Dangerous for new users |
| Chat hangs indefinitely | **Critical** | Complete blocker |
| Provider integration failures | High | Z.AI not working |
| Intermittent unresponsiveness | High | Reliability issues |

### Pain Points

1. **Safety First Use** - Autonomous mode enabled by default scares new users
2. **Provider Lock-in** - Custom providers frequently fail
3. **Reliability** - Chats become unresponsive
4. **Onboarding** - No warning about autonomous mode risks

### User Quotes

> "Autonomous mode by default is dangerous for new users who may not read the manual"
> "Chat interface stuck at 'loading conversation...' indefinitely"

---

## 2. KiloCode (Kilo-Org/kilocode)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| File truncation | **Critical** | Data loss |
| Supply chain vulnerability | **Critical** | CVE-2025-11445 |
| Edit failures | High | 80% failure rate |
| Parameter errors | High | Tools unusable |

### Pain Points

1. **Unreliable Edits** - Files truncated/corrupted mid-write
2. **Security** - Prompt injection vulnerability
3. **Tool Failures** - Edit/write operations fail frequently
4. **Provider Issues** - Z.AI integration broken

### User Quotes

> "AI fails to maintain essential syntax during file write operations, stripping required array size initializers"
> "Failure rate has increased" - recurring complaint

---

## 3. OpenCode (anomalyco/opencode)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| Model selection not honored | Medium | Wrong model used |
| API call errors | High | Azure integration fails |
| Client config ignored | High | Cost overruns |

### Pain Points

1. **Model Confusion** - Agent reverts to previous model
2. **Server-Side Override** - Client config ignored
3. **Platform Issues** - WebView crashes on macOS
4. **Cache Corruption** - Requires manual cache clearing

### User Quotes

> "Agent toggle does not honor the agent model specification"
> "Server-side model selection overrides client configurations"

---

## 4. Coder/Mux (coder/mux)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| Subagent discovery broken | High | Custom agents not loaded |
| Platform limitations | Medium | Android/Termux issues |
| Complex setup | Medium | High learning curve |

### Pain Points

1. **Custom Agent Discovery** - Subagents not recognized
2. **Configuration Overhead** - Complex setup required
3. **Platform Gaps** - Not all features work everywhere

---

## 5. Terminus (terminusdb/terminusdb)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| Dashboard deprecated | Low | Feature removed |
| Image size bloat | Medium | Resource heavy |
| Complex configuration | Medium | Steep learning |

### Pain Points

1. **Feature Removal** - Dashboard deprecated
2. **Resource Usage** - Large image sizes
3. **Documentation Gaps** - Hard to navigate

---

## 6. Roo-Code (RooCodeInc/Roo-Code)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| Cloud dependency | High | Privacy concerns |
| Subscription required | High | Cost barrier |
| Security concerns | Medium | Remote execution |

### Pain Points

1. **Cloud Lock-in** - Cloud agents require subscription
2. **Privacy** - Remote execution raises concerns
3. **Complexity** - Too many modes/options

---

## 7. Claude-Flow (ruvnet/claude-flow)

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|---------|
| Complexity overload | High | New users overwhelmed |
| Documentation sprawl | Medium | ADR fatigue |
| Too many options | Medium | Decision paralysis |

### Pain Points

1. **60+ agents** - Choice paralysis
2. **Massive ADR system** - Hard to follow
3. **Steep learning curve** - Enterprise features too complex

---

## Cross-Cutting Pain Points

### Top 10 Friction Points

| Rank | Pain Point | Frequency | Impact |
|------|------------|-----------|--------|
| 1 | **Autonomous by default** | 3 repos | Safety |
| 2 | **Edit/file operation failures** | 3 repos | Reliability |
| 3 | **Provider integration broken** | 3 repos | Functionality |
| 4 | **Model config not honored** | 2 repos | Cost/control |
| 5 | **State management issues** | 2 repos | UX |
| 6 | **Complex setup** | 3 repos | Adoption |
| 7 | **Cache/storage problems** | 2 repos | Performance |
| 8 | **Security vulnerabilities** | 1 repo | Critical |
| 9 | **Documentation gaps** | 2 repos | Onboarding |
| 10 | **Platform inconsistencies** | 2 repos | Reliability |

### Safety Concerns

1. **Autonomous by default** - Goose, general trend
2. **Supply chain attacks** - KiloCode CVE-2025-11445
3. **Prompt injection** - Security implications

### Reliability Concerns

1. **File truncation** - Data loss risk
2. **Chat hangs** - Complete blockers
3. **Provider failures** - Integration broken

---

## heliosHarness Opportunities

### What to Avoid

| Anti-Pattern | Source | Recommendation |
|--------------|--------|-----------------|
| Autonomous default | Goose | Always require explicit opt-in |
| Edit without preview | KiloCode | Always show diff before apply |
| Provider dependency | Multiple | Support fallback providers |
| Complex defaults | Claude-Flow | Opinionated, simple defaults |

### What to Implement

| Feature | Priority | Rationale |
|---------|----------|------------|
| **Diff preview** | Critical | Competitive with Cline |
| **Approval workflow** | Critical | Safety requirement |
| **Provider fallback** | High | Reliability |
| **Simple onboarding** | High | Reduce friction |
| **State isolation** | High | Project separation |

---

## Recommendations

### Safety First

1. **Never autonomous by default** - Always require explicit user action
2. **Preview before apply** - Show diffs, require approval
3. **Provider fallback** - Automatic failover on failure

### Reliability Focus

1. **Test file operations** - Verify write integrity
2. **State isolation** - Clean project boundaries
3. **Error recovery** - Graceful degradation

### UX Simplification

1. **Opinionated defaults** - Reduce choice paralysis
2. **Progressive disclosure** - Simple first, advanced later
3. **Clear feedback** - Status visibility

---

## Action Items

| Priority | Item | Source |
|----------|------|--------|
| 1 | Implement diff preview | KiloCode, Cline |
| 2 | Safe autonomous mode | Goose |
| 3 | Provider fallback | Multiple |
| 4 | Simple onboarding | All |
| 5 | State isolation | OpenCode |

---

## References

- Goose issues: #2806, #5845, #4685
- KiloCode issues: #2547, #2369, #1996
- OpenCode issues: #3550, #5343
- Coder/Mux: Claude Code issues
- CVE-2025-11445 (KiloCode)
