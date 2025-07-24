"""
Test Suite for Performance Monitoring System
===========================================

Comprehensive tests for the advanced performance monitoring system,
validating real-time tracking, caching, resource monitoring, and optimization.

"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from cover_letter_generator.performance_monitor import (
    PerformanceMonitor, performance_monitor, CacheManager,
    ResourceMonitor, PerformanceMetrics
)
from conftest import measure_execution_time


class TestPerformanceMonitor:
    """Test the performance monitoring main functionality"""
    
    @pytest.fixture
    def perf_monitor(self):
        """Create performance monitor instance for testing"""
        return PerformanceMonitor()
    
    def test_monitor_initialization(self, perf_monitor):
        """Test proper initialization of performance monitor"""
        assert perf_monitor is not None
        assert hasattr(perf_monitor, 'cache_manager')
        assert hasattr(perf_monitor, 'resource_monitor')
        assert hasattr(perf_monitor, 'metrics')
        assert hasattr(perf_monitor, 'performance_history')
    
    def test_operation_tracking(self, perf_monitor):
        """Test operation performance tracking"""
        component = "test_component"
        operation = "test_operation"
        execution_time = 150.0  # milliseconds
        
        # Track operation
        perf_monitor.track_operation(component, operation, execution_time)
        
        # Verify tracking
        metrics = perf_monitor.get_performance_metrics(component)
        assert metrics is not None
        assert operation in metrics.operations
        assert metrics.operations[operation]["total_calls"] == 1
        assert metrics.operations[operation]["total_time"] == execution_time
        assert metrics.operations[operation]["avg_time"] == execution_time
    
    def test_multiple_operation_tracking(self, perf_monitor):
        """Test tracking multiple operations"""
        component = "test_component"
        operation = "test_operation"
        
        # Track multiple calls
        execution_times = [100.0, 200.0, 150.0]
        for time_ms in execution_times:
            perf_monitor.track_operation(component, operation, time_ms)
        
        # Verify aggregation
        metrics = perf_monitor.get_performance_metrics(component)
        op_metrics = metrics.operations[operation]
        
        assert op_metrics["total_calls"] == 3
        assert op_metrics["total_time"] == sum(execution_times)
        assert abs(op_metrics["avg_time"] - (sum(execution_times) / 3)) < 0.1
        assert op_metrics["min_time"] == min(execution_times)
        assert op_metrics["max_time"] == max(execution_times)
    
    def test_performance_decorator(self, perf_monitor):
        """Test performance monitoring decorator"""
        @performance_monitor(perf_monitor, "test_component", "decorated_function")
        def test_function(duration_ms=100):
            time.sleep(duration_ms / 1000.0)  # Convert to seconds
            return "test_result"
        
        # Execute function
        result = test_function(150)
        
        # Verify result
        assert result == "test_result"
        
        # Verify monitoring
        metrics = perf_monitor.get_performance_metrics("test_component")
        assert "decorated_function" in metrics.operations
        
        # Execution time should be approximately 150ms (with some tolerance)
        avg_time = metrics.operations["decorated_function"]["avg_time"]
        assert 140 <= avg_time <= 200  # Allow for execution overhead
    
    def test_performance_decorator_with_cache(self, perf_monitor):
        """Test performance decorator with caching enabled"""
        call_count = 0
        
        @performance_monitor(perf_monitor, "test_component", "cached_function", use_cache=True)
        def expensive_function(param):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate expensive operation
            return f"result_{param}"
        
        # First call
        result1 = expensive_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Second call with same parameter (should use cache)
        result2 = expensive_function("test")
        assert result2 == "result_test"
        assert call_count == 1  # Function not called again
        
        # Third call with different parameter
        result3 = expensive_function("different")
        assert result3 == "result_different"
        assert call_count == 2
    
    def test_slow_operation_detection(self, perf_monitor):
        """Test detection of slow operations"""
        # Configure slow operation threshold
        perf_monitor.slow_operation_threshold_ms = 100
        
        # Track fast operation
        perf_monitor.track_operation("component", "fast_op", 50)
        
        # Track slow operation
        perf_monitor.track_operation("component", "slow_op", 200)
        
        # Get slow operations
        slow_ops = perf_monitor.get_slow_operations(threshold_ms=100)
        
        assert len(slow_ops) == 1
        assert slow_ops[0]["component"] == "component"
        assert slow_ops[0]["operation"] == "slow_op"
        assert slow_ops[0]["avg_time"] == 200
    
    def test_performance_history_tracking(self, perf_monitor):
        """Test performance history tracking over time"""
        component = "test_component"
        operation = "test_operation"
        
        # Track operations over time
        for i in range(10):
            perf_monitor.track_operation(component, operation, 100 + i * 10)
            time.sleep(0.01)  # Small delay to differentiate timestamps
        
        # Get performance history
        history = perf_monitor.get_performance_history(component, operation)
        
        assert len(history) == 10
        assert all("timestamp" in entry for entry in history)
        assert all("execution_time" in entry for entry in history)
        
        # Verify chronological order
        timestamps = [entry["timestamp"] for entry in history]
        assert timestamps == sorted(timestamps)
    
    def test_performance_report_generation(self, perf_monitor):
        """Test comprehensive performance report generation"""
        # Add some test data
        perf_monitor.track_operation("component1", "operation1", 100)
        perf_monitor.track_operation("component1", "operation2", 200)
        perf_monitor.track_operation("component2", "operation1", 150)
        
        # Generate report
        report = perf_monitor.generate_performance_report()
        
        assert isinstance(report, dict)
        assert "report_timestamp" in report
        assert "summary" in report
        assert "components" in report
        assert "slow_operations" in report
        assert "cache_statistics" in report
        assert "resource_usage" in report
        
        # Verify summary
        summary = report["summary"]
        assert "total_components" in summary
        assert "total_operations" in summary
        assert "avg_response_time" in summary
    
    def test_cache_hit_rate_tracking(self, perf_monitor):
        """Test cache hit rate tracking"""
        cache_key = "test_cache_key"
        
        # Simulate cache miss
        perf_monitor.cache_manager.record_cache_miss(cache_key)
        
        # Simulate cache hits
        for _ in range(3):
            perf_monitor.cache_manager.record_cache_hit(cache_key)
        
        # Check hit rate
        hit_rate = perf_monitor.cache_manager.get_cache_hit_rate()
        assert 0.70 <= hit_rate <= 0.80  # 3 hits out of 4 total (75%)
    
    def test_resource_monitoring(self, perf_monitor):
        """Test resource monitoring functionality"""
        # Get current resource usage
        resource_usage = perf_monitor.resource_monitor.get_current_usage()
        
        assert isinstance(resource_usage, dict)
        assert "cpu_percent" in resource_usage
        assert "memory_mb" in resource_usage
        assert "timestamp" in resource_usage
        
        # Verify reasonable values
        assert 0 <= resource_usage["cpu_percent"] <= 100
        assert resource_usage["memory_mb"] > 0


class TestCacheManager:
    """Test the cache management component"""
    
    @pytest.fixture
    def cache_manager(self):
        return CacheManager(max_size=100, ttl_seconds=300)
    
    def test_cache_basic_operations(self, cache_manager):
        """Test basic cache operations"""
        key = "test_key"
        value = "test_value"
        
        # Set value
        cache_manager.set(key, value)
        
        # Get value
        retrieved = cache_manager.get(key)
        assert retrieved == value
        
        # Test cache hit recording
        assert cache_manager.cache_hits > 0
    
    def test_cache_miss_handling(self, cache_manager):
        """Test cache miss handling"""
        # Try to get non-existent key
        result = cache_manager.get("non_existent_key")
        assert result is None
        
        # Verify cache miss was recorded
        assert cache_manager.cache_misses > 0
    
    def test_cache_ttl_expiration(self, cache_manager):
        """Test cache TTL expiration"""
        # Create cache with short TTL
        short_ttl_cache = CacheManager(max_size=10, ttl_seconds=0.1)
        
        key = "ttl_test_key"
        value = "ttl_test_value"
        
        # Set value
        short_ttl_cache.set(key, value)
        
        # Immediately retrieve (should hit)
        assert short_ttl_cache.get(key) == value
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should now be expired
        assert short_ttl_cache.get(key) is None
    
    def test_cache_size_limits(self, cache_manager):
        """Test cache size limit enforcement"""
        # Create small cache
        small_cache = CacheManager(max_size=3, ttl_seconds=300)
        
        # Fill cache beyond capacity
        for i in range(5):
            small_cache.set(f"key_{i}", f"value_{i}")
        
        # Cache should only contain the most recent items
        assert len(small_cache.cache) <= 3
        
        # Most recent items should still be accessible
        assert small_cache.get("key_4") == "value_4"
        assert small_cache.get("key_3") == "value_3"
    
    def test_cache_hit_rate_calculation(self, cache_manager):
        """Test cache hit rate calculation"""
        # Start with clean cache
        cache_manager.cache_hits = 0
        cache_manager.cache_misses = 0
        
        # Generate hits and misses
        cache_manager.set("key1", "value1")
        cache_manager.get("key1")  # Hit
        cache_manager.get("key1")  # Hit
        cache_manager.get("key2")  # Miss
        
        hit_rate = cache_manager.get_cache_hit_rate()
        assert 0.6 <= hit_rate <= 0.7  # 2 hits out of 3 total
    
    def test_cache_statistics(self, cache_manager):
        """Test cache statistics reporting"""
        # Perform various cache operations
        cache_manager.set("key1", "value1")
        cache_manager.get("key1")  # Hit
        cache_manager.get("key2")  # Miss
        
        stats = cache_manager.get_cache_statistics()
        
        assert isinstance(stats, dict)
        assert "hit_rate" in stats
        assert "total_hits" in stats
        assert "total_misses" in stats
        assert "cache_size" in stats
        assert "max_size" in stats


class TestResourceMonitor:
    """Test the resource monitoring component"""
    
    @pytest.fixture
    def resource_monitor(self):
        return ResourceMonitor()
    
    def test_current_usage_monitoring(self, resource_monitor):
        """Test current resource usage monitoring"""
        usage = resource_monitor.get_current_usage()
        
        assert isinstance(usage, dict)
        required_fields = ["cpu_percent", "memory_mb", "timestamp"]
        for field in required_fields:
            assert field in usage
        
        # Validate reasonable values
        assert 0 <= usage["cpu_percent"] <= 100
        assert usage["memory_mb"] > 0
    
    def test_resource_history_tracking(self, resource_monitor):
        """Test resource usage history tracking"""
        # Start monitoring
        resource_monitor.start_monitoring(interval_seconds=0.1)
        
        # Let it collect some data
        time.sleep(0.3)
        
        # Stop monitoring
        resource_monitor.stop_monitoring()
        
        # Get history
        history = resource_monitor.get_resource_history()
        
        assert isinstance(history, list)
        assert len(history) >= 2  # Should have collected at least 2 data points
        
        for entry in history:
            assert "cpu_percent" in entry
            assert "memory_mb" in entry
            assert "timestamp" in entry
    
    def test_high_usage_detection(self, resource_monitor):
        """Test high resource usage detection"""
        # Set low thresholds for testing
        resource_monitor.high_cpu_threshold = 1.0  # Very low threshold
        resource_monitor.high_memory_threshold_mb = 1.0  # Very low threshold
        
        # Check for high usage (should trigger with low thresholds)
        high_usage = resource_monitor.detect_high_usage()
        
        assert isinstance(high_usage, dict)
        assert "high_cpu" in high_usage
        assert "high_memory" in high_usage
        
        # At least one should be True with very low thresholds
        assert high_usage["high_cpu"] or high_usage["high_memory"]
    
    def test_resource_monitoring_thread_safety(self, resource_monitor):
        """Test thread safety of resource monitoring"""
        def monitor_resources():
            for _ in range(10):
                resource_monitor.get_current_usage()
                time.sleep(0.01)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=monitor_resources)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should complete without errors
        assert True


class TestPerformanceMetrics:
    """Test the performance metrics data structure"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = PerformanceMetrics("test_component")
        
        assert metrics.component_name == "test_component"
        assert isinstance(metrics.operations, dict)
        assert metrics.total_operations == 0
        assert metrics.total_execution_time == 0.0
    
    def test_operation_recording(self):
        """Test operation recording in metrics"""
        metrics = PerformanceMetrics("test_component")
        
        # Record operation
        metrics.record_operation("test_op", 100.0)
        
        assert "test_op" in metrics.operations
        op_data = metrics.operations["test_op"]
        
        assert op_data["total_calls"] == 1
        assert op_data["total_time"] == 100.0
        assert op_data["avg_time"] == 100.0
        assert op_data["min_time"] == 100.0
        assert op_data["max_time"] == 100.0
    
    def test_multiple_operation_recording(self):
        """Test recording multiple operations"""
        metrics = PerformanceMetrics("test_component")
        
        # Record multiple calls to same operation
        execution_times = [100.0, 200.0, 150.0]
        for time_ms in execution_times:
            metrics.record_operation("test_op", time_ms)
        
        op_data = metrics.operations["test_op"]
        
        assert op_data["total_calls"] == 3
        assert op_data["total_time"] == sum(execution_times)
        assert abs(op_data["avg_time"] - (sum(execution_times) / 3)) < 0.1
        assert op_data["min_time"] == min(execution_times)
        assert op_data["max_time"] == max(execution_times)
    
    def test_metrics_summary(self):
        """Test metrics summary generation"""
        metrics = PerformanceMetrics("test_component")
        
        # Record some operations
        metrics.record_operation("op1", 100.0)
        metrics.record_operation("op2", 200.0)
        metrics.record_operation("op1", 150.0)  # Second call to op1
        
        summary = metrics.get_summary()
        
        assert isinstance(summary, dict)
        assert summary["component_name"] == "test_component"
        assert summary["total_operations"] == 3
        assert summary["unique_operations"] == 2
        assert summary["total_execution_time"] == 450.0


class TestPerformanceIntegration:
    """Test integration scenarios for performance monitoring"""
    
    def test_end_to_end_monitoring(self, perf_monitor):
        """Test end-to-end performance monitoring scenario"""
        @performance_monitor(perf_monitor, "integration_test", "complex_operation", use_cache=True)
        def complex_operation(param1, param2=None):
            # Simulate complex processing
            time.sleep(0.05)  # 50ms processing time
            return f"result_{param1}_{param2}"
        
        # Execute multiple operations
        results = []
        for i in range(5):
            result = complex_operation(f"param_{i}", param2="test")
            results.append(result)
        
        # Verify results
        assert len(results) == 5
        assert all("result_" in result for result in results)
        
        # Verify monitoring data
        metrics = perf_monitor.get_performance_metrics("integration_test")
        assert "complex_operation" in metrics.operations
        
        # Generate comprehensive report
        report = perf_monitor.generate_performance_report()
        assert "integration_test" in report["components"]
    
    def test_concurrent_monitoring(self, perf_monitor):
        """Test performance monitoring under concurrent load"""
        def worker_function(worker_id):
            @performance_monitor(perf_monitor, f"worker_{worker_id}", "concurrent_op")
            def concurrent_operation():
                time.sleep(0.01)  # Small processing time
                return f"worker_{worker_id}_result"
            
            # Execute multiple operations
            for _ in range(10):
                concurrent_operation()
        
        # Start multiple worker threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all workers were monitored
        report = perf_monitor.generate_performance_report()
        worker_components = [name for name in report["components"].keys() if name.startswith("worker_")]
        assert len(worker_components) == 3
    
    def test_performance_degradation_detection(self, perf_monitor):
        """Test detection of performance degradation"""
        operation_name = "degradation_test"
        
        @performance_monitor(perf_monitor, "degradation_component", operation_name)
        def degrading_operation(delay_ms):
            time.sleep(delay_ms / 1000.0)
            return "result"
        
        # Simulate performance degradation
        delays = [10, 20, 30, 50, 80, 130]  # Increasing delays
        for delay in delays:
            degrading_operation(delay)
        
        # Analyze performance trends
        history = perf_monitor.get_performance_history("degradation_component", operation_name)
        
        # Should show increasing execution times
        execution_times = [entry["execution_time"] for entry in history]
        
        # Last execution should be significantly slower than first
        assert execution_times[-1] > execution_times[0] * 2
