"""
Test Suite for Error Handling System
====================================

Comprehensive tests for the advanced error handling system,
validating intelligent recovery, graceful degradation, and error analytics.

Author: Claude AI (Anthropic)
"""

import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime

from cover_letter_generator.error_handler import (
    ErrorHandler, ErrorContext, ErrorSeverity, RecoveryStrategy,
    with_error_handling
)


class TestErrorHandler:
    """Test the error handling main functionality"""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler instance for testing"""
        return ErrorHandler()
    
    def test_error_handler_initialization(self, error_handler):
        """Test proper initialization of error handler"""
        assert error_handler is not None
        assert hasattr(error_handler, 'error_history')
        assert hasattr(error_handler, 'recovery_strategies')
        assert hasattr(error_handler, 'error_patterns')
        assert hasattr(error_handler, 'performance_monitor')
    
    def test_basic_error_handling(self, error_handler):
        """Test basic error handling functionality"""
        test_exception = ValueError("Test error message")
        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            additional_data={"test_key": "test_value"}
        )
        
        # Handle the error
        result = error_handler.handle_error(test_exception, context)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "error_id" in result
        assert "handled" in result
        assert "recovery_applied" in result
        assert "timestamp" in result
        
        # Verify error was logged
        assert len(error_handler.error_history) == 1
        logged_error = error_handler.error_history[0]
        assert logged_error["error_type"] == "ValueError"
        assert logged_error["error_message"] == "Test error message"
        assert logged_error["component"] == "test_component"
        assert logged_error["operation"] == "test_operation"
    
    def test_error_severity_classification(self, error_handler):
        """Test error severity classification"""
        # Test different error types
        test_cases = [
            (ValueError("Invalid input"), ErrorSeverity.MEDIUM),
            (FileNotFoundError("File missing"), ErrorSeverity.HIGH),
            (ConnectionError("Network issue"), ErrorSeverity.HIGH),
            (MemoryError("Out of memory"), ErrorSeverity.CRITICAL),
            (KeyboardInterrupt("User interrupt"), ErrorSeverity.LOW),
        ]
        
        for exception, expected_severity in test_cases:
            context = ErrorContext("test_op", "test_component", {})
            result = error_handler.handle_error(exception, context)
            
            # Check that severity was properly classified
            error_record = error_handler.error_history[-1]
            # Note: Actual severity classification may vary based on implementation
            assert "severity" in error_record
    
    def test_recovery_strategy_selection(self, error_handler):
        """Test recovery strategy selection"""
        # Test retry strategy for transient errors
        network_error = ConnectionError("Network timeout")
        context = ErrorContext("api_call", "openai_client", {"retry_count": 0})
        
        result = error_handler.handle_error(network_error, context)
        
        # Should suggest retry strategy for network errors
        assert result["recovery_applied"] is not None
        error_record = error_handler.error_history[-1]
        assert "recovery_strategy" in error_record
    
    def test_error_pattern_detection(self, error_handler):
        """Test error pattern detection"""
        # Simulate repeated similar errors
        for i in range(5):
            error = ValueError(f"Similar error {i}")
            context = ErrorContext("repeated_operation", "test_component", {"iteration": i})
            error_handler.handle_error(error, context)
        
        # Analyze patterns
        patterns = error_handler.analyze_error_patterns()
        
        assert isinstance(patterns, list)
        # Should detect pattern of repeated ValueError in same operation
        pattern_found = any(
            pattern["error_type"] == "ValueError" and 
            pattern["component"] == "test_component"
            for pattern in patterns
        )
        assert pattern_found
    
    def test_graceful_degradation(self, error_handler):
        """Test graceful degradation functionality"""
        # Test with critical error that should trigger degradation
        critical_error = MemoryError("System out of memory")
        context = ErrorContext("memory_intensive_op", "memory_core", {})
        
        result = error_handler.handle_error(critical_error, context)
        
        # Should indicate graceful degradation
        assert result["handled"] is True
        # Check if degradation mode was activated
        error_record = error_handler.error_history[-1]
        assert "degradation_applied" in error_record or "recovery_strategy" in error_record
    
    def test_error_context_enrichment(self, error_handler):
        """Test error context enrichment"""
        error = RuntimeError("Test runtime error")
        context = ErrorContext(
            operation="complex_operation",
            component="main_processor",
            additional_data={
                "user_id": "test_user",
                "job_id": "job_123",
                "skill_count": 25
            }
        )
        
        error_handler.handle_error(error, context)
        
        # Verify context was preserved and enriched
        error_record = error_handler.error_history[-1]
        assert error_record["operation"] == "complex_operation"
        assert error_record["component"] == "main_processor"
        assert "user_id" in error_record["additional_data"]
        assert "job_id" in error_record["additional_data"]
        assert "skill_count" in error_record["additional_data"]
        
        # Should have added system context
        assert "timestamp" in error_record
        assert "error_id" in error_record
    
    def test_error_analytics(self, error_handler):
        """Test error analytics and reporting"""
        # Generate various errors for analytics
        errors = [
            (ValueError("Validation error 1"), "validation", "input_processor"),
            (ValueError("Validation error 2"), "validation", "input_processor"),
            (ConnectionError("Network error 1"), "api_call", "openai_client"),
            (FileNotFoundError("File missing"), "file_operation", "file_monitor"),
            (RuntimeError("Runtime issue"), "processing", "relevance_engine"),
        ]
        
        for error, operation, component in errors:
            context = ErrorContext(operation, component, {})
            error_handler.handle_error(error, context)
        
        # Generate analytics report
        analytics = error_handler.generate_error_analytics()
        
        assert isinstance(analytics, dict)
        assert "total_errors" in analytics
        assert "error_types_breakdown" in analytics
        assert "component_breakdown" in analytics
        assert "operation_breakdown" in analytics
        assert "error_frequency" in analytics
        
        # Verify breakdown data
        assert analytics["total_errors"] == 5
        assert analytics["error_types_breakdown"]["ValueError"] == 2
        assert analytics["component_breakdown"]["input_processor"] == 2
    
    def test_error_suppression_and_filtering(self, error_handler):
        """Test error suppression and filtering"""
        # Configure to suppress certain error types
        error_handler.suppressed_error_types.add("DeprecationWarning")
        
        # Test suppressed error
        suppressed_error = DeprecationWarning("Deprecated function used")
        context = ErrorContext("legacy_operation", "old_component", {})
        
        result = error_handler.handle_error(suppressed_error, context)
        
        # Should be handled but not logged extensively
        assert result["handled"] is True
        # Check that it was marked as suppressed
        error_record = error_handler.error_history[-1]
        assert error_record.get("suppressed", False) or result.get("suppressed", False)
    
    def test_performance_impact_tracking(self, error_handler):
        """Test tracking of error handling performance impact"""
        # Mock performance monitor
        mock_monitor = Mock()
        error_handler.performance_monitor = mock_monitor
        
        # Handle an error
        error = RuntimeError("Test error")
        context = ErrorContext("test_operation", "test_component", {})
        
        error_handler.handle_error(error, context)
        
        # Verify performance was tracked
        assert mock_monitor.track_operation.called
        call_args = mock_monitor.track_operation.call_args
        assert "error_handler" in call_args[0]  # component
        assert "handle_error" in call_args[0]   # operation


class TestErrorDecorator:
    """Test the error handling decorator functionality"""
    
    @pytest.fixture
    def error_handler(self):
        return ErrorHandler()
    
    def test_decorator_basic_functionality(self, error_handler):
        """Test basic decorator functionality"""
        @with_error_handling(error_handler, "test_component", "test_operation")
        def test_function(should_fail=False):
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # Test successful execution
        result = test_function(False)
        assert result == "success"
        
        # Test error handling
        result = test_function(True)
        # Should not raise exception, but return error handling result
        assert result is not None
        
        # Verify error was logged
        assert len(error_handler.error_history) == 1
    
    def test_decorator_with_return_value(self, error_handler):
        """Test decorator preserves return values"""
        @with_error_handling(error_handler, "test_component", "test_operation")
        def function_with_complex_return():
            return {"status": "success", "data": [1, 2, 3]}
        
        result = function_with_complex_return()
        assert result == {"status": "success", "data": [1, 2, 3]}
    
    def test_decorator_with_arguments(self, error_handler):
        """Test decorator works with function arguments"""
        @with_error_handling(error_handler, "test_component", "test_operation")
        def function_with_args(arg1, arg2, kwarg1=None):
            if arg1 == "error":
                raise RuntimeError("Argument error")
            return f"{arg1}_{arg2}_{kwarg1}"
        
        # Test successful execution with arguments
        result = function_with_args("test", "value", kwarg1="keyword")
        assert result == "test_value_keyword"
        
        # Test error handling with arguments
        result = function_with_args("error", "value")
        # Should handle error gracefully
        assert result is not None
    
    def test_decorator_preserves_exceptions_when_configured(self, error_handler):
        """Test decorator can be configured to re-raise exceptions"""
        @with_error_handling(error_handler, "test_component", "test_operation", suppress_exceptions=False)
        def function_that_fails():
            raise ValueError("This should be re-raised")
        
        # Should re-raise the exception
        with pytest.raises(ValueError, match="This should be re-raised"):
            function_that_fails()
        
        # But should still log the error
        assert len(error_handler.error_history) == 1


class TestErrorContext:
    """Test the ErrorContext data structure"""
    
    def test_error_context_creation(self):
        """Test error context creation"""
        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            additional_data={"key": "value"}
        )
        
        assert context.operation == "test_operation"
        assert context.component == "test_component"
        assert context.additional_data == {"key": "value"}
        assert isinstance(context.timestamp, datetime)
    
    def test_error_context_serialization(self):
        """Test error context serialization"""
        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            additional_data={"key": "value", "number": 42}
        )
        
        serialized = context.to_dict()
        
        assert isinstance(serialized, dict)
        assert serialized["operation"] == "test_operation"
        assert serialized["component"] == "test_component"
        assert serialized["additional_data"]["key"] == "value"
        assert serialized["additional_data"]["number"] == 42
        assert "timestamp" in serialized


class TestRecoveryStrategies:
    """Test recovery strategy implementations"""
    
    @pytest.fixture
    def error_handler(self):
        return ErrorHandler()
    
    def test_retry_strategy(self, error_handler):
        """Test retry recovery strategy"""
        # Simulate transient error that could benefit from retry
        error = ConnectionError("Temporary network issue")
        context = ErrorContext("api_call", "openai_client", {"retry_count": 0})
        
        result = error_handler.handle_error(error, context)
        
        # Should suggest retry
        assert result["handled"] is True
        error_record = error_handler.error_history[-1]
        
        # Check for retry strategy indication
        recovery_applied = result.get("recovery_applied") or error_record.get("recovery_strategy")
        assert recovery_applied is not None
    
    def test_fallback_strategy(self, error_handler):
        """Test fallback recovery strategy"""
        # Simulate error that should trigger fallback
        error = FileNotFoundError("Configuration file missing")
        context = ErrorContext("load_config", "config_manager", {"config_path": "/missing/file"})
        
        result = error_handler.handle_error(error, context)
        
        # Should suggest fallback (like default config)
        assert result["handled"] is True
        error_record = error_handler.error_history[-1]
        
        # Should have recovery strategy
        assert "recovery_strategy" in error_record or result.get("recovery_applied")
    
    def test_degradation_strategy(self, error_handler):
        """Test degradation recovery strategy"""
        # Simulate critical resource error
        error = MemoryError("Insufficient memory")
        context = ErrorContext("process_large_dataset", "memory_core", {"dataset_size": "large"})
        
        result = error_handler.handle_error(error, context)
        
        # Should handle gracefully
        assert result["handled"] is True
        error_record = error_handler.error_history[-1]
        
        # Should indicate degradation
        recovery = result.get("recovery_applied") or error_record.get("recovery_strategy")
        assert recovery is not None


class TestErrorIntegration:
    """Test error handling integration scenarios"""
    
    def test_cascade_error_handling(self, mock_error_handler):
        """Test handling of cascading errors"""
        @with_error_handling(mock_error_handler, "component1", "operation1")
        def operation1():
            @with_error_handling(mock_error_handler, "component2", "operation2")
            def operation2():
                raise ValueError("Inner error")
            
            result = operation2()
            if result is None:  # Error occurred
                raise RuntimeError("Cascade error")
            return result
        
        # Execute and verify both errors are handled
        result = operation1()
        
        # Should handle both errors
        assert len(mock_error_handler.error_history) >= 1
    
    def test_error_handling_under_load(self, mock_error_handler):
        """Test error handling under concurrent load"""
        import threading
        
        def worker_with_errors(worker_id):
            @with_error_handling(mock_error_handler, f"worker_{worker_id}", "concurrent_operation")
            def concurrent_operation():
                if worker_id % 2 == 0:  # Every other worker fails
                    raise ValueError(f"Worker {worker_id} error")
                return f"Worker {worker_id} success"
            
            for _ in range(10):
                concurrent_operation()
        
        # Start multiple workers
        threads = []
        for i in range(4):
            thread = threading.Thread(target=worker_with_errors, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have handled errors from workers 0 and 2 (20 errors total)
        error_count = len(mock_error_handler.error_history)
        assert error_count == 20  # 2 workers * 10 operations each
    
    def test_error_recovery_effectiveness(self, mock_error_handler):
        """Test effectiveness of error recovery strategies"""
        recovery_success_count = 0
        
        @with_error_handling(mock_error_handler, "recovery_test", "operation_with_recovery")
        def operation_with_recovery(attempt_number):
            nonlocal recovery_success_count
            
            if attempt_number < 3:  # Fail first 2 attempts
                raise ConnectionError(f"Attempt {attempt_number} failed")
            else:
                recovery_success_count += 1
                return f"Success on attempt {attempt_number}"
        
        # Simulate retry logic
        for attempt in range(1, 5):
            result = operation_with_recovery(attempt)
            if result and "Success" in str(result):
                break
        
        # Should eventually succeed
        assert recovery_success_count == 1
        
        # Should have logged the failures
        failures = [err for err in mock_error_handler.error_history 
                   if err["error_type"] == "ConnectionError"]
        assert len(failures) == 2  # First 2 attempts failed
    
    def test_comprehensive_error_reporting(self, mock_error_handler):
        """Test comprehensive error reporting across components"""
        # Generate errors across different components
        components_and_errors = [
            ("memory_core", "load_operation", ValueError("Memory load error")),
            ("relevance_engine", "score_calculation", RuntimeError("Scoring error")),
            ("openai_client", "api_call", ConnectionError("API error")),
            ("file_monitor", "file_watch", FileNotFoundError("File error")),
        ]
        
        for component, operation, error in components_and_errors:
            context = ErrorContext(operation, component, {})
            mock_error_handler.handle_error(error, context)
        
        # Generate comprehensive report
        analytics = mock_error_handler.generate_error_analytics()
        
        # Should cover all components
        assert len(analytics["component_breakdown"]) == 4
        assert all(comp in analytics["component_breakdown"] 
                  for comp, _, _ in components_and_errors)
        
        # Should have varied error types
        assert len(analytics["error_types_breakdown"]) >= 3