"""Integration tests for performance optimization modules.

Tests cross-module interactions and combined functionality.
"""

import asyncio
import tempfile
import time
import pytest
from pathlib import Path


class TestSubprocessAndMemory:
    """Test subprocess + memory integration."""
    
    def test_resources_with_memory_profiler(self):
        """Test that resources module works with memory profiler."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.resources import safe_popen, ResourceMonitor
        from harness.memory_profiler import MemoryProfiler
        import subprocess
        
        # Use resource monitor with memory profiler
        with ResourceMonitor() as monitor:
            with safe_popen(['echo', 'test'], stdout=subprocess.PIPE) as proc:
                proc.wait()
        
        # Should not leak
        assert monitor.metrics.get('fd_delta', 0) <= 2
    
    def test_bounded_cache_with_memory(self):
        """Test bounded cache doesn't leak memory."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.bounded_cache import BoundedCache
        import tracemalloc
        
        tracemalloc.start()
        
        cache = BoundedCache(max_size=10)
        
        # Fill cache
        for i in range(20):
            cache.set(f"key{i}", f"value{i}" * 100)
        
        # Check size is bounded
        assert len(cache) <= 10
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should not use excessive memory
        assert peak < 10 * 1024 * 1024  # 10MB


class TestNetworkAndCircuit:
    """Test network + circuit breaker integration."""
    
    def test_http_pool_with_circuit_breaker(self):
        """Test HTTP pool with circuit breaker."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.http_pool import HTTPConnectionPool
        from harness.circuit_breaker import CircuitBreaker
        
        # Create pool and circuit
        pool = HTTPConnectionPool()
        breaker = CircuitBreaker("test")
        
        # Should both work
        assert pool.get_stats() is not None
        assert breaker.state.value == "closed"


class TestMultiAgentAndContext:
    """Test multi-agent + context integration."""
    
    def test_teammate_with_session(self):
        """Test teammate registry with session store."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.teammate_registry import TeammateRegistry, TeammateType
        from harness.session_store import get_session_store
        
        # Create registry
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = TeammateRegistry(Path(tmpdir) / "teammates.json")
            registry.register(
                type=TeammateType.CODER,
                name="test-coder",
                model="test",
            )
            
            # Create session
            store = get_session_store(Path(tmpdir) / "sessions")
            session = store.create("Test goal")
            
            # Both should work
            assert registry.get("test-coder") is not None
            assert session.goal == "Test goal"
    
    def test_planning_with_scratchpad(self):
        """Test planning with scratchpad file system."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.planning import PlanExecutor
        from harness.scratchpad import ScratchpadFileSystem
        
        # Create executor and scratchpad
        executor = PlanExecutor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            scratchpad = ScratchpadFileSystem("test-session", Path(tmpdir))
            
            # Create plan
            plan = executor.create_plan("Test", [
                {"id": "step1", "description": "Write code"},
                {"id": "step2", "description": "Buffer results"},
            ])
            
            assert len(plan.steps) == 2


class TestAsyncAndBulkhead:
    """Test async + bulkhead integration."""
    
    def test_async_runtime_with_bulkhead(self):
        """Test async runtime with bulkhead."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.async_runtime import AsyncRuntime
        from harness.bulkhead import Bulkhead, BulkheadConfig
        
        # Create both
        runtime = AsyncRuntime()
        bulkhead = Bulkhead(BulkheadConfig("test", max_concurrent=2))
        
        assert runtime.get_stats() is not None
        assert bulkhead.get_metrics() is not None


class TestLatencyAndBatcher:
    """Test latency + request batcher integration."""
    
    def test_latency_with_batching(self):
        """Test latency tracking with request batching."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.latency_tracker import LatencyTracker
        from harness.request_batcher import RequestBatcher
        
        tracker = LatencyTracker()
        
        # Simulate batched requests
        for i in range(10):
            tracker.record("api/test", 10 + i, True)
        
        stats = tracker.get_stats("api/test")
        
        assert stats.count == 10
        assert stats.mean_ms > 0


class TestShutdownAndQueue:
    """Test shutdown + task queue integration."""
    
    def test_graceful_shutdown_with_queue(self):
        """Test graceful shutdown with task queue."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.shutdown import GracefulShutdown
        from harness.task_queue import TaskQueue
        
        shutdown = GracefulShutdown()
        queue = TaskQueue(max_size=10)
        
        assert shutdown.get_state() is not None
        assert queue.get_status() is not None


class TestContextCompaction:
    """Test context compaction integration."""
    
    def test_compactor_with_delegation(self):
        """Test context compactor with delegation protocol."""
        import sys
        sys.path.insert(0, 'harness/src')
        
        from harness.context_compactor import ContextCompactor, ContextMessage, CompactionStrategy
        from harness.delegation_protocol import DelegationProtocol
        
        # Create compactor and protocol
        compactor = ContextCompactor()
        protocol = DelegationProtocol()
        
        # Add messages
        compactor.add_message(ContextMessage(
            role="user",
            content="Hello",
            priority=5,
        ))
        
        # Get compacted
        result = compactor.get_compacted_context()
        
        assert len(result) > 0
        assert protocol.get_stats() is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
