"""Helios Harness - Lazy-loaded for low memory"""

# Lazy imports to reduce startup memory (<10MB target)
def __getattr__(name: str):
    """Lazy load modules on first access"""
    
    # Core interfaces - always needed
    if name in ("Discoverer", "Runner", "RunnerConfig", "QualityNormalizer", "evidence_payload"):
        from . import interfaces, discoverer, runner, normalizer, schema
        return locals()[name]
    
    # Teammate system - loaded on demand
    if name in ("Teammate", "TeammateRegistry", "DelegationRequest", "DelegationResult",
                "DelegationProtocol", "CodexExecutor", "Priority", "DelegationStatus",
                "HealthStatus", "HealthMonitor"):
        from . import teammates
        return getattr(teammates, name)
    
    # Dynamic scaling - loaded on demand  
    if name in ("ScalingConfig", "ResourceSampler", "ResourceSnapshot",
                "DynamicLimitController", "MemoryPressureHandler", "FDManager", "CircuitBreaker"):
        from . import scaling
        return getattr(scaling, name)
    
    # Caching - loaded on demand
    if name in ("L1Cache", "L2Cache", "L1CacheStats", "RequestCoalescer",
                "CachePreWarmer", "SpeculativeExecutor"):
        from . import cache
        return getattr(cache, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Core
    "Discoverer", "Runner", "RunnerConfig", "QualityNormalizer", "evidence_payload",
]
