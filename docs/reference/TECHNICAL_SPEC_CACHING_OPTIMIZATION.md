# Technical Specification: Caching & Optimization System

**Version**: 1.0  
**Date**: 2026-02-23  
**Project**: heliosHarness

---

## Table of Contents

1. [Overview](#overview)
2. [Multi-Level Cache Architecture](#multi-level-cache-architecture)
3. [Predictive Pre-Warming](#predictive-pre-warming)
4. [Request Coalescing](#request-coalescing)
5. [Speculative Execution](#speculative-execution)
6. [Zero-Copy Optimizations](#zero-copy-optimizations)
7. [Resource Management](#resource-management)
8. [Network Optimization](#network-optimization)
9. [Configuration](#configuration)
10. [API Reference](#api-reference)

---

## Overview

This document details the caching and optimization strategies for heliosHarness, implementing:

- **4-tier caching** (L1-L4)
- **Predictive pre-warming** with usage patterns
- **Request coalescing** to prevent duplicate work
- **Speculative execution** for latency reduction
- **Zero-copy** operations for memory efficiency
- **Adaptive timeouts** based on historical data

---

## Multi-Level Cache Architecture

### Tier 1: L1 In-Memory Cache

```python
from cachetools import TTLCache
from threading import Lock

class L1Cache:
    """Hot path in-memory cache."""
    
    def __init__(
        self,
        maxsize: int = 1000,
        ttl: float = 60.0,
    ):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Any:
        with self._lock:
            if key in self._cache:
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = value
    
    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
```

### Tier 2: L2 Disk Cache

```python
import diskcache as dc

class L2Cache:
    """Persistent disk-backed cache."""
    
    def __init__(
        self,
        directory: str = "~/.cache/heliosharness",
        ttl: int = 3600,
        size_limit: int = 10**9,  # 1GB
    ):
        self._cache = dc.Cache(
            directory,
            size_limit=size_limit,
            eviction_policy="least-recently-used",
        )
        self._ttl = ttl
    
    def get(self, key: str) -> Any:
        value = self._cache.get(key, expire_time=self._ttl)
        if value is not None:
            # Promote to L1
            L1_CACHE.set(key, value)
        return value
    
    def set(self, key: str, value: Any):
        self._cache.set(key, value, expire=self._ttl)
        # Also set in L1
        L1_CACHE.set(key, value)
```

### Tier 3: Distributed Cache

```python
import redis.asyncio as redis

class L3Cache:
    """Redis-backed distributed cache."""
    
    def __init__(self, url: str):
        self._client = redis.from_url(url)
        self._prefix = "heliosharness:"
    
    async def get(self, key: str) -> Any:
        value = await self._client.get(f"{self._prefix}{key}")
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self._client.setex(
            f"{self._prefix}{key}",
            ttl,
            json.dumps(value),
        )
```

### Tier 4: Plan Template Cache

```python
class PlanCache:
    """Agentic plan caching - stores execution templates."""
    
    def __init__(self):
        self._plans: dict[str, PlanTemplate] = {}
        self._adaptor = LightweightAdaptor()
    
    async def get_adapted_plan(
        self, 
        request: Request
    ) -> Plan | None:
        keywords = extract_keywords(request.prompt)
        for key, template in self._plans.items():
            if keywords_match(keywords, template.keywords):
                return await self._adaptor.adapt(template, request)
        return None
    
    async def store_plan(self, request: Request, plan: Plan):
        keywords = extract_keywords(request.prompt)
        cache_key = hashlib.sha256(
            json.dumps(keywords, sort_keys=True).encode()
        ).hexdigest()
        
        self._plans[cache_key] = PlanTemplate(
            keywords=keywords,
            steps=plan.steps,
            tools=plan.tools,
            created_at=time.time(),
        )
```

---

## Predictive Pre-Warming

### Usage Predictor

```python
class UsagePredictor:
    """Predict likely-needed cache entries."""
    
    def __init__(self, model: str = "frecency"):
        self.model = model
        self._history: deque = deque(maxlen=10000)
        self._pattern_model = None
    
    def record(self, key: str):
        """Record cache access."""
        self._history.append({
            "key": key,
            "timestamp": time.time(),
        })
    
    async def predict_next(self, n: int = 10) -> list[str]:
        """Predict next N likely-needed keys."""
        if self.model == "frecency":
            return self._frecency_predict(n)
        elif self.model == "pattern":
            return await self._pattern_predict(n)
        return []
    
    def _frecency_predict(self, n: int) -> list[str]:
        """Frecency: frequently + recently used."""
        scores = {}
        now = time.time()
        
        for entry in self._history:
            key = entry["key"]
            age = now - entry["timestamp"]
            decay = 0.9 ** (age / 60)  # Decay over minutes
            scores[key] = scores.get(key, 0) + decay
        
        return sorted(scores, key=scores.get, reverse=True)[:n]
```

### Pre-Warming Daemon

```python
class PreWarmingDaemon:
    """Background pre-warming service."""
    
    def __init__(
        self,
        cache: MultiLevelCache,
        predictor: UsagePredictor,
        interval: int = 300,  # 5 minutes
    ):
        self.cache = cache
        self.predictor = predictor
        self.interval = interval
        self._running = False
    
    async def start(self):
        self._running = True
        while self._running:
            await self._warm()
            await asyncio.sleep(self.interval)
    
    async def _warm(self):
        predicted = await self.predictor.predict_next(n=20)
        
        for key in predicted:
            if not self.cache.get(key):
                try:
                    data = await self.cache.fetch(key)
                    self.cache.set(key, data)
                except Exception:
                    pass  # Best-effort
```

---

## Request Coalescing

### Coalescer Implementation

```python
class RequestCoalescer:
    """Merge concurrent requests for same key."""
    
    def __init__(self, timeout: float = 5.0):
        self._inflight: dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
        self.timeout = timeout
    
    async def get_or_fetch(
        self,
        key: str,
        fetch_fn: callable,
    ) -> Any:
        async with self._lock:
            if key in self._inflight:
                return await asyncio.wait_for(
                    self._inflight[key],
                    timeout=self.timeout
                )
            
            future = asyncio.Future()
            self._inflight[key] = future
        
        try:
            result = await fetch_fn()
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            async with self._lock:
                self._inflight.pop(key, None)
        
        return result
```

---

## Speculative Execution

### Provider Racing

```python
class SpeculativeExecutor:
    """Execute multiple providers, use best/first result."""
    
    async def race_first(
        self,
        providers: list[Provider],
        request: Request,
        timeout: float = 5.0,
    ) -> Result:
        """Return first successful result."""
        tasks = [
            asyncio.create_task(p.execute(request))
            for p in providers
        ]
        
        done, pending = await asyncio.wait(
            tasks,
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )
        
        # Cancel pending
        for task in pending:
            task.cancel()
        
        # Return first success
        for task in done:
            if not task.cancelled():
                result = task.result()
                if isinstance(result, Result):
                    return result
        
        raise NoProviderSucceededError()
    
    async def race_best(
        self,
        providers: list[Provider],
        request: Request,
        timeout: float = 10.0,
    ) -> Result:
        """Wait all, return highest quality."""
        results = await asyncio.gather(
            *[p.execute(request) for p in providers],
            return_exceptions=True,
            timeout=timeout,
        )
        
        valid = [r for r in results if isinstance(r, Result)]
        if valid:
            return max(valid, key=lambda r: r.quality_score)
        
        raise NoProviderSucceededError()
```

### Adaptive Timeout

```python
class AdaptiveTimeout:
    """Compute timeout based on historical performance."""
    
    def __init__(self, history_size: int = 100):
        self._latencies: deque = deque(maxlen=history_size)
    
    def record(self, latency_ms: float):
        self._latencies.append(latency_ms)
    
    def compute(
        self,
        base_timeout_ms: float = 5000,
        percentile: float = 0.95,
        safety_multiplier: float = 1.5,
    ) -> int:
        if not self._latencies:
            return base_timeout_ms
        
        sorted_latencies = sorted(self._latencies)
        idx = int(len(sorted_latencies) * percentile)
        p95 = sorted_latencies[min(idx, len(sorted_latencies)-1)]
        
        return int(max(base_timeout_ms, p95 * safety_multiplier))
```

---

## Zero-Copy Optimizations

### Memory-Mapped Files

```python
import mmap
import os

class ZeroCopyReader:
    """Read files without copying into user space."""
    
    def __init__(self, path: str, threshold_kb: int = 64):
        self.path = path
        self.threshold = threshold_kb * 1024
        self._mmap = None
    
    def _should_mmap(self) -> bool:
        return os.path.getsize(self.path) > self.threshold
    
    def read(self) -> bytes:
        if self._should_mmap():
            return self._read_mmap()
        return self._read_normal()
    
    def _read_mmap(self) -> bytes:
        with open(self.path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                return mm[:]
    
    def _read_normal(self) -> bytes:
        with open(self.path, 'rb') as f:
            return f.read()
```

### Sendfile for Network

```python
import asyncio
import os

async def sendfile_transfer(
    output_fd: int,
    input_path: str,
    offset: int = 0,
    count: int = -1,
):
    """Transfer file to socket without user-space copy."""
    with open(input_path, 'rb') as input_file:
        # Seek to offset
        input_file.seek(offset)
        
        # Use os.sendfile for zero-copy
        bytes_sent = 0
        while True:
            chunk = input_file.read(65536)
            if not chunk:
                break
            n = os.sendfile(output_fd, input_file.fileno(), 
                          offset + bytes_sent, len(chunk))
            bytes_sent += n
            if count > 0 and bytes_sent >= count:
                break
        
        return bytes_sent
```

### Shared Memory IPC

```python
import multiprocessing as mp

class SharedMemoryChannel:
    """Zero-copy IPC via shared memory."""
    
    def __init__(self, name: str, size: int):
        self.shm = mp.SharedMemory(name=name, create=True, size=size)
        self.buffer = mp.Buffer(self.shm.buf)
    
    def write(self, data: bytes):
        self.buffer.write(data)
    
    def read(self, size: int) -> bytes:
        return self.buffer.read(size)
    
    def close(self):
        self.shm.close()
        self.shm.unlink()
```

---

## Resource Management

### FD Manager

```python
class FDManager:
    """Manage file descriptors with limits."""
    
    SOFT_LIMIT = 512
    HARD_LIMIT = 1024
    
    def __init__(self):
        self._open: dict[int, FDInfo] = {}
        self._lock = asyncio.Lock()
    
    async def acquire(self, path: str, flags: int) -> int:
        async with self._lock:
            if len(self._open) >= self.HARD_LIMIT:
                raise FDExhaustedError()
            
            fd = os.open(path, flags)
            self._open[fd] = FDInfo(
                fd=fd,
                path=path,
                opened=time.time(),
            )
            return fd
    
    async def release(self, fd: int):
        async with self._lock:
            if fd in self._open:
                os.close(fd)
                del self._open[fd]
```

### Memory Pressure Handler

```python
class MemoryPressureHandler:
    """Respond to system memory pressure."""
    
    WARNING = 0.75
    CRITICAL = 0.90
    
    def __init__(self, callback: callable):
        self.callback = callback
    
    async def check(self):
        import psutil
        mem = psutil.virtual_memory()
        
        if mem.percent >= self.CRITICAL:
            await self.callback("critical", mem.percent)
        elif mem.percent >= self.WARNING:
            await self.callback("warning", mem.percent)
```

---

## Network Optimization

### Connection Pool

```python
import httpx

class AgentConnectionPool:
    """HTTP/2 connection pool with limits."""
    
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive: int = 20,
    ):
        self._client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive,
            ),
            http2=True,  # Multiplexing
            timeout=httpx.Timeout(30.0),
        )
    
    async def request(self, method: str, url: str, **kwargs):
        return await self._client.request(method, url, **kwargs)
    
    async def close(self):
        await self._client.aclose()
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
    size_limit_gb: 1
  l3:
    enabled: false
    redis_url: redis://localhost:6379
  plan_cache:
    enabled: true
    max_templates: 1000

optimization:
  prewarm:
    enabled: true
    interval_seconds: 300
    batch_size: 20
    model: frecency  # or pattern
  
  coalescing:
    enabled: true
    timeout_ms: 100
  
  speculative:
    enabled: true
    strategy: race_first  # or race_best
    providers:
      - claude
      - gemini
      - openai
    timeout_ms: 5000
  
  zero_copy:
    mmap_threshold_kb: 64
    sendfile: true
    shm_enabled: true

resources:
  fd_soft_limit: 512
  fd_hard_limit: 1024
  memory_warning_percent: 75
  memory_critical_percent: 90
  
network:
  http2: true
  max_connections: 100
  max_keepalive: 20
  timeout_seconds: 30
```

---

## API Reference

```python
# Cache API
from heliosHarness.cache import MultiLevelCache, L1Cache, L2Cache, PlanCache

cache = MultiLevelCache(l1_maxsize=1000, l2_dir="~/.cache/heliosharness")
cache.get(key)
cache.set(key, value)
cache.fetch(key)  # Miss handler

# Pre-warming API
from heliosHarness.optimization import PreWarmingDaemon, UsagePredictor

predictor = UsagePredictor(model="frecency")
daemon = PreWarmingDaemon(cache, predictor, interval=300)
await daemon.start()

# Coalescing API
from heliosHarness.optimization import RequestCoalescer

coalescer = RequestCoalescer(timeout=5.0)
result = await coalescer.get_or_fetch(key, fetch_fn)

# Speculative API
from heliosHarness.optimization import SpeculativeExecutor

executor = SpeculativeExecutor()
result = await executor.race_first(providers, request)

# Resource API
from heliosHarness.resources import FDManager, MemoryPressureHandler

fd_mgr = FDManager()
fd = await fd_mgr.acquire(path, os.O_RDONLY)
await fd_mgr.release(fd)
```

---

**Document Version**: 1.0  
**Status**: Ready for Implementation
