---
work_package_id: "WP02"
title: "Shared Package Scaffolding"
lane: "planned"
dependencies: []
subtasks: ["T006", "T007"]
history:
  - date: "2026-03-03"
    event: "created"
    by: "spec-kitty.tasks"
---

# WP02: Shared Package Scaffolding

**Implementation command**: `spec-kitty implement WP02`

## Objective

Create 7 empty shared package repositories with proper structure, CI, README, and package manager configuration. These repos will be populated by downstream WPs (WP04, WP07, WP10, WP11).

## Context

- Polyrepo strategy per `docs/governance/project_decomposition_governance.md`
- Naming: `phenotype-{lang}-{concern}` for Go/Rust/Python, `@helios/{concern}` for TypeScript
- Flat dependency graph: shared packages never depend on each other
- All start at v0.1.0; accept breaking changes freely pre-v1.0

## Subtasks

### T006: Create Go shared repos

**Purpose**: Scaffold 3 Go module repos.

**Steps** (repeat for each):

1. **phenotype-go-authkit**:
   - `gh repo create KooshaPari/phenotype-go-authkit --public`
   - `go mod init github.com/KooshaPari/phenotype-go-authkit`
   - Create `authkit.go` with package declaration + doc comment
   - Create `.github/workflows/go-ci.yml` (build, test, vet, lint)
   - README: purpose (token storage, refresh, provider auth), consumers (cliproxy++, agent++)

2. **phenotype-go-executor-core**:
   - Same scaffold
   - `go mod init github.com/KooshaPari/phenotype-go-executor-core`
   - README: purpose (ExecutorInterface, BaseExecutor, retry/HTTP helpers)

3. **phenotype-go-httpkit**:
   - Same scaffold
   - `go mod init github.com/KooshaPari/phenotype-go-httpkit`
   - README: purpose (defaultHttpRequest, proxy helpers, cache helpers)

**Common CI template** (`.github/workflows/go-ci.yml`):
```yaml
name: Go CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.22' }
      - run: go build ./...
      - run: go test ./...
      - run: go vet ./...
```

**Files per repo**: go.mod, {name}.go, README.md, .github/workflows/go-ci.yml, .gitignore, LICENSE
**Validation**: `go build ./...` passes in each repo

### T007: Create non-Go shared repos

**Purpose**: Scaffold 4 shared repos (1 Rust, 1 Python, 2 TypeScript).

**Steps**:

1. **phenotype-rs-protocol** (Rust):
   - `cargo init --lib phenotype-rs-protocol`
   - Add `prost` dependency in Cargo.toml
   - Create `src/lib.rs` with doc comment
   - CI: `cargo build`, `cargo test`, `cargo clippy`

2. **phenotype-py-infra** (Python):
   - `uv init phenotype-py-infra`
   - Create `pyproject.toml` with package metadata
   - Create `src/phenotype_py_infra/__init__.py`
   - CI: `uv sync`, `pytest`, `ruff check`

3. **@helios/audit-core** (TypeScript):
   - Create repo `helios-audit-core`
   - `pnpm init`
   - Set `"name": "@helios/audit-core"` in package.json
   - Create `src/index.ts` with placeholder export
   - CI: `pnpm build` (tsup or tsc), `pnpm test` (vitest)
   - tsconfig.json with strict mode

4. **@helios/protocol-types** (TypeScript):
   - Same scaffold as audit-core
   - `"name": "@helios/protocol-types"`

**Files per repo**: language-specific config, src/ entry point, README.md, CI workflow, .gitignore, LICENSE
**Validation**: Each repo builds clean with its language toolchain

## Definition of Done

- [ ] All 7 repos exist on GitHub with proper structure
- [ ] Each repo has CI workflow that passes
- [ ] Each repo has README documenting purpose and consumers
- [ ] Go modules resolve (`go mod tidy`), Cargo builds, pnpm builds, uv syncs
- [ ] All repos are at v0.1.0 initial state

## Risks

- **GitHub API rate limits**: Creating 7 repos in sequence. Use `gh` CLI with auth token.
- **Package registry setup**: npm scope `@helios` may need org-level config. Verify publishing permissions.

## Reviewer Guidance

- Verify naming follows `phenotype-{lang}-{concern}` convention
- Ensure no repo has dependencies on other shared repos (flat graph)
- Check that LICENSE is consistent across all repos
