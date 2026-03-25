---
work_package_id: "WP06"
title: "cliproxyapi++: Executor Core Extraction"
lane: "planned"
dependencies: []
subtasks: ["T015", "T016"]
history:
  - date: "2026-03-03"
    event: "created"
    by: "spec-kitty.tasks"
---

# WP06: cliproxyapi++ — Executor Core Extraction

**Implementation command**: `spec-kitty implement WP06`

## Objective

Extract a shared `sdk/executor-core` package from cliproxyapi++ containing `ExecutorInterface`, `BaseExecutor`, and shared retry/HTTP/streaming helpers. Refactor all 15 executors to use the shared base.

## Context

- cliproxyapi++ has 15 LLM provider executors (Claude, Codex, Gemini, Kiro, Copilot, etc.)
- Each executor duplicates: retry logic, HTTP request construction, streaming response handling, error wrapping, timeout management
- Code reduction phase already extracted `RefreshWithRetry` and `defaultHttpRequest` — build on that
- See `kitty-specs/002-phenotype-modular-arch/research.md` Decision 5

## Subtasks

### T015: Extract sdk/executor-core

**Steps**:
1. Create `sdk/executor-core/` directory in cliproxyapi++
2. Define `ExecutorInterface`:
   ```go
   type ExecutorInterface interface {
       Execute(ctx context.Context, req *ExecuteRequest) (*ExecuteResponse, error)
       Stream(ctx context.Context, req *ExecuteRequest) (<-chan StreamChunk, error)
       Name() string
       SupportedModels() []string
       Health() HealthStatus
   }
   ```
3. Implement `BaseExecutor` struct with shared functionality:
   - HTTP client with configurable timeout, retry policy
   - Token refresh integration (uses authkit pattern)
   - Streaming response parser (SSE, WebSocket, HTTP chunked)
   - Error wrapping with provider context
   - Request/response logging hooks
4. Create `RetryPolicy` config:
   ```go
   type RetryPolicy struct {
       MaxRetries    int
       InitialDelay  time.Duration
       MaxDelay      time.Duration
       BackoffFactor float64
       RetryableErrs []int // HTTP status codes
   }
   ```
5. Create `go.mod` for `sdk/executor-core` (internal module, not yet extracted to separate repo)

**Validation**: `go build ./sdk/executor-core/...` passes

### T016: Refactor 15 executors to use executor-core

**Steps**:
1. For each executor (Claude, Codex, Gemini, Kiro, Copilot, GPT, Mistral, etc.):
   - Embed `BaseExecutor` struct
   - Remove duplicated retry/HTTP/streaming logic
   - Override only provider-specific behavior (auth, request format, response parsing)
2. Example refactored executor:
   ```go
   type ClaudeExecutor struct {
       executorcore.BaseExecutor
       apiKey string
   }

   func (e *ClaudeExecutor) Execute(ctx context.Context, req *ExecuteRequest) (*ExecuteResponse, error) {
       httpReq := e.BuildRequest("POST", "https://api.anthropic.com/v1/messages", req.ToClaudeFormat())
       return e.DoWithRetry(ctx, httpReq)
   }
   ```
3. Update executor factory/registry to construct executors with BaseExecutor embedded
4. Run full test suite after each executor migration (incremental, not big-bang)

**Validation**:
- All 15 executors build and pass existing tests
- No duplicated retry/HTTP/streaming code remains
- Each executor file is significantly smaller

## Definition of Done

- [ ] `sdk/executor-core` package with ExecutorInterface, BaseExecutor, RetryPolicy
- [ ] All 15 executors embed BaseExecutor
- [ ] No duplicated retry/HTTP/streaming patterns across executors
- [ ] All existing executor tests pass
- [ ] `go build ./...` and `go test ./...` pass

## Risks

- **Provider-specific edge cases**: Some executors may have unique retry or streaming needs that don't fit BaseExecutor. Allow per-executor overrides.
- **Test coverage**: Ensure executor tests still exercise the same code paths through the new base.

## Reviewer Guidance

- Check each executor's refactoring preserves its specific behavior
- Verify BaseExecutor is not over-abstracted — it should handle common cases, not force uncommon patterns
- Confirm no executor test was deleted or weakened during migration
