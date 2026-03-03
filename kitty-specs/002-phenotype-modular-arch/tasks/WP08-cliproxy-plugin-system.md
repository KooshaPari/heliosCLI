---
work_package_id: WP08
title: 'cliproxyapi++: Plugin System + Hexagonal Ports'
lane: planned
dependencies: []
subtasks: [T019, T020, T021, T022]
history:
- date: '2026-03-03'
  event: created
  by: spec-kitty.tasks
---

# WP08: cliproxyapi++ — Plugin System + Hexagonal Ports

**Implementation command**: `spec-kitty implement WP08 --base WP06`

## Objective

Implement the two-tier plugin architecture for cliproxyapi++ executors. Formalize executor and translator interfaces as hexagonal ports. Add translator matrix builder to reduce N×M duplication.

## Context

- executor-core extracted in WP06 provides BaseExecutor
- 15 built-in executors already use ExecutorInterface
- Goal: allow third-party executors as WASM plugins without modifying core routing
- Translator matrix (input format × output format) currently duplicated across executors

## Subtasks

### T019: Tier 1 — Executor interface + init() registration

**Steps**:
1. Create `plugin/registry.go`:
   ```go
   var executorRegistry = make(map[string]ExecutorFactory)

   type ExecutorFactory func(config map[string]any) (ExecutorInterface, error)

   func RegisterExecutor(name string, factory ExecutorFactory) {
       executorRegistry[name] = factory
   }
   ```
2. Each built-in executor registers via `init()`:
   ```go
   func init() {
       plugin.RegisterExecutor("claude", func(cfg map[string]any) (ExecutorInterface, error) {
           return NewClaudeExecutor(cfg)
       })
   }
   ```
3. Update routing to discover executors from registry instead of hardcoded switch

**Validation**: All 15 executors register via init() and are discoverable

### T020: Tier 2 — Extism host for executor .wasm

**Steps**:
1. Add `github.com/extism/go-sdk` dependency
2. Create `plugin/wasm_host.go`:
   - Load `.wasm` executor plugins from configurable directory
   - Validate plugin exports match ExecutorContract proto schema
   - Wrap in WasmExecutor implementing ExecutorInterface
3. Sandbox: memory limit (256MB), timeout (60s), no fs access
4. Register WASM executors in same registry as Tier 1
5. Create test .wasm plugin (minimal echo executor)

**Validation**: WASM executor loads, registers, handles requests; failure doesn't crash host

### T021: Translator matrix builder

**Steps**:
1. Analyze current translator duplication (input format × output format conversions)
2. Create `translator/matrix.go`:
   - Define `Translator` interface: `Translate(from Format, to Format, data []byte) ([]byte, error)`
   - Build translator registry mapping (Format, Format) → Translator
   - Codegen or builder pattern to reduce N×M to N+M implementations
3. Replace hardcoded format conversions in executors with matrix lookups

**Validation**: All format conversions work through the matrix; no duplicated conversion code

### T022: Formalize executor + translator as hexagonal ports

**Steps**:
1. Create `ports/` package:
   - `executor_port.go` — ExecutorPort interface (same as ExecutorInterface but named as port)
   - `translator_port.go` — TranslatorPort interface
   - `routing_port.go` — RoutingPort for request dispatch
2. Create `adapters/` for concrete implementations
3. Ensure all external I/O goes through ports (HTTP calls, auth, storage)

**Validation**: Clear separation between domain logic and external dependencies

## Definition of Done

- [ ] Plugin registry with init() registration for all built-in executors
- [ ] Extism host loads and executes .wasm executor plugins
- [ ] Translator matrix reduces format conversion duplication
- [ ] Executor and translator formalized as hexagonal ports
- [ ] All tests pass; no routing behavior changes

## Risks

- **Extism Go SDK maturity**: Test thoroughly; fall back to HashiCorp go-plugin if Extism is unstable.
- **Translator matrix complexity**: Start simple (map-based registry) before adding codegen.

## Reviewer Guidance

- Verify WASM sandbox constraints are enforced
- Check translator matrix covers all existing format pairs
- Ensure hexagonal ports don't over-abstract simple operations
