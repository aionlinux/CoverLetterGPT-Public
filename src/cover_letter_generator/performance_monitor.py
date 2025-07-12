"""
Advanced Performance Monitoring and Analytics System
===================================================

Real-time performance monitoring, intelligent caching, and comprehensive analytics
for production-grade performance optimization and user experience enhancement.

Author: Claude AI (Anthropic)
Purpose: Ultra-fine-tuned performance monitoring for public GitHub showcase
"""

import time
import psutil
import threading
import functools
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union
from collections import deque, defaultdict
from dataclasses import dataclass, field
import json
import statistics
from pathlib import Path


@dataclass
class PerformanceMetric:
    """Container for individual performance measurements"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    component: str
    operation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "operation": self.operation,
            "metadata": self.metadata
        }


@dataclass
class OperationProfile:
    """Performance profile for a specific operation"""
    operation_name: str
    component: str
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_execution: Optional[datetime] = None
    error_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def update(self, execution_time: float, had_error: bool = False, cache_hit: bool = False):
        """Update profile with new execution data"""
        self.total_calls += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = self.total_time / self.total_calls
        self.last_execution = datetime.now()
        
        if had_error:
            self.error_count += 1
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage"""
        return (self.error_count / self.total_calls * 100) if self.total_calls > 0 else 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage"""
        total_cache_operations = self.cache_hits + self.cache_misses
        return (self.cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_name": self.operation_name,
            "component": self.component,
            "total_calls": self.total_calls,
            "total_time": self.total_time,
            "min_time": self.min_time if self.min_time != float('inf') else 0,
            "max_time": self.max_time,
            "avg_time": self.avg_time,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hit_rate
        }


class PerformanceCache:
    """Intelligent caching system with LRU eviction and TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with TTL and LRU tracking"""
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        entry = self.cache[key]
        
        # Check TTL
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            del self.access_times[key]
            self.miss_count += 1
            return None
        
        # Update access time for LRU
        self.access_times[key] = datetime.now()
        self.hit_count += 1
        
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store item in cache with TTL"""
        # Evict if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": expires_at
        }
        self.access_times[key] = datetime.now()
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times, key=self.access_times.get)
        del self.cache[lru_key]
        del self.access_times[lru_key]
        self.eviction_count += 1
    
    def _periodic_cleanup(self) -> None:
        """Periodically clean up expired entries"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                now = datetime.now()
                expired_keys = [
                    key for key, entry in self.cache.items()
                    if now > entry["expires_at"]
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]
                        
            except Exception:
                pass  # Ignore cleanup errors
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hit_count + self.miss_count
        return (self.hit_count / total * 100) if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_rate,
            "eviction_count": self.eviction_count,
            "memory_usage_mb": self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage of cache in MB"""
        try:
            import sys
            total_size = sum(sys.getsizeof(entry) for entry in self.cache.values())
            total_size += sum(sys.getsizeof(key) for key in self.cache.keys())
            return total_size / (1024 * 1024)  # Convert to MB
        except:
            return 0.0


class PerformanceMonitor:
    """
    Advanced performance monitoring system with real-time analytics.
    
    Features:
    - Real-time performance tracking with sub-millisecond precision
    - Intelligent caching with LRU eviction and TTL
    - System resource monitoring (CPU, memory, disk)
    - Operation profiling with detailed statistics
    - Performance bottleneck detection
    - Automatic performance optimization recommendations
    - Historical performance trending
    """
    
    def __init__(self, max_history: int = 10000, cache_size: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.operation_profiles: Dict[str, OperationProfile] = {}
        self.cache = PerformanceCache(max_size=cache_size)
        self.system_metrics: deque = deque(maxlen=100)  # Last 100 system snapshots
        
        # Performance thresholds
        self.thresholds = {
            "slow_operation_ms": 1000,
            "high_memory_usage_mb": 500,
            "high_cpu_usage_percent": 80,
            "low_cache_hit_rate_percent": 50
        }
        
        # Start system monitoring
        self._start_system_monitoring()
        
        # Performance alerts
        self.alerts: List[Dict[str, Any]] = []
    
    def _start_system_monitoring(self):
        """Start background system resource monitoring"""
        def monitor_system():
            while True:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    system_snapshot = {
                        "timestamp": datetime.now(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_mb": memory.used / (1024**2),
                        "memory_available_mb": memory.available / (1024**2),
                        "disk_percent": disk.percent,
                        "disk_free_gb": disk.free / (1024**3)
                    }
                    
                    self.system_metrics.append(system_snapshot)
                    
                    # Check for performance alerts
                    self._check_system_alerts(system_snapshot)
                    
                    time.sleep(30)  # Monitor every 30 seconds
                    
                except Exception:
                    time.sleep(60)  # Retry in 1 minute on error
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def _check_system_alerts(self, snapshot: Dict[str, Any]):
        """Check for system performance alerts"""
        alerts = []
        
        if snapshot["cpu_percent"] > self.thresholds["high_cpu_usage_percent"]:
            alerts.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": f"High CPU usage: {snapshot['cpu_percent']:.1f}%",
                "timestamp": snapshot["timestamp"],
                "value": snapshot["cpu_percent"]
            })
        
        if snapshot["memory_used_mb"] > self.thresholds["high_memory_usage_mb"]:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning",
                "message": f"High memory usage: {snapshot['memory_used_mb']:.1f}MB",
                "timestamp": snapshot["timestamp"],
                "value": snapshot["memory_used_mb"]
            })
        
        # Add alerts to history
        self.alerts.extend(alerts)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert["timestamp"] > cutoff_time]
    
    def track_operation(self, 
                       component: str, 
                       operation: str, 
                       execution_time: float,
                       had_error: bool = False,
                       cache_hit: bool = False,
                       metadata: Optional[Dict[str, Any]] = None):
        """Track performance metrics for an operation"""
        
        # Create metric
        metric = PerformanceMetric(
            name="execution_time",
            value=execution_time,
            unit="seconds",
            timestamp=datetime.now(),
            component=component,
            operation=operation,
            metadata=metadata or {}
        )
        
        # Add to history
        self.metrics_history.append(metric)
        
        # Update operation profile
        profile_key = f"{component}.{operation}"
        if profile_key not in self.operation_profiles:
            self.operation_profiles[profile_key] = OperationProfile(operation, component)
        
        self.operation_profiles[profile_key].update(execution_time, had_error, cache_hit)
        
        # Check for performance alerts
        self._check_operation_alerts(metric, self.operation_profiles[profile_key])
    
    def _check_operation_alerts(self, metric: PerformanceMetric, profile: OperationProfile):
        """Check for operation-specific performance alerts"""
        alerts = []
        
        # Slow operation alert
        if metric.value * 1000 > self.thresholds["slow_operation_ms"]:
            alerts.append({
                "type": "slow_operation",
                "severity": "warning",
                "message": f"Slow operation: {metric.component}.{metric.operation} took {metric.value*1000:.1f}ms",
                "timestamp": metric.timestamp,
                "component": metric.component,
                "operation": metric.operation,
                "value": metric.value * 1000
            })
        
        # Low cache hit rate alert
        if profile.cache_hit_rate < self.thresholds["low_cache_hit_rate_percent"] and profile.total_calls > 10:
            alerts.append({
                "type": "low_cache_hit_rate",
                "severity": "info",
                "message": f"Low cache hit rate: {metric.component}.{metric.operation} at {profile.cache_hit_rate:.1f}%",
                "timestamp": metric.timestamp,
                "component": metric.component,
                "operation": metric.operation,
                "value": profile.cache_hit_rate
            })
        
        self.alerts.extend(alerts)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Generate comprehensive performance summary"""
        if not self.metrics_history:
            return {"status": "no_data", "message": "No performance data available"}
        
        # Calculate overall statistics
        recent_metrics = [m for m in self.metrics_history if m.timestamp > datetime.now() - timedelta(hours=1)]
        
        if recent_metrics:
            execution_times = [m.value for m in recent_metrics]
            avg_execution_time = statistics.mean(execution_times)
            median_execution_time = statistics.median(execution_times)
            p95_execution_time = sorted(execution_times)[int(len(execution_times) * 0.95)] if execution_times else 0
        else:
            avg_execution_time = median_execution_time = p95_execution_time = 0
        
        # Get top performing and worst performing operations
        sorted_profiles = sorted(
            self.operation_profiles.values(),
            key=lambda p: p.avg_time,
            reverse=True
        )
        
        # System resource summary
        recent_system = list(self.system_metrics)[-10:] if self.system_metrics else []
        avg_cpu = statistics.mean([s["cpu_percent"] for s in recent_system]) if recent_system else 0
        avg_memory = statistics.mean([s["memory_used_mb"] for s in recent_system]) if recent_system else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_performance": {
                "total_operations": len(self.metrics_history),
                "avg_execution_time_ms": avg_execution_time * 1000,
                "median_execution_time_ms": median_execution_time * 1000,
                "p95_execution_time_ms": p95_execution_time * 1000,
                "operations_tracked": len(self.operation_profiles)
            },
            "system_resources": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_mb": avg_memory,
                "cache_hit_rate": self.cache.hit_rate,
                "cache_size": len(self.cache.cache)
            },
            "top_slow_operations": [profile.to_dict() for profile in sorted_profiles[:5]],
            "recent_alerts": [alert for alert in self.alerts if alert["timestamp"] > datetime.now() - timedelta(hours=1)],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze cache performance
        if self.cache.hit_rate < 50 and self.cache.hit_count + self.cache.miss_count > 100:
            recommendations.append({
                "type": "cache_optimization",
                "priority": "medium",
                "message": f"Cache hit rate is low ({self.cache.hit_rate:.1f}%). Consider increasing cache size or TTL.",
                "action": "Increase cache size or adjust TTL settings"
            })
        
        # Analyze slow operations
        slow_operations = [
            profile for profile in self.operation_profiles.values()
            if profile.avg_time > 1.0 and profile.total_calls > 5
        ]
        
        if slow_operations:
            slowest = max(slow_operations, key=lambda p: p.avg_time)
            recommendations.append({
                "type": "operation_optimization",
                "priority": "high",
                "message": f"Operation {slowest.component}.{slowest.operation_name} is slow (avg: {slowest.avg_time*1000:.1f}ms)",
                "action": "Profile and optimize this operation"
            })
        
        # Analyze error rates
        high_error_operations = [
            profile for profile in self.operation_profiles.values()
            if profile.error_rate > 5.0 and profile.total_calls > 10
        ]
        
        if high_error_operations:
            worst = max(high_error_operations, key=lambda p: p.error_rate)
            recommendations.append({
                "type": "error_reduction",
                "priority": "high",
                "message": f"Operation {worst.component}.{worst.operation_name} has high error rate ({worst.error_rate:.1f}%)",
                "action": "Investigate and fix error conditions"
            })
        
        # System resource recommendations
        if self.system_metrics:
            recent_memory = [s["memory_used_mb"] for s in list(self.system_metrics)[-10:]]
            avg_memory = statistics.mean(recent_memory)
            
            if avg_memory > 400:
                recommendations.append({
                    "type": "memory_optimization",
                    "priority": "medium",
                    "message": f"Average memory usage is high ({avg_memory:.1f}MB)",
                    "action": "Review memory usage patterns and implement garbage collection optimizations"
                })
        
        return recommendations
    
    def get_operation_insights(self, component: str = None, operation: str = None) -> Dict[str, Any]:
        """Get detailed insights for specific operations"""
        
        if component and operation:
            profile_key = f"{component}.{operation}"
            if profile_key in self.operation_profiles:
                profile = self.operation_profiles[profile_key]
                
                # Get historical trend
                operation_metrics = [
                    m for m in self.metrics_history
                    if m.component == component and m.operation == operation
                ]
                
                trend = "stable"
                if len(operation_metrics) > 10:
                    recent = [m.value for m in operation_metrics[-5:]]
                    older = [m.value for m in operation_metrics[-10:-5]]
                    
                    if recent and older:
                        recent_avg = statistics.mean(recent)
                        older_avg = statistics.mean(older)
                        
                        if recent_avg > older_avg * 1.2:
                            trend = "degrading"
                        elif recent_avg < older_avg * 0.8:
                            trend = "improving"
                
                return {
                    "profile": profile.to_dict(),
                    "trend": trend,
                    "total_metrics": len(operation_metrics),
                    "recommendations": self._get_operation_recommendations(profile)
                }
        
        # Return summary of all operations
        return {
            "total_operations": len(self.operation_profiles),
            "operations": [profile.to_dict() for profile in self.operation_profiles.values()],
            "summary_stats": {
                "fastest_operation": min(self.operation_profiles.values(), key=lambda p: p.avg_time).operation_name if self.operation_profiles else None,
                "slowest_operation": max(self.operation_profiles.values(), key=lambda p: p.avg_time).operation_name if self.operation_profiles else None,
                "most_reliable": min(self.operation_profiles.values(), key=lambda p: p.error_rate).operation_name if self.operation_profiles else None
            }
        }
    
    def _get_operation_recommendations(self, profile: OperationProfile) -> List[str]:
        """Get specific recommendations for an operation"""
        recommendations = []
        
        if profile.avg_time > 0.5:
            recommendations.append("Consider optimizing algorithm or adding caching")
        
        if profile.error_rate > 2.0:
            recommendations.append("Investigate error conditions and add better error handling")
        
        if profile.cache_hit_rate < 30 and profile.total_calls > 20:
            recommendations.append("Improve caching strategy or increase cache TTL")
        
        if profile.total_calls < 5:
            recommendations.append("Operation needs more usage data for accurate analysis")
        
        return recommendations
    
    def export_performance_report(self, filepath: str) -> None:
        """Export comprehensive performance report to JSON"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "summary": self.get_performance_summary(),
            "operation_profiles": {k: v.to_dict() for k, v in self.operation_profiles.items()},
            "cache_stats": self.cache.get_stats(),
            "recent_alerts": [alert for alert in self.alerts if alert["timestamp"] > datetime.now() - timedelta(hours=24)],
            "system_metrics_sample": [
                {**metrics, "timestamp": metrics["timestamp"].isoformat()}
                for metrics in list(self.system_metrics)[-20:]
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)


def performance_monitor(monitor: PerformanceMonitor, 
                       component: str,
                       operation: str = None,
                       use_cache: bool = False,
                       cache_ttl: int = None):
    """
    Decorator for automatic performance monitoring with optional caching
    
    Usage:
        @performance_monitor(monitor, "memory_core", "load_skills", use_cache=True)
        def load_skills(self):
            # Your code here
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = operation or func.__name__
            
            # Check cache if enabled
            cache_key = None
            cache_hit = False
            if use_cache:
                cache_key = f"{component}.{op_name}:{hash(str(args) + str(kwargs))}"
                cached_result = monitor.cache.get(cache_key)
                if cached_result is not None:
                    cache_hit = True
                    monitor.track_operation(component, op_name, 0, False, True)
                    return cached_result
            
            # Execute operation with timing
            start_time = time.perf_counter()
            had_error = False
            
            try:
                result = func(*args, **kwargs)
                
                # Cache result if enabled
                if use_cache and cache_key:
                    monitor.cache.set(cache_key, result, cache_ttl)
                
                return result
                
            except Exception as e:
                had_error = True
                raise
            finally:
                execution_time = time.perf_counter() - start_time
                monitor.track_operation(component, op_name, execution_time, had_error, cache_hit)
        
        return wrapper
    return decorator


# Global performance monitor instance
_global_performance_monitor = None

def get_global_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor


def initialize_performance_monitoring(max_history: int = 10000, cache_size: int = 1000) -> PerformanceMonitor:
    """Initialize the global performance monitoring system"""
    global _global_performance_monitor
    _global_performance_monitor = PerformanceMonitor(max_history, cache_size)
    return _global_performance_monitor