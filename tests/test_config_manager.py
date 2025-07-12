"""
Test Suite for Configuration Management System
==============================================

Comprehensive tests for the advanced configuration management system,
validating dynamic reloading, environment awareness, and validation.

Author: Claude AI (Anthropic)
"""

import pytest
import json
import yaml
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from cover_letter_generator.config_manager import (
    ConfigurationManager, ApplicationConfig, Environment,
    ConfigSource, ConfigValue, ConfigurationValidator
)


class TestConfigurationManager:
    """Test the configuration manager main functionality"""
    
    @pytest.fixture
    def temp_config_file(self, temp_directory):
        """Create temporary config file for testing"""
        config_data = {
            "openai": {
                "model": "gpt-4",
                "max_tokens": 1500,
                "temperature": 0.8
            },
            "performance": {
                "cache_size": 500,
                "enable_monitoring": True
            },
            "logging": {
                "log_level": "DEBUG"
            }
        }
        
        config_file = Path(temp_directory) / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        return str(config_file)
    
    def test_config_manager_initialization(self, temp_config_file):
        """Test proper initialization of configuration manager"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        assert config_manager is not None
        assert config_manager.config_file == temp_config_file
        assert config_manager.environment == Environment.TESTING
        assert isinstance(config_manager.config, ApplicationConfig)
        assert isinstance(config_manager.validator, ConfigurationValidator)
    
    def test_environment_detection(self):
        """Test automatic environment detection"""
        # Test with environment variable
        with patch.dict(os.environ, {'COVER_LETTER_ENV': 'production'}):
            config_manager = ConfigurationManager()
            assert config_manager.environment == Environment.PRODUCTION
        
        # Test with development default
        with patch.dict(os.environ, {}, clear=True):
            config_manager = ConfigurationManager()
            assert config_manager.environment == Environment.DEVELOPMENT
    
    def test_config_file_loading(self, temp_config_file):
        """Test configuration file loading"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        # Verify file configuration was applied
        assert config_manager.config.openai.model == "gpt-4"
        assert config_manager.config.openai.max_tokens == 1500
        assert config_manager.config.openai.temperature == 0.8
        assert config_manager.config.performance.cache_size == 500
        assert config_manager.config.logging.log_level == "DEBUG"
    
    def test_environment_variable_overrides(self, temp_config_file):
        """Test environment variable overrides"""
        env_vars = {
            'OPENAI_API_KEY': 'test-override-key',
            'OPENAI_MODEL': 'gpt-3.5-turbo',
            'CACHE_SIZE': '200',
            'DEBUG_MODE': 'true',
            'LOG_LEVEL': 'INFO'
        }
        
        with patch.dict(os.environ, env_vars):
            config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
            
            # Verify environment variables override file config
            assert config_manager.config.openai.api_key == "test-override-key"
            assert config_manager.config.openai.model == "gpt-3.5-turbo"
            assert config_manager.config.performance.cache_size == 200
            assert config_manager.config.debug_mode is True
            assert config_manager.config.logging.log_level == "INFO"
    
    def test_environment_specific_settings(self):
        """Test environment-specific configuration settings"""
        # Test production environment
        prod_config = ConfigurationManager(environment=Environment.PRODUCTION)
        assert prod_config.config.debug_mode is False
        assert prod_config.config.logging.log_level == "INFO"
        assert prod_config.config.security.encrypt_sensitive_data is True
        
        # Test development environment
        dev_config = ConfigurationManager(environment=Environment.DEVELOPMENT)
        assert dev_config.config.debug_mode is True
        assert dev_config.config.logging.log_level == "DEBUG"
        
        # Test demo environment
        demo_config = ConfigurationManager(environment=Environment.DEMO)
        assert demo_config.config.openai.api_key == ""  # Allow empty in demo
        assert demo_config.config.performance.cache_size == 50
    
    def test_configuration_validation(self, temp_config_file):
        """Test configuration validation"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        # Test valid configuration
        errors = config_manager.validator.validate_config(config_manager.config)
        assert isinstance(errors, list)
        
        # Test invalid configuration
        config_manager.config.performance.cache_size = -1  # Invalid value
        errors = config_manager.validator.validate_config(config_manager.config)
        assert len(errors) > 0
        assert any("cache_size" in error for error in errors)
    
    def test_dynamic_configuration_updates(self, temp_config_file):
        """Test dynamic configuration updates"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        # Test setting configuration value
        original_cache_size = config_manager.config.performance.cache_size
        config_manager.set_config_value("performance", "cache_size", 1000)
        
        assert config_manager.config.performance.cache_size == 1000
        assert config_manager.config.performance.cache_size != original_cache_size
        
        # Test validation on invalid update
        with pytest.raises(ValueError):
            config_manager.set_config_value("performance", "cache_size", -1)
    
    def test_configuration_change_notifications(self, temp_config_file):
        """Test configuration change notification system"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        # Setup change listener
        changes_received = []
        def change_listener(changes):
            changes_received.append(changes)
        
        config_manager.add_change_listener(change_listener)
        
        # Trigger configuration change
        config_manager.set_config_value("performance", "cache_size", 800)
        
        # Verify listener was called
        assert len(changes_received) > 0
        
        # Remove listener
        config_manager.remove_change_listener(change_listener)
    
    def test_configuration_export(self, temp_config_file, temp_directory):
        """Test configuration export functionality"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        # Export configuration
        export_path = Path(temp_directory) / "exported_config.json"
        config_manager.export_config(str(export_path), include_sensitive=False)
        
        # Verify exported file
        assert export_path.exists()
        
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert "configuration" in exported_data
        assert "environment" in exported_data
        assert exported_data["environment"] == "testing"
        
        # Verify sensitive data is hidden
        if "openai" in exported_data["configuration"]:
            api_key = exported_data["configuration"]["openai"].get("api_key", "")
            assert api_key == "" or api_key == "***HIDDEN***"
    
    def test_configuration_summary(self, temp_config_file):
        """Test configuration summary generation"""
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        
        summary = config_manager.get_configuration_summary()
        
        assert isinstance(summary, dict)
        required_fields = [
            "environment", "config_file", "file_exists",
            "total_config_values", "sources_breakdown",
            "last_reload", "validation_status"
        ]
        
        for field in required_fields:
            assert field in summary
        
        assert summary["environment"] == "testing"
        assert summary["file_exists"] is True
        assert summary["total_config_values"] > 0
    
    def test_file_watching_functionality(self, temp_config_file):
        """Test configuration file watching"""
        config_manager = ConfigurationManager(temp_config_file, Environment.DEVELOPMENT)
        
        # File watching should be active in development
        assert config_manager._file_watch_thread is not None
        
        # Stop file watching
        config_manager.stop_file_watching()
        
        # Verify stopped
        if config_manager._file_watch_thread:
            assert not config_manager._file_watch_thread.is_alive()


class TestConfigurationValidator:
    """Test the configuration validation component"""
    
    @pytest.fixture
    def validator(self):
        return ConfigurationValidator()
    
    def test_basic_validation_rules(self, validator):
        """Test basic validation rules"""
        config = ApplicationConfig()
        
        # Test valid configuration
        errors = validator.validate_config(config)
        assert isinstance(errors, list)
        
        # Test invalid API key format
        config.openai.api_key = "invalid-key"
        errors = validator.validate_config(config)
        assert any("api_key" in error for error in errors)
        
        # Test valid API key format
        config.openai.api_key = "valid-test-key-format"
        errors = validator.validate_config(config)
        api_key_errors = [error for error in errors if "api_key" in error]
        assert len(api_key_errors) == 0
    
    def test_cross_dependency_validation(self, validator):
        """Test cross-component dependency validation"""
        config = ApplicationConfig()
        
        # Test performance vs memory consistency
        config.performance.cache_size = 2000
        config.memory.max_skills = 100  # Cache larger than max skills
        
        errors = validator.validate_config(config)
        assert any("cache size" in error.lower() for error in errors)
        
        # Test production environment validations
        config.environment = Environment.PRODUCTION
        config.debug_mode = True  # Should not be enabled in production
        config.openai.api_key = ""  # Required in production
        
        errors = validator.validate_config(config)
        assert any("debug mode" in error.lower() for error in errors)
        assert any("api key" in error.lower() for error in errors)
    
    def test_validation_rule_configuration(self, validator):
        """Test validation rule configuration"""
        # Test cache size validation
        config = ApplicationConfig()
        config.performance.cache_size = 5  # Below minimum
        
        errors = validator.validate_config(config)
        assert any("cache_size" in error for error in errors)
        
        # Test valid cache size
        config.performance.cache_size = 100
        errors = validator.validate_config(config)
        cache_errors = [error for error in errors if "cache_size" in error]
        assert len(cache_errors) == 0
    
    def test_flatten_dict_functionality(self, validator):
        """Test dictionary flattening for validation"""
        nested_dict = {
            "level1": {
                "level2": {
                    "level3": "value"
                },
                "simple": "value"
            },
            "root": "value"
        }
        
        flattened = validator._flatten_dict(nested_dict)
        
        assert "level1.level2.level3" in flattened
        assert flattened["level1.level2.level3"] == "value"
        assert "level1.simple" in flattened
        assert "root" in flattened


class TestConfigValue:
    """Test the ConfigValue data structure"""
    
    def test_config_value_creation(self):
        """Test config value creation"""
        config_value = ConfigValue(
            value="test_value",
            source=ConfigSource.CONFIG_FILE,
            last_updated=datetime.now(),
            description="Test configuration value",
            is_sensitive=False
        )
        
        assert config_value.value == "test_value"
        assert config_value.source == ConfigSource.CONFIG_FILE
        assert config_value.description == "Test configuration value"
        assert config_value.is_sensitive is False
    
    def test_config_value_serialization(self):
        """Test config value serialization"""
        # Test non-sensitive value
        config_value = ConfigValue(
            value="visible_value",
            source=ConfigSource.ENVIRONMENT_VARIABLE,
            last_updated=datetime.now(),
            is_sensitive=False
        )
        
        serialized = config_value.to_dict()
        assert serialized["value"] == "visible_value"
        assert serialized["source"] == "env_var"
        assert serialized["is_sensitive"] is False
        
        # Test sensitive value
        sensitive_value = ConfigValue(
            value="secret_key",
            source=ConfigSource.ENVIRONMENT_VARIABLE,
            last_updated=datetime.now(),
            is_sensitive=True
        )
        
        serialized = sensitive_value.to_dict()
        assert serialized["value"] == "***HIDDEN***"
        assert serialized["is_sensitive"] is True


class TestApplicationConfig:
    """Test the ApplicationConfig data structure"""
    
    def test_config_initialization(self):
        """Test configuration initialization with defaults"""
        config = ApplicationConfig()
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug_mode is False
        assert config.app_name == "Cover Letter GPT"
        assert isinstance(config.openai.model, str)
        assert isinstance(config.performance.cache_size, int)
        assert isinstance(config.relevance.relevance_threshold, float)
    
    def test_config_serialization(self):
        """Test configuration serialization"""
        config = ApplicationConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "environment" in config_dict
        assert "openai" in config_dict
        assert "performance" in config_dict
        assert "relevance" in config_dict
        
        # Test nested structure
        assert "model" in config_dict["openai"]
        assert "cache_size" in config_dict["performance"]
    
    def test_config_component_validation(self):
        """Test individual component configuration validation"""
        # Test OpenAI config validation
        with pytest.raises(ValueError):
            from cover_letter_generator.config_manager import OpenAIConfig
            OpenAIConfig(temperature=3.0)  # Invalid temperature
        
        # Test Performance config validation
        with pytest.raises(ValueError):
            from cover_letter_generator.config_manager import PerformanceConfig
            PerformanceConfig(cache_size=5)  # Below minimum


class TestConfigurationIntegration:
    """Test configuration integration scenarios"""
    
    def test_json_config_file_support(self, temp_directory):
        """Test JSON configuration file support"""
        config_data = {
            "openai": {
                "model": "gpt-4",
                "temperature": 0.7
            },
            "performance": {
                "cache_size": 300
            }
        }
        
        config_file = Path(temp_directory) / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config_manager = ConfigurationManager(str(config_file), Environment.TESTING)
        
        assert config_manager.config.openai.model == "gpt-4"
        assert config_manager.config.openai.temperature == 0.7
        assert config_manager.config.performance.cache_size == 300
    
    def test_missing_config_file_handling(self):
        """Test handling of missing configuration file"""
        # Should use defaults when config file doesn't exist
        config_manager = ConfigurationManager("non_existent_file.yaml", Environment.TESTING)
        
        assert config_manager.config is not None
        assert isinstance(config_manager.config, ApplicationConfig)
    
    def test_malformed_config_file_handling(self, temp_directory):
        """Test handling of malformed configuration file"""
        # Create malformed YAML file
        malformed_file = Path(temp_directory) / "malformed.yaml"
        with open(malformed_file, 'w') as f:
            f.write("invalid: yaml: content: [\n")  # Malformed YAML
        
        # Should handle gracefully and use defaults
        config_manager = ConfigurationManager(str(malformed_file), Environment.TESTING)
        assert config_manager.config is not None
    
    def test_concurrent_configuration_access(self, temp_config_file):
        """Test concurrent access to configuration"""
        import threading
        
        config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
        results = []
        
        def config_accessor(thread_id):
            for i in range(10):
                config = config_manager.get_config()
                results.append((thread_id, config.openai.model))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=config_accessor, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All should have succeeded
        assert len(results) == 30  # 3 threads * 10 operations
        assert all(model == "gpt-4" for _, model in results)
    
    def test_configuration_hot_reload(self, temp_config_file):
        """Test configuration hot reload functionality"""
        config_manager = ConfigurationManager(temp_config_file, Environment.DEVELOPMENT)
        
        original_model = config_manager.config.openai.model
        assert original_model == "gpt-4"
        
        # Update config file
        config_data = {
            "openai": {
                "model": "gpt-3.5-turbo",  # Changed model
                "max_tokens": 1500,
                "temperature": 0.8
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Manually trigger reload (in real scenario, file watcher would do this)
        config_manager.reload_configuration()
        
        # Verify configuration was updated
        assert config_manager.config.openai.model == "gpt-3.5-turbo"
        assert config_manager.config.openai.model != original_model
    
    def test_configuration_source_tracking(self, temp_config_file):
        """Test tracking of configuration value sources"""
        env_vars = {'OPENAI_MODEL': 'env-override-model'}
        
        with patch.dict(os.environ, env_vars):
            config_manager = ConfigurationManager(temp_config_file, Environment.TESTING)
            
            # Check that source tracking works
            model_config = config_manager.get_config_value("openai.model")
            assert model_config is not None
            assert model_config.source == ConfigSource.ENVIRONMENT_VARIABLE
            assert model_config.value == "env-override-model"
            
            # File-based config should also be tracked
            tokens_config = config_manager.get_config_value("openai.max_tokens")
            if tokens_config:  # May not exist in all test scenarios
                assert tokens_config.source == ConfigSource.CONFIG_FILE