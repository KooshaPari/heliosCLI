# Technical Design: Dynamic Thread Limit System

**Version**: 1.0  
**Date**: 2026-02-23  
**Project**: heliosHarness

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Models](#data-models)
4. [Resource Monitoring](#resource-monitoring)
5. [Dynamic Limit Computation](#dynamic-limit-computation)
6. [Hysteresis Control](#hysteresis-control)
7. [Backpressure Mechanism](#backpressure-mechanism)
8. [Configuration](#configuration)
9. [API Reference](#api-reference)

---

## Overview

The Dynamic Thread Limit System replaces fixed concurrency limits with resource-aware adaptive limits. It:

1. Samples system resources (CPU, memory, FD, load)
2. Applies hysteresis to prevent thrashing
3. Computes dynamic limit with safety buffers
4. Provides backpressure when overloaded

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DynamicLimitController                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌─────────────────────────────────┐ │
│  │  ResourceSampler │───▶│   HysteresisController          │ │
│  │  (CPU, Mem, FD, │    │   upper_threshold: 0.80         │ │
│  │   Load)          │    │   lower_threshold: 0.60         │ │
│  │  interval: 1-5s  │    │   dwell_time: 30s              │ │
│  └──────────────────┘    └─────────────────────────────────┘ │
│           │                           │                          │
│           │                           ▼                          │
│           │                  ┌─────────────────────────────────┐ │
│           └─────────────────▶│  compute_dynamic_limit          │ │
│                            │  min_buffer: 0.05               │ │
│                            │  discretionary_buffer: 0.15     │ │
│                            └─────────────────────────────────┘ │
│                                            │                   │
│                                            ▼                   │
│                            ┌─────────────────────────────────┐ │
│                            │   LimitGate (semaphore)         │ │
│                            │   effective_limit: int          │ │
│                            └─────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### ResourceSnapshot

```python
@dataclass
class ResourceSnapshot:
    """Current system resource usage."""
    
    # CPU
    cpu_percent: float  # 0.0 - 100.0
    
    # Memory  
    memory_percent: float  # 0.0 - 100.0
    memory_available_mb: float
    
    # File Descriptors
    fd_used: int
    fd_limit: int
    fd_percent: float  # 0.0 - 100.0
    
    # Load Average (1min, 5min, 15min)
    load_avg_1m: float
    load_avg_5m: float
    load_avg_15m: float
    
    # Computed
    timestamp: float
    
    @property
    def load_normalized(self) -> float:
        """Normalize load to 0-1 based on CPU cores."""
        cpu_count = os.cpu_count() or 4
        return min(self.load_avg_1m / cpu_count, 1.0)
```

### LimitGateConfig

```python
@dataclass
class LimitGateConfig:
    """Configuration for dynamic limits."""
    
    # Buffer thresholds
    min_buffer: float = 0.05  # 5% hard limit
    discretionary_buffer: float = 0.15  # 15% soft limit
    
    # Resource thresholds (0.0-1.0)
    cpu_threshold: float = 0.80
    memory_threshold: float = 0.85
    fd_threshold: float = 0.80
    load_threshold: float = 0.80
    
    # Sampling
    sampling_interval_seconds: float = 2.0
    
    @classmethod
    def from_dict(cls, d: dict) -> "LimitGateConfig":
        """Build from dict (e.g. settings)."""
        return cls(
            min_buffer=d.get("min_buffer", 0.05),
            discretionary_buffer=d.get("discretionary_buffer", 0.15),
            cpu_threshold=d.get("cpu_threshold", 0.80),
            memory_threshold=d.get("memory_threshold", 0.85),
            fd_threshold=d.get("fd_threshold", 0.80),
            load_threshold=d.get("load_threshold", 0.80),
            sampling_interval_seconds=d.get("sampling_interval_seconds", 2.0),
        )
```

### HysteresisController

```python
@dataclass
class HysteresisState:
    """Current hysteresis state."""
    
    state: Literal["stable", "scaling_up", "scaling_down"] = "stable"
    last_change_time: float = 0.0
    consecutive_same_direction: int = 0
    
class HysteresisController:
    """Prevents thrashing by using upper/lower thresholds."""
    
    def __init__(
        self,
        upper_threshold: float = 0.80,
        lower_threshold: float = 0.60,
        dwell_time_seconds: int = 30,
    ):
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.dwell_time_seconds = dwell_time_seconds
        self._state = HysteresisState()
    
    def get_limit(
        self,
        current_limit: int,
        running_count: int,
        target_limit: int,
    ) -> int:
        """Apply hysteresis to determine the new limit."""
        
        now = time.time()
        time_since_change = now - self._state.last_change_time
        
        # Determine direction
        if target_limit > current_limit:
            desired_direction = "up"
        elif target_limit < current_limit:
            desired_direction = "down"
        else:
            return current_limit
        
        # Check if we should change
        if desired_direction == "up":
            # Can always scale up after dwell time
            if time_since_change >= self.dwell_time_seconds:
                self._state = HysteresisState(
                    state="stable",
                    last_change_time=now,
                    consecutive_same_direction=0,
                )
                return target_limit
        else:
            # Scale down only if we're above target and dwell passed
            if running_count < target_limit and time_since_change >= self.dwell_time_seconds:
                self._state = HysteresisState(
                    state="stable", 
                    last_change_time=now,
                    consecutive_same_direction=0,
                )
                return target_limit
        
        # Hold current limit
        return current_limit
```

---

## Resource Monitoring

### ResourceSampler

```python
class ResourceSampler:
    """Sample system resources cross-platform."""
    
    def __init__(self, use_native: bool = False):
        self.use_native = use_native
        
    def sample(self) -> ResourceSnapshot:
        """Sample all resources."""
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        mem = psutil.virtual_memory()
        memory_percent = mem.percent
        memory_available_mb = mem.available / (1024 * 1024)
        
        # File Descriptors (Unix)
        try:
            fd_used = len(os.listdir('/proc/self/fd'))
            fd_limit = 1024  # Default, may need adjustment
            fd_percent = fd_used / fd_limit
        except NotImplementedError:
            # macOS fallback
            try:
                import resource
                soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                fd_used = soft
                fd_limit = soft
                fd_percent = fd_used / fd_limit
            except:
                fd_used = 0
                fd_limit = 1024
                fd_percent = 0.0
        
        # Load Average
        try:
            load_avg_1m, load_avg_5m, load_avg_15m = os.getloadavg()
        except NotImplementedError:
            load_avg_1m = load_avg_5m = load_avg_15m = 0.0
        
        return ResourceSnapshot(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            fd_used=fd_used,
            fd_limit=fd_limit,
            fd_percent=fd_percent,
            load_avg_1m=load_avg_1m,
            load_avg_5m=load_avg_5m,
            load_avg_15m=load_avg_15m,
            timestamp=time.time(),
        )
```

---

## Dynamic Limit Computation

### compute_dynamic_limit

```python
def compute_dynamic_limit(
    snapshot: ResourceSnapshot,
    config: LimitGateConfig,
    running_count: int,
) -> tuple[int, dict]:
    """
    Compute max concurrent slots from resource gates.
    
    Returns (effective_limit, gate_details).
    """
    
    # Normalize each resource to 0-1
    cpu_util = snapshot.cpu_percent / 100.0
    mem_util = snapshot.memory_percent / 100.0
    fd_util = snapshot.fd_percent
    
    # Normalize load to 0-1
    load_util = snapshot.load_normalized
    
    # Calculate available headroom for each resource
    # Headroom = 1.0 - utilization (so 1.0 = fully available)
    cpu_headroom = max(0.0, 1.0 - cpu_util)
    mem_headroom = max(0.0, 1.0 - mem_util)
    fd_headroom = max(0.0, 1.0 - fd_util)
    load_headroom = max(0.0, 1.0 - load_util)
    
    # Minimum headroom across all resources
    min_headroom = min(cpu_headroom, mem_headroom, fd_headroom, load_headroom)
    
    # Calculate limits at different buffer levels
    # Base: assume max 100 concurrent as baseline
    max_baseline = 100
    
    # Hard limit: use min_buffer (5%)
    hard_limit = int(max_baseline * (1.0 - config.min_buffer))
    
    # Soft limit: use discretionary_buffer (15%)
    soft_limit = int(max_baseline * (1.0 - config.discretionary_buffer))
    
    # Dynamic limit: scale with headroom
    dynamic_limit = int(max_baseline * min_headroom)
    
    # Effective limit: most restrictive
    effective_limit = min(hard_limit, soft_limit, dynamic_limit)
    
    # Ensure minimum of 1
    effective_limit = max(1, effective_limit)
    
    # Gate details for logging/metrics
    gate_details = {
        "cpu_util": cpu_util,
        "mem_util": mem_util,
        "fd_util": fd_util,
        "load_util": load_util,
        "min_headroom": min_headroom,
        "hard_limit": hard_limit,
        "soft_limit": soft_limit,
        "dynamic_limit": dynamic_limit,
        "effective_limit": effective_limit,
        "running_count": running_count,
    }
    
    return effective_limit, gate_details
```

---

## Hysteresis Control

### Integration

```python
class DynamicLimitController:
    """Main controller for dynamic limits."""
    
    def __init__(
        self,
        config: LimitGateConfig | None = None,
        initial_limit: int = 10,
    ):
        self.config = config or LimitGateConfig()
        self.current_limit = initial_limit
        self.sampler = ResourceSampler()
        self.hysteresis = HysteresisController(
            upper_threshold=0.80,
            lower_threshold=0.60,
            dwell_time_seconds=30,
        )
    
    async def run(self):
        """Main loop - sample and adjust."""
        while True:
            # Sample resources
            snapshot = self.sampler.sample()
            
            # Compute dynamic limit
            target_limit, details = compute_dynamic_limit(
                snapshot,
                self.config,
                self._running_count,
            )
            
            # Apply hysteresis
            self.current_limit = self.hysteresis.get_limit(
                current_limit=self.current_limit,
                running_count=self._running_count,
                target_limit=target_limit,
            )
            
            # Log details
            logger.info(
                "dynamic_limit_update",
                current=self.current_limit,
                target=target_limit,
                running=self._running_count,
                **details,
            )
            
            # Wait for next sample
            await asyncio.sleep(self.config.sampling_interval_seconds)
```

---

## Backpressure Mechanism

### PriorityQueue with Backpressure

```python
class BackpressureQueue:
    """Priority queue with backpressure."""
    
    def __init__(
        self,
        max_size: int = 100,
        backpressure_threshold: float = 0.75,
    ):
        self.max_size = max_size
        self.backpressure_threshold = backpressure_threshold
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=max_size
        )
        self._priority_counts = defaultdict(int)
    
    async def enqueue(
        self,
        item: Any,
        priority: int = 2,  # 0=CRITICAL, 1=HIGH, 2=NORMAL, 3=LOW
    ) -> bool:
        """Try to enqueue item. Returns False if rejected."""
        
        load_percent = self._queue.qsize() / self.max_size
        
        # Check backpressure based on priority
        if priority == 0:  # CRITICAL
            can_accept = self._queue.qsize() < self.max_size
        elif priority == 1:  # HIGH
            can_accept = load_percent < 0.90
        elif priority == 2:  # NORMAL
            can_accept = load_percent < 0.75
        else:  # LOW
            can_accept = load_percent < 0.50
        
        if not can_accept:
            logger.warning(
                "backpressure_reject",
                priority=priority,
                size=self._queue.qsize(),
                max_size=self.max_size,
            )
            return False
        
        await self._queue.put((priority, item))
        self._priority_counts[priority] += 1
        return True
    
    async def dequeue(self) -> Any:
        """Dequeue highest priority item."""
        priority, item = await self._queue.get()
        self._priority_counts[priority] -= 1
        return item
```

---

## Recovery Methods

### Checkpoint & Restore

```python
class CheckpointManager:
    """Save/restore delegation state for recovery."""
    
    def __init__(self, checkpoint_dir: str = "/tmp/heliosharness/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_checkpoint(self, delegation_id: str, state: dict):
        """Save delegation state."""
        checkpoint_file = self.checkpoint_dir / f"{delegation_id}.json"
        await asyncio.to_thread(checkpoint_file.write_text, json.dumps(state))
    
    async def load_checkpoint(self, delegation_id: str) -> dict | None:
        """Load delegation state."""
        checkpoint_file = self.checkpoint_dir / f"{delegation_id}.json"
        if checkpoint_file.exists():
            return json.loads(checkpoint_file.read_text())
        return None
    
    async def clear_checkpoint(self, delegation_id: str):
        """Remove checkpoint after success."""
        checkpoint_file = self.checkpoint_dir / f"{delegation_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
```

### Cascading Cancellation

```python
class CancellationRegistry:
    """Track parent-child delegation relationships."""
    
    def __init__(self):
        self._parents: dict[str, set[str]] = defaultdict(set)
        self._children: dict[str, str] = {}  # child_id -> parent_id
    
    def register_child(self, parent_id: str, child_id: str):
        """Register parent-child relationship."""
        self._parents[parent_id].add(child_id)
        self._children[child_id] = parent_id
    
    async def cancel_cascade(self, parent_id: str):
        """Cancel parent and all descendants."""
        to_cancel = {parent_id}
        
        # BFS to find all descendants
        queue = list(self._parents[parent_id])
        while queue:
            child = queue.pop(0)
            to_cancel.add(child)
            queue.extend(self._parents[child])
        
        # Cancel all
        for deleg_id in to_cancel:
            await self._cancel_delegation(deleg_id)
```

---

## Optimization Techniques

### Zero-Overhead Agent Pool

```python
class LazyAgentPool:
    """Pool that spawns agents only when needed."""
    
    def __init__(self, max_agents: int = 10):
        self.max_agents = max_agents
        self._idle: asyncio.Queue[AgentProcess] = asyncio.Queue()
        self._active: dict[str, AgentProcess] = {}
        self._lock = asyncio.Lock()
    
    async def acquire(self, timeout: float = 30.0) -> AgentProcess:
        """Acquire agent from pool (spawn if needed)."""
        # Try to get idle agent
        try:
            agent = self._idle.get_nowait()
            self._active[agent.id] = agent
            return agent
        except asyncio.QueueEmpty:
            pass
        
        # Check if we can spawn new
        async with self._lock:
            if len(self._active) < self.max_agents:
                agent = await self._spawn_agent()
                self._active[agent.id] = agent
                return agent
        
        # Wait for idle
        agent = await asyncio.wait_for(
            self._idle.get(),
            timeout=timeout
        )
        self._active[agent.id] = agent
        return agent
    
    async def release(self, agent: AgentProcess):
        """Return agent to pool."""
        if agent.id in self._active:
            del self._active[agent.id]
        
        # Check if agent is still healthy
        if await agent.is_healthy():
            await self._idle.put(agent)
        else:
            await self._destroy_agent(agent)
    
    async def _spawn_agent(self) -> AgentProcess:
        """Spawn new agent process (lazy)."""
        # Use COW fork for fast startup
        proc = await asyncio.create_subprocess_exec(
            "codex", "exec", "--profile", "default",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return AgentProcess(proc, warmup=True)
```

### Lock-Free Queue Operations

```python
class LockFreePriorityQueue:
    """Lock-free priority queue using atomic operations."""
    
    def __init__(self, max_size: int = 1000):
        self._data: list[tuple[int, Any]] = []
        self._lock = asyncio.Lock()  # Minimal locking
    
    async def enqueue(self, item: Any, priority: int) -> bool:
        """Enqueue with minimal lock time."""
        async with self._lock:
            if len(self._data) >= 1000:
                return False
            # Binary heap insert - O(log n)
            heapq.heappush(self._data, (priority, item))
            return True
    
    async def dequeue(self) -> Any | None:
        """Dequeue highest priority."""
        async with self._lock:
            if not self._data:
                return None
            return heapq.heappop(self._data)[1]
```

### Batch Resource Sampling

```python
class BatchedResourceSampler:
    """Sample resources in batches for efficiency."""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self._pending: list[asyncio.Future] = []
    
    async def sample(self) -> ResourceSnapshot:
        """Sample with batching."""
        # Coalesce multiple sample requests
        if not self._pending:
            return await self._do_sample()
        
        # Wait for batch
        results = await asyncio.gather(*self._pending)
        return results[0]
    
    async def _do_sample(self) -> ResourceSnapshot:
        """Actual sampling logic."""
        # Single psutil call for all metrics
        return ResourceSnapshot(...)
```

---

## Performance Budgets

| Operation | Target | Max Acceptable | Implementation |
|-----------|--------|---------------|-----------------|
| Delegate start | <100ms | <500ms | Lazy pool, COW fork |
| Status query | <10ms | <50ms | In-memory cache |
| Queue enqueue | <5ms | <20ms | Lock-free heap |
| Resource sample | <50ms | <100ms | Batch sampling |
| Context switch | <10ms | <50ms | Zero-copy mmap |

---

## Configuration

### YAML Configuration

```yaml
# heliosharness.yaml
scaling:
  # Buffer thresholds
  min_buffer: 0.05        # 5% - hard limit
  discretionary_buffer: 0.15  # 15% - soft limit
  
  # Resource thresholds
  cpu_threshold: 0.80
  memory_threshold: 0.85
  fd_threshold: 0.80
  load_threshold: 0.80
  
  # Sampling
  sampling_interval_seconds: 2.0
  
  # Hysteresis
  hysteresis:
    upper_threshold: 0.80
    lower_threshold: 0.60
    dwell_time_seconds: 30

# Queue
queue:
  max_size: 100
  backpressure_threshold: 0.75
  
  # Priority levels
  priority_levels:
    CRITICAL: 0
    HIGH: 1
    NORMAL: 2
    LOW: 3
```

### Environment Variables

```bash
# Scaling
HELIOS_MIN_BUFFER=0.05
HELIOS_DISCRETIONARY_BUFFER=0.15
HELIOS_SAMPLING_INTERVAL=2.0
HELIOS_HYSTERESIS_UPPER=0.80
HELIOS_HYSTERESIS_LOWER=0.60
HELIOS_HYSTERESIS_DWELL=30

# Queue
HELIOS_QUEUE_MAX_SIZE=100
HELIOS_BACKPRESSURE_THRESHOLD=0.75
```

---

## API Reference

### Python API

```python
from heliosHarness.scaling import (
    DynamicLimitController,
    LimitGateConfig,
    ResourceSampler,
    compute_dynamic_limit,
    BackpressureQueue,
)

# Create config
config = LimitGateConfig(
    min_buffer=0.05,
    discretionary_buffer=0.15,
    sampling_interval_seconds=2.0,
)

# Create controller
controller = DynamicLimitController(
    config=config,
    initial_limit=10,
)

# Get current limit
current_limit = controller.current_limit

# Create queue with backpressure
queue = BackpressureQueue(
    max_size=100,
    backpressure_threshold=0.75,
)
```

### CLI Commands

```bash
# View current scaling info
harness scaling info

# View queue status
harness queue status

# Set manual limit override
harness scaling set-limit 15

# Enable/disable dynamic scaling
harness scaling enable
harness scaling disable
```

---

## Resource Management

### File Descriptor Management
- FD limits: 512 soft, 1024 hard
- Tracking: per-agent FD count
- Cleanup: automatic stale FD closure

### Process Management
- Memory limit: 256MB per agent
- Thread limit: 50 per agent  
- Health checks: every 10 seconds

### Memory Pressure Response
- 75% memory: warn + slow new work
- 90% memory: stop new work + cleanup
- 95% memory: force kill lowest priority

### Leak Detection
- FD leak: baseline comparison
- Memory leak: heap growth tracking
- Handle leak: thread/connection counts

---

**Document Version**: 1.1  
**Status**: Ready for Implementation
