---
work_package_id: WP07
title: 'cliproxyapi++: Shared Package Extraction (authkit + httpkit)'
lane: planned
dependencies: []
subtasks: [T017, T018]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP07: cliproxyapi++ — Shared Package Extraction

**Implementation command**: `spec-kitty implement WP07 --base WP02`

## Objective

Extract auth logic to `phenotype-go-authkit` and HTTP helpers to `phenotype-go-httpkit` shared repos. cliproxyapi++ and agentapi++ will consume these as Go module dependencies.

## Context

- Shared repos scaffolded in WP02
- cliproxyapi++ `internal/auth/` has ~4K LOC of token storage, refresh, provider auth — used by 20+ importers within cliproxy++
- HTTP helpers (`defaultHttpRequest`, proxy helpers) identified during code reduction phase
- agentapi++ also needs auth and HTTP patterns (WP14 will consume these)

## Subtasks

### T017: Extract auth logic to phenotype-go-authkit

**Steps**:
1. Identify all auth-related types in cliproxyapi++ `internal/auth/`:
   - `TokenStore`, `BaseTokenStorage`, `RefreshWithRetry`
   - Provider-specific auth (OAuth2, API key, session-based)
2. Copy to `phenotype-go-authkit/`:
   - `tokenstore.go` — TokenStore interface + BaseTokenStorage
   - `refresh.go` — RefreshWithRetry generic helper
   - `oauth2.go` — OAuth2 token flow
   - `apikey.go` — API key management
3. Ensure no cliproxyapi++-internal imports in extracted code
4. In cliproxyapi++, replace `internal/auth` imports with `phenotype-go-authkit`:
   ```go
   import authkit "github.com/KooshaPari/phenotype-go-authkit"
   ```
5. Update `go.mod` with new dependency
6. Run `go mod tidy` and verify all imports resolve

**Validation**: `go build ./...` and `go test ./...` pass in both repos

### T018: Extract HTTP helpers to phenotype-go-httpkit

**Steps**:
1. Identify HTTP helper code:
   - `defaultHttpRequest` function (extracted during code reduction)
   - Proxy request construction helpers
   - Response parsing utilities
   - Cache helpers
2. Copy to `phenotype-go-httpkit/`:
   - `request.go` — defaultHttpRequest, request builders
   - `response.go` — response parsing, error extraction
   - `cache.go` — cache helpers
3. In cliproxyapi++, replace local helpers with httpkit imports
4. Update `go.mod`

**Validation**: `go build ./...` and `go test ./...` pass in both repos

## Definition of Done

- [ ] phenotype-go-authkit contains all shared auth types
- [ ] phenotype-go-httpkit contains all shared HTTP helpers
- [ ] cliproxyapi++ consumes both as Go module dependencies
- [ ] No auth/HTTP duplicated code remains in cliproxyapi++ internals
- [ ] All tests pass in all 3 repos

## Risks

- **internal/ visibility**: Go `internal/` packages can't be imported externally. The extraction must move types OUT of internal/ into the shared repo.
- **Transitive deps**: Shared packages should minimize their own dependencies.

## Reviewer Guidance

- Verify no cliproxyapi++-specific logic leaked into shared packages
- Check that shared package APIs are clean and documented
- Ensure go.sum files are committed
