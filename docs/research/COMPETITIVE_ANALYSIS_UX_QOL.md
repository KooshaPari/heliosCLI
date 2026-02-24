# Competitive Analysis: AI Agent Tools Research

**Date:** 2026-02-23  
**Focus:** QOL features, UX patterns, customer pain points

---

## Executive Summary

This document analyzes leading AI coding agents for UX patterns, QOL features, and customer pain points to inform heliosHarness development.

---

## 1. Claude-Flow (ruvnet)

### Overview
- **Type:** Multi-agent orchestration platform
- **Architecture:** 64+ specialized agents in swarm topologies
- **Target:** Enterprise-grade multi-agent workflows

### Key Features

| Feature | Description |
|---------|-------------|
| **Swarm Topologies** | Mesh, hierarchical, ring, star patterns |
| **Consensus Protocols** | Raft, BFT, Gossip, CRDT |
| **Memory Layer** | AgentDB for persistent storage |
| **MCP Protocol** | Native Claude Code support |
| **Self-Learning** | RuVector intelligence layer |
| **60+ Specialized Agents** | Role-based (coders, reviewers, testers) |

### UX Patterns

1. **Skill-Based System** - Modular, versioned skill sets
2. **SPARC Methodology** - Structured feature building
3. **Hooks System** - Automation and integration
4. **Statusline Observability** - Real-time agent status

### Pain Points Identified

- Complexity overload for new users
- Too many configuration options
- Documentation sprawl (massive ADR system)
- Steep learning curve

---

## 2. KIRA (Krafton)

### Overview
- **Type:** Terminal-based AI agent
- **Benchmark:** 74.8% on Terminal-Bench 2.0
- **Target:** Game development workflows

### Key Features

| Feature | Description |
|---------|-------------|
| **Self-Critique** | Iterative improvement prompts |
| **Task Orchestration** | Multi-step workflow automation |
| **Electron App** | Desktop application |
| **Skills System** | Reusable task patterns |

### UX Patterns

1. **Terminal-First** - CLI-native experience
2. **Benchmark-Driven** - Performance-focused development

### Pain Points

- Gaming-specific (niche use case)
- Limited general-purpose features

---

## 3. Cline

### Overview
- **Type:** VS Code extension
- **Model Support:** Cloud + local models
- **Target:** Individual developers

### Key Features

| Feature | Description |
|---------|-------------|
| **Plan Mode** | Approve before execution |
| **MCP Integration** | Extensible tool system |
| **Local Models** | Ollama, LM Studio support |
| **Privacy Controls** | API key management |
| **Parallel Tasks** | Multiple concurrent agents |

### UX Patterns

1. **IDE-Integrated** - Seamless VS Code experience
2. **Explicit Consent** - User approves file changes
3. **Readable Diffs** - Clear change preview

### Pain Points

- State management issues with parallel tasks
- Project switching can corrupt state
- Less intuitive than VS Code-native tools

---

## 4. Roo Code

### Overview
- **Type:** VS Code extension + Cloud Agents
- **Target:** Development teams

### Key Features

| Feature | Description |
|---------|-------------|
| **Role Modes** | Architect, Coder, Debugger, Tester |
| **Cloud Agents** | Remote execution via Slack/GitHub |
| **Multi-Repo** | Large codebase management |
| **End-to-End Loops** | Iterative testing/debugging |

### UX Patterns

1. **Mode-Based** - Role-specific contexts
2. **Branch-Based** - Isolated work per task

### Pain Points

- Cloud agents require subscription
- Security concerns with remote execution

---

## 5. OpenCode (Comparison)

### Key Features

| Feature | Status |
|---------|--------|
| Multi-model | ✅ Multiple providers |
| MCP Support | ✅ Native |
| Local-first | ✅ Privacy focused |
| Swarm Mode | ✅ Agent orchestration |

---

## Common UX Patterns Across All Tools

### 1. Approval Workflows

| Tool | Pattern |
|------|---------|
| Cline | Plan mode with diff preview |
| Claude-Flow | Consensus protocols |
| Roo Code | Role-based approval |
| KIRA | Self-critique prompts |

### 2. Memory/Context

| Tool | Approach |
|------|----------|
| Claude-Flow | AgentDB, RuVector |
| Cline | Project context |
| Roo Code | Session memory |
| heliosHarness | Multi-level cache (L1-L4) |

### 3. Agent Specialization

| Tool | Specialization |
|------|----------------|
| Claude-Flow | 60+ role-based agents |
| Cline | Configurable assistants |
| KIRA | Task-specific |
| Roo Code | Mode-based (architect, coder, etc) |

---

## Feature Gaps vs heliosHarness

### What's Missing in heliosHarness

| Feature | Priority | Description |
|---------|----------|-------------|
| **Visual Diff Approval** | High | User sees diff before approval |
| **Role-Based Agents** | High | Specialized agent types |
| **Plan Mode** | Medium | Preview plans before execution |
| **Skills System** | Medium | Reusable task patterns |
| **Swarm Topologies** | Medium | Multi-agent patterns |
| **IDE Integration** | Low | VS Code plugin |
| **Local Model Support** | Medium | Ollama integration |

### What heliosHarness Does Better

| Feature | Advantage |
|---------|------------|
| Multi-level Cache | L1-L4 with pre-warming |
| Dynamic Scaling | Resource-based concurrency |
| Team mate System | Delegation protocol |
| Bounded Queue | Backpressure handling |

---

## Customer Pain Points Summary

### Top 5 Complaints Across Tools

1. **Complexity** - Too many options, steep learning curve
2. **State Management** - Parallel tasks interfere
3. **Context Loss** - Switching projects loses context
4. **Approval Friction** - Want more autonomy vs safety
5. **Model Lock-in** - Want local model support

### Opportunities for heliosHarness

1. **Simplified UX** -opinionated defaults
2. **State Isolation** - Proper project separation
3. **Hybrid Approval** - Configurable autonomy levels
4. **Local-First** - Privacy without complexity

---

## Recommendations

### QOL Priorities

| Priority | Feature | Rationale |
|----------|---------|------------|
| 1 | Plan Mode | Competitive with Cline |
| 2 | Skills System | Like Roo Code / Claude-Flow |
| 3 | Visual Diff | Approval workflow |
| 4 | Local Models | Privacy demand |
| 5 | Role-Based Agents | Specialization |

### Differentiation

1. **Resource-Aware Scaling** - Unique to heliosHarness
2. **Bounded Execution** - Memory safety
3. **Multi-Level Cache** - Performance focus

---

## References

- Claude-Flow: github.com/ruvnet/claude-flow
- KIRA: github.com/krafton-ai/KIRA
- Cline: cline.bot
- Roo Code: roocode.com
- Terminal-Bench: tbench.ai
