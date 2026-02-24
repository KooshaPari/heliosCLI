"""Circuit breaker pattern for fault tolerance.

Provides circuit breaker implementation to prevent cascade failures
when external services are unavailable.
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any, Optional


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"        # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 3           # Successes to close
    timeout: float = 30.0               # Seconds before half-open
    half_open_max_calls: int = 3       # Max calls in half-open


@dataclass
class CircuitMetrics:
    """Circuit breaker metrics."""
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0.0
    total_calls: int = 0
    rejected_calls: int = 0


class CircuitBreaker:
    """Circuit breaker for fault tolerance.
    
    Usage:
        breaker = CircuitBreaker(failure_threshold=5, timeout=30)
        
        try:
            result = breaker.call(risky_function)
        except CircuitOpenError:
            # Service is down
            pass
    """
    
    def __init__(self, name: str = "circuit", config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._last_failure_time = 0.0
        self._lock = threading.RLock()
        self._last_state_change = time.time()
    
    @property
    def state(self) -> CircuitState:
        """Get current state."""
        with self._lock:
            self._check_state_transition()
            return self._state
    
    def _check_state_transition(self) -> None:
        """Check if state should transition."""
        if self._state == CircuitState.OPEN:
            # Check if timeout expired
            if time.time() - self._last_state_change >= self._config.timeout:
                self._state = CircuitState.HALF_OPEN
                self._last_state_change = time.time()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        with self._lock:
            self._check_state_transition()
            
            if self._state == CircuitState.OPEN:
                self._reject_call()
                raise CircuitOpenError(f"Circuit {self.name} is OPEN")
            
            self._total_calls += 1
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, coro) -> Any:
        """Execute async function with circuit breaker protection."""
        with self._lock:
            self._check_state_transition()
            
            if self._state == CircuitState.OPEN:
                self._reject_call()
                raise CircuitOpenError(f"Circuit {self.name} is OPEN")
        
        try:
            result = await coro
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful call."""
        with self._lock:
            self._successes += 1
            
            if self._state == CircuitState.HALF_OPEN:
                if self._successes >= self._config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failures = 0
                    self._successes = 0
                    self._last_state_change = time.time()
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._last_state_change = time.time()
                self._successes = 0
            elif self._failures >= self._config.failure_threshold:
                self._state = CircuitState.OPEN
                self._last_state_change = time.time()
    
    def _reject_call(self) -> None:
        """Record rejected call."""
        with self._lock:
            self._rejected_calls += 1
    
    def get_metrics(self) -> CircuitMetrics:
        """Get circuit breaker metrics."""
        with self._lock:
            return CircuitMetrics(
                state=self._state,
                failures=self._failures,
                successes=self._successes,
                last_failure_time=self._last_failure_time,
                total_calls=getattr(self, '_total_calls', 0),
                rejected_calls=getattr(self, '_rejected_calls', 0),
            )
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failures = 0
            self._successes = 0
            self._last_state_change = time.time()


class CircuitOpenError(Exception):
    """Raised when circuit is open."""
    pass


class CircuitBreakerRegistry:
    """Registry of circuit breakers for different services."""
    
    _instance: Optional['CircuitBreakerRegistry'] = None
    
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'CircuitBreakerRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_or_create(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, **kwargs)
            return self._breakers[name]
    
    def get_all_metrics(self) -> dict[str, CircuitMetrics]:
        """Get metrics for all circuit breakers."""
        with self._lock:
            return {name: b.get_metrics() for name, b in self._breakers.items()}


# Decorator for easy circuit breaker usage
def circuit_breaker(name: str, **config_kwargs):
    """Decorator to add circuit breaker to a function.
    
    Usage:
        @circuit_breaker("my-service", failure_threshold=3)
        def call_service():
            pass
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreakerRegistry.get_instance().get_or_create(
            name, **config_kwargs
        )
        
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator
