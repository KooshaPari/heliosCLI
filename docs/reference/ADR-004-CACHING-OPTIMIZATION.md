# ADR-004: Caching & Optimization Architecture

**Date**: 2026-02-23  
**Status**: Proposed  
**Author**: heliosHarness Team

## Context

We need a comprehensive caching and optimization strategy for heliosHarness that addresses:

1. **Multi-level caching** for agent responses and tool outputs
2. **Predictive pre-warming** based on usage patterns
3. **Zero-copy optimizations** for memory efficiency
4. **Request coalescing** to prevent duplicate work
5. **Network optimization** for distributed agents

## Decision

We implement a layered caching architecture with the following levels:

### Layer 1: In-Memory Cache (L1)
- **Implementation**: `cachetools.TTLCache`
- **Max Size**: 1000 entries
- **TTL**: 60 seconds
- **Use**: Hot paths, frequently accessed data
- **Thread Safety**: Required (locks for mutations)

### Layer 2: Disk Cache (L2)
- **Implementation**: `diskcache.Cache` (SQLite-backed)
- **Location**: `~/.cache/heliosharness/`
- **TTL**: 3600 seconds (1 hour)
- **Use**: Persistent data, larger payloads
- **Graceful Fallback**: If unavailable, L1-only mode

### Layer 3: Distributed Cache (L3)
- **Implementation**: Redis/Memcached (optional)
- **Use**: Multi-instance deployments
- **Consistency**: eventual

---

## Caching Strategies

### 1. Response Caching

**What's Cached**:
- Tool execution results
- LLM responses (with determinism fingerprint)
- File reads (with mtime hash)

**Cache Key**:
```python
def cache_key(prompt: str, config: dict, tools: list) -> str:
    """Generate cache key including factors affecting output."""
    fingerprint = hash([
        prompt,
        json.dumps(config, sort_keys=True),
        sorted(tools),
        environment_variables,  # if deterministic
    ])
    return f"response:{fingerprint}"
```

### 2. Agentic Plan Caching (APC)

Based on latest research (Agentic Plan Caching - OpenReview 2025):

**How It Works**:
1. Extract plan templates from previous executions
2. Store in cache with keyword extraction
3. Match new requests to cached plans
4. Lightweight adaptation to specific context

```python
class AgenticPlanCache:
    """Cache and adapt plan templates."""
    
    def __init__(self):
        self.plans: dict[str, PlanTemplate] = {}
        self.adaptor = LightweightAdaptor()
    
    async def get_plan(self, request: Request) -> Plan | None:
        keywords = extract_keywords(request)
        for key, template in self.plans.items():
            if keywords_match(keywords, template.keywords):
                return await self.adaptor.adapt(template, request)
        return None
    
    async def store_plan(self, request: Request, plan: Plan):
        keywords = extract_keywords(request)
        template = PlanTemplate(keywords=keywords, steps=plan.steps)
        self.plans[cache_key(keywords)] = template
```

**Benefits**:
- 46% cost reduction (per research)
- 27% latency reduction
- Maintains quality via adaptation

### 3. Context Caching

Based on IC-Cache (arxiv 2025):

```python
class ContextCache:
    """Cache in-context examples from larger models."""
    
    def __init__(self, embedding_model: str = "small"):
        self.examples: list[Example] = []
        self.embeddings = EmbeddingCache(embedding_model)
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[Example]:
        query_emb = await self.embeddings.embed(query)
        scores = cosine_similarity(query_emb, [e.emb for e in self.examples])
        top_indices = np.argsort(scores)[-top_k:]
        return [self.examples[i] for i in top_indices]
```

---

## Optimization Strategies

### 1. Zero-Copy Operations

**Techniques**:

| Technique | Use Case | Benefit |
|-----------|----------|----------|
| `mmap` | Large file access | No kernel→user copy |
| `sendfile()` | Network transfers | Direct pipe |
| Shared memory | IPC | Zero copy between processes |
| io_uring | Async I/O | Batch operations |
| COW fork | Agent spawning | Fast process creation |

**Implementation**:
```python
# mmap for large context files
def load_context_mmap(path: str) -> bytes:
    with open(path, 'rb') as f:
        return mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

# sendfile for network
async def send_file(peer: asyncio.StreamWriter, path: str):
    with open(path, 'rb') as f:
        await asyncio.start_server(
            lambda r, w: transfer(peer, f),
            sendfile(peer.fileno(), f.fileno())
        )
```

### 2. Request Coalescing

```python
class RequestCoalescer:
    """Prevent duplicate work from concurrent requests."""
    
    def __init__(self):
        self._inflight: dict[str, asyncio.Future] = {}
    
    async def get(self, key: str, fetch_fn) -> Any:
        if key in self._inflight:
            return await self._inflight[key]
        
        future = asyncio.Future()
        self._inflight[key] = future
        
        try:
            result = await fetch_fn()
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            self._inflight.pop(key, None)
        
        return await future
```

### 3. Speculative Execution

```python
class SpeculativeExecutor:
    """Execute multiple paths, use best result."""
    
    async def race_first(
        self, 
        providers: list[Provider], 
        task: str
    ) -> Result:
        """Race providers, return first success."""
        results = await asyncio.gather(
            *[p.execute(task) for p in providers],
            return_exceptions=True
        )
        for r in results:
            if isinstance(r, Result):
                return r
        raise AllProvidersFailedError()
    
    async def race_best(
        self,
        providers: list[Provider],
        task: str
    ) -> Result:
        """Race providers, return highest quality."""
        results = await asyncio.gather(
            *[p.execute(task) for p in providers]
        )
        return max(results, key=lambda r: r.quality_score)
```

### 4. Adaptive Timeout

```python
def adaptive_timeout(
    historical_p95_ms: float,
    base_ms: int = 5000,
    safety: float = 1.5
) -> int:
    """Compute timeout based on history."""
    return int(max(base_ms, historical_p95_ms * safety))
```

---

## Pre-Warming Strategies

### 1. Predictive Pre-Warming

```python
class PredictiveWarming:
    """Pre-warm based on predicted needs."""
    
    def __init__(self, cache: MultiLevelCache):
        self.cache = cache
        self.predictor = UsagePredictor()
    
    async def warm(self):
        predicted = await self.predictor.predict_next()
        for key in predicted:
            if not self.cache.get(key):
                data = await self.cache.fetch(key)
                self.cache.set(key, data)
```

### 2. Frecency-Based Warming

```python
class FrecencyCache:
    """Frequently + Recently used cache."""
    
    def __init__(self, decay: float = 0.9):
        self.decay = decay
        self.scores: dict[str, float] = {}
    
    def access(self, key: str):
        self.scores[key] = self.scores.get(key, 0) * self.decay + 1
    
    def top(self, n: int) -> list[str]:
        return sorted(self.scores, key=self.scores.get, reverse=True)[:n]
```

---

## Configuration

```yaml
# heliosharness.yaml
cache:
  l1:
    maxsize: 1000
    ttl_seconds: 60
  l2:
    enabled: true
    directory: ~/.cache/heliosharness
    ttl_seconds: 3600
  prewarm:
    enabled: true
    strategies:
      - name: "frecency"
        decay: 0.9
      - name: "predictive"
        model: usage_patterns

optimization:
  zero_copy:
    mmap_threshold_kb: 64
    sendfile_enabled: true
  speculative:
    enabled: true
    providers: [claude, gemini, openai]
    strategy: race_first
  coalescing:
    enabled: true
    timeout_ms: 100
```

---

## Consequences

### Positive
- 40-80% latency reduction (per research)
- 46% cost reduction with plan caching
- Zero overhead when idle (lazy init)
- Graceful degradation

### Negative
- Complexity increase
- Cache invalidation challenges
- Memory overhead for cache structures

### Neutral
- Requires tuning per workload

---

## References

- Agentic Plan Caching (OpenReview 2025)
- IC-Cache: In-Context Caching (arxiv 2025)
- Zero-Copy I/O with io_uring (Medium 2025)
- Multi-Level Cache (thegent implementation)
- CachePreWarmer (thegent implementation)
- FrecencyCache (thegent implementation)
