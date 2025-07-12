"""
Advanced Configuration Management System
=======================================

Sophisticated configuration management with environment-aware settings,
dynamic reloading, validation, and intelligent defaults.

Author: Claude AI (Anthropic)
Purpose: Ultra-fine-tuned configuration management for public GitHub showcase
"""

import os
import json
import yaml
from typing import Any, Dict, List, Optional, Union, Type
from pathlib import Path
from datetime import datetime
import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from copy import deepcopy

# Import our monitoring and error handling
from .performance_monitor import get_global_performance_monitor
from .error_handler import get_global_error_handler, ErrorContext


class Environment(Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    DEMO = "demo"


class ConfigSource(Enum):
    """Configuration sources in priority order"""
    ENVIRONMENT_VARIABLE = "env_var"
    CONFIG_FILE = "config_file"
    DEFAULT = "default"


@dataclass
class ConfigValue:
    """Container for configuration values with metadata"""
    value: Any
    source: ConfigSource
    last_updated: datetime
    description: str = ""
    is_sensitive: bool = False
    validation_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": "***HIDDEN***" if self.is_sensitive else self.value,
            "source": self.source.value,
            "last_updated": self.last_updated.isoformat(),
            "description": self.description,
            "is_sensitive": self.is_sensitive,
            "validation_rules": self.validation_rules
        }


@dataclass
class OpenAIConfig:
    """OpenAI service configuration"""
    api_key: str = ""
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_per_minute: int = 60
    
    def __post_init__(self):
        # Validation
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if self.max_tokens < 1 or self.max_tokens > 4000:
            raise ValueError("Max tokens must be between 1 and 4000")


@dataclass
class PerformanceConfig:
    """Performance and monitoring configuration"""
    enable_monitoring: bool = True
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600
    max_history: int = 10000
    slow_operation_threshold_ms: int = 1000
    high_memory_threshold_mb: int = 500
    high_cpu_threshold_percent: int = 80
    monitoring_interval_seconds: int = 30
    
    def __post_init__(self):
        if self.cache_size < 10:
            raise ValueError("Cache size must be at least 10")
        if self.max_history < 100:
            raise ValueError("Max history must be at least 100")


@dataclass
class RelevanceConfig:
    """Relevance engine configuration"""
    enable_semantic_matching: bool = True
    enable_industry_classification: bool = True
    enable_learning: bool = True
    relevance_threshold: float = 0.1
    max_skills_returned: int = 15
    confidence_threshold: float = 0.5
    learning_decay_days: int = 90
    semantic_similarity_weight: float = 0.3
    domain_boost_weight: float = 0.4
    industry_boost_multiplier: float = 1.5
    
    def __post_init__(self):
        if self.relevance_threshold < 0 or self.relevance_threshold > 1:
            raise ValueError("Relevance threshold must be between 0 and 1")
        if self.max_skills_returned < 1:
            raise ValueError("Max skills returned must be at least 1")


@dataclass
class FileMonitorConfig:
    """File monitoring configuration"""
    enable_auto_sync: bool = True
    check_interval_seconds: int = 60
    enable_backup: bool = True
    backup_retention_days: int = 30
    max_file_size_mb: int = 10
    watched_extensions: List[str] = field(default_factory=lambda: ['.txt', '.csv', '.json'])
    
    def __post_init__(self):
        if self.check_interval_seconds < 5:
            raise ValueError("Check interval must be at least 5 seconds")


@dataclass
class MemoryConfig:
    """Memory system configuration"""
    max_skills: int = 1000
    max_interactions: int = 10000
    enable_cleanup: bool = True
    cleanup_interval_days: int = 7
    skill_expiry_days: int = 365
    enable_analytics: bool = True
    memory_file_backup: bool = True
    
    def __post_init__(self):
        if self.max_skills < 10:
            raise ValueError("Max skills must be at least 10")


@dataclass
class SecurityConfig:
    """Security configuration"""
    encrypt_sensitive_data: bool = True
    log_sensitive_operations: bool = True
    enable_access_logging: bool = True
    max_failed_operations: int = 5
    operation_timeout_seconds: int = 300
    enable_data_validation: bool = True
    
    def __post_init__(self):
        if self.max_failed_operations < 1:
            raise ValueError("Max failed operations must be at least 1")


@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    log_file_path: str = "logs/cover_letter_gpt.log"
    max_log_file_size_mb: int = 100
    log_retention_days: int = 30
    enable_structured_logging: bool = True
    
    def __post_init__(self):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")


@dataclass
class ApplicationConfig:
    """Main application configuration container"""
    environment: Environment = Environment.DEVELOPMENT
    debug_mode: bool = False
    app_name: str = "Cover Letter GPT"
    app_version: str = "2.0.0"
    data_directory: str = "data"
    output_directory: str = "output"
    temp_directory: str = "temp"
    
    # Component configurations
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    relevance: RelevanceConfig = field(default_factory=RelevanceConfig)
    file_monitor: FileMonitorConfig = field(default_factory=FileMonitorConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with environment variable resolution"""
        return asdict(self)


class ConfigurationValidator:
    """Advanced configuration validation with business rules"""
    
    def __init__(self):
        self.validation_rules = {
            "openai.api_key": [
                lambda x: len(x) > 10 if x else True,  # Allow empty for demo mode
                lambda x: len(x) == 0 or len(x) > 10 if x is not None else True  # Valid API key length
            ],
            "performance.cache_size": [
                lambda x: 10 <= x <= 100000,
                lambda x: x % 10 == 0  # Must be multiple of 10
            ],
            "relevance.max_skills_returned": [
                lambda x: 1 <= x <= 50
            ],
            "memory.max_skills": [
                lambda x: 10 <= x <= 100000
            ]
        }
    
    def validate_config(self, config: ApplicationConfig) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        config_dict = asdict(config)
        
        # Flatten nested configuration for validation
        flat_config = self._flatten_dict(config_dict)
        
        for key, rules in self.validation_rules.items():
            if key in flat_config:
                value = flat_config[key]
                for rule in rules:
                    try:
                        if not rule(value):
                            errors.append(f"Validation failed for {key}: {value}")
                    except Exception as e:
                        errors.append(f"Validation error for {key}: {e}")
        
        # Cross-validation rules
        errors.extend(self._validate_cross_dependencies(config))
        
        return errors
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _validate_cross_dependencies(self, config: ApplicationConfig) -> List[str]:
        """Validate cross-component dependencies"""
        errors = []
        
        # Performance vs Memory consistency
        if config.performance.cache_size > config.memory.max_skills:
            errors.append("Performance cache size should not exceed max skills")
        
        # Environment-specific validations
        if config.environment == Environment.PRODUCTION:
            if config.debug_mode:
                errors.append("Debug mode should be disabled in production")
            if not config.openai.api_key:
                errors.append("OpenAI API key is required in production")
            if not config.security.encrypt_sensitive_data:
                errors.append("Data encryption should be enabled in production")
        
        # Resource constraints
        if config.performance.max_history > 50000 and config.memory.max_skills > 5000:
            errors.append("High memory usage configuration detected - consider reducing limits")
        
        return errors


class ConfigurationManager:
    """
    Advanced configuration management system with dynamic reloading,
    environment awareness, and intelligent defaults.
    
    Features:
    - Multi-source configuration (env vars, files, defaults)
    - Environment-specific configurations
    - Dynamic reloading without restart
    - Configuration validation with business rules
    - Secure handling of sensitive data
    - Configuration change notifications
    - Performance optimization settings
    """
    
    def __init__(self, config_file: Optional[str] = None, environment: Optional[Environment] = None):
        self.config_file = config_file or "config.yaml"
        self.environment = environment or self._detect_environment()
        self.validator = ConfigurationValidator()
        
        # Configuration storage
        self.config: ApplicationConfig = None
        self.config_values: Dict[str, ConfigValue] = {}
        self.change_listeners: List[callable] = []
        
        # Monitoring
        self.performance_monitor = get_global_performance_monitor()
        self.error_handler = get_global_error_handler()
        self.logger = logging.getLogger(__name__)
        
        # File watching for dynamic reloading
        self._file_watch_thread = None
        self._stop_watching = threading.Event()
        
        # Load initial configuration
        self.reload_configuration()
        
        # Start file watching if in development
        if self.environment == Environment.DEVELOPMENT:
            self.start_file_watching()
    
    def _detect_environment(self) -> Environment:
        """Detect environment from environment variables"""
        env_name = os.getenv("COVER_LETTER_ENV", "development").lower()
        
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "demo": Environment.DEMO
        }
        
        return env_mapping.get(env_name, Environment.DEVELOPMENT)
    
    def reload_configuration(self):
        """Reload configuration from all sources"""
        try:
            # Start with defaults
            config = ApplicationConfig()
            config.environment = self.environment
            
            # Load from file if exists
            if Path(self.config_file).exists():
                file_config = self._load_config_file()
                config = self._merge_configs(config, file_config)
            
            # Override with environment variables
            config = self._apply_environment_overrides(config)
            
            # Apply environment-specific settings
            config = self._apply_environment_specific_settings(config)
            
            # Validate configuration
            validation_errors = self.validator.validate_config(config)
            if validation_errors:
                self.logger.warning(f"Configuration validation errors: {validation_errors}")
                # Continue with warnings in development, halt in production
                if self.environment == Environment.PRODUCTION:
                    raise ValueError(f"Configuration validation failed: {validation_errors}")
            
            # Store configuration
            old_config = self.config
            self.config = config
            
            # Notify listeners of changes
            if old_config and old_config != config:
                self._notify_config_changes(old_config, config)
            
            self.logger.info(f"Configuration loaded successfully for {self.environment.value} environment")
            
        except Exception as e:
            error_context = ErrorContext("reload_configuration", "config_manager", {"config_file": self.config_file})
            self.error_handler.handle_error(e, error_context)
            
            # Use default configuration as fallback
            if self.config is None:
                self.config = ApplicationConfig()
                self.config.environment = self.environment
                self.logger.warning("Using default configuration due to loading error")
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    return yaml.safe_load(f) or {}
                elif self.config_file.endswith('.json'):
                    return json.load(f) or {}
                else:
                    raise ValueError(f"Unsupported config file format: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load config file {self.config_file}: {e}")
            return {}
    
    def _merge_configs(self, base_config: ApplicationConfig, file_config: Dict[str, Any]) -> ApplicationConfig:
        """Merge file configuration into base configuration"""
        
        # Convert file config to nested structure
        for section, values in file_config.items():
            if hasattr(base_config, section) and isinstance(values, dict):
                section_obj = getattr(base_config, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
                        
                        # Track configuration source
                        config_key = f"{section}.{key}"
                        self.config_values[config_key] = ConfigValue(
                            value=value,
                            source=ConfigSource.CONFIG_FILE,
                            last_updated=datetime.now(),
                            description=f"Loaded from {self.config_file}"
                        )
        
        return base_config
    
    def _apply_environment_overrides(self, config: ApplicationConfig) -> ApplicationConfig:
        """Apply environment variable overrides"""
        
        # Define environment variable mappings
        env_mappings = {
            "OPENAI_API_KEY": ("openai", "api_key", True),
            "OPENAI_MODEL": ("openai", "model", False),
            "CACHE_SIZE": ("performance", "cache_size", False),
            "DEBUG_MODE": ("debug_mode", None, False),
            "LOG_LEVEL": ("logging", "log_level", False)
        }
        
        for env_var, (section, key, is_sensitive) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Type conversion
                if key and hasattr(getattr(config, section, None), key):
                    attr_obj = getattr(config, section)
                    current_value = getattr(attr_obj, key)
                    
                    # Convert type based on current value type
                    if isinstance(current_value, bool):
                        env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif isinstance(current_value, int):
                        env_value = int(env_value)
                    elif isinstance(current_value, float):
                        env_value = float(env_value)
                    
                    setattr(attr_obj, key, env_value)
                    config_key = f"{section}.{key}"
                else:
                    # Direct attribute
                    current_value = getattr(config, section)
                    if isinstance(current_value, bool):
                        env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    setattr(config, section, env_value)
                    config_key = section
                
                # Track source
                self.config_values[config_key] = ConfigValue(
                    value=env_value,
                    source=ConfigSource.ENVIRONMENT_VARIABLE,
                    last_updated=datetime.now(),
                    description=f"Override from {env_var}",
                    is_sensitive=is_sensitive
                )
        
        return config
    
    def _apply_environment_specific_settings(self, config: ApplicationConfig) -> ApplicationConfig:
        """Apply environment-specific optimizations"""
        
        if self.environment == Environment.PRODUCTION:
            # Production optimizations
            config.debug_mode = False
            config.logging.log_level = "INFO"
            config.performance.enable_monitoring = True
            config.security.encrypt_sensitive_data = True
            config.security.enable_access_logging = True
            
        elif self.environment == Environment.DEVELOPMENT:
            # Development conveniences
            config.debug_mode = True
            config.logging.log_level = "DEBUG"
            config.performance.cache_size = 100  # Smaller cache for development
            config.file_monitor.check_interval_seconds = 30  # More frequent checks
            
        elif self.environment == Environment.TESTING:
            # Testing configurations
            config.debug_mode = True
            config.logging.log_level = "WARNING"
            config.performance.enable_monitoring = False
            config.memory.max_skills = 100  # Smaller limits for testing
            
        elif self.environment == Environment.DEMO:
            # Demo mode - no API key required
            config.openai.api_key = ""  # Allow empty API key
            config.performance.cache_size = 50
            config.memory.max_skills = 50
        
        return config
    
    def _notify_config_changes(self, old_config: ApplicationConfig, new_config: ApplicationConfig):
        """Notify listeners of configuration changes"""
        
        # Find changed values
        old_dict = asdict(old_config)
        new_dict = asdict(new_config)
        changes = self._find_config_differences(old_dict, new_dict)
        
        if changes:
            self.logger.info(f"Configuration changes detected: {list(changes.keys())}")
            
            # Notify all listeners
            for listener in self.change_listeners:
                try:
                    listener(changes)
                except Exception as e:
                    self.logger.error(f"Error notifying config change listener: {e}")
    
    def _find_config_differences(self, old_dict: Dict, new_dict: Dict, prefix: str = "") -> Dict[str, Any]:
        """Find differences between two configuration dictionaries"""
        differences = {}
        
        all_keys = set(old_dict.keys()) | set(new_dict.keys())
        
        for key in all_keys:
            full_key = f"{prefix}.{key}" if prefix else key
            
            if key not in old_dict:
                differences[full_key] = {"type": "added", "new_value": new_dict[key]}
            elif key not in new_dict:
                differences[full_key] = {"type": "removed", "old_value": old_dict[key]}
            elif isinstance(old_dict[key], dict) and isinstance(new_dict[key], dict):
                nested_diffs = self._find_config_differences(old_dict[key], new_dict[key], full_key)
                differences.update(nested_diffs)
            elif old_dict[key] != new_dict[key]:
                differences[full_key] = {
                    "type": "changed",
                    "old_value": old_dict[key],
                    "new_value": new_dict[key]
                }
        
        return differences
    
    def start_file_watching(self):
        """Start watching configuration file for changes"""
        if self._file_watch_thread and self._file_watch_thread.is_alive():
            return
        
        def watch_file():
            last_modified = None
            
            while not self._stop_watching.is_set():
                try:
                    if Path(self.config_file).exists():
                        current_modified = Path(self.config_file).stat().st_mtime
                        
                        if last_modified and current_modified > last_modified:
                            self.logger.info("Configuration file changed, reloading...")
                            self.reload_configuration()
                        
                        last_modified = current_modified
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error watching config file: {e}")
                    time.sleep(30)  # Wait longer on error
        
        self._file_watch_thread = threading.Thread(target=watch_file, daemon=True)
        self._file_watch_thread.start()
        self.logger.info("Started configuration file watching")
    
    def stop_file_watching(self):
        """Stop watching configuration file"""
        if self._file_watch_thread and self._file_watch_thread.is_alive():
            self._stop_watching.set()
            self._file_watch_thread.join(timeout=10)
            self.logger.info("Stopped configuration file watching")
    
    def add_change_listener(self, listener: callable):
        """Add a listener for configuration changes"""
        self.change_listeners.append(listener)
    
    def remove_change_listener(self, listener: callable):
        """Remove a configuration change listener"""
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
    
    def get_config(self) -> ApplicationConfig:
        """Get current configuration"""
        return self.config
    
    def get_config_value(self, key: str) -> Optional[ConfigValue]:
        """Get detailed information about a configuration value"""
        return self.config_values.get(key)
    
    def set_config_value(self, section: str, key: str, value: Any):
        """Dynamically set a configuration value"""
        if hasattr(self.config, section):
            section_obj = getattr(self.config, section)
            if hasattr(section_obj, key):
                old_value = getattr(section_obj, key)
                setattr(section_obj, key, value)
                
                # Track the change
                config_key = f"{section}.{key}"
                self.config_values[config_key] = ConfigValue(
                    value=value,
                    source=ConfigSource.DEFAULT,  # Runtime change
                    last_updated=datetime.now(),
                    description="Runtime modification"
                )
                
                self.logger.info(f"Configuration updated: {config_key} = {value} (was {old_value})")
                
                # Validate new configuration
                validation_errors = self.validator.validate_config(self.config)
                if validation_errors:
                    # Rollback on validation failure
                    setattr(section_obj, key, old_value)
                    raise ValueError(f"Configuration validation failed: {validation_errors}")
    
    def export_config(self, filepath: str, include_sensitive: bool = False):
        """Export current configuration to file"""
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "configuration": asdict(self.config),
            "config_sources": {
                key: value.to_dict() 
                for key, value in self.config_values.items()
                if include_sensitive or not value.is_sensitive
            }
        }
        
        # Remove sensitive data if not included
        if not include_sensitive:
            if "openai" in export_data["configuration"]:
                export_data["configuration"]["openai"]["api_key"] = "***HIDDEN***"
        
        with open(filepath, 'w') as f:
            if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                yaml.dump(export_data, f, default_flow_style=False, indent=2)
            else:
                json.dump(export_data, f, indent=2, default=str)
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        
        return {
            "environment": self.environment.value,
            "config_file": self.config_file,
            "file_exists": Path(self.config_file).exists(),
            "total_config_values": len(self.config_values),
            "sources_breakdown": {
                source.value: sum(1 for cv in self.config_values.values() if cv.source == source)
                for source in ConfigSource
            },
            "last_reload": max(
                (cv.last_updated for cv in self.config_values.values()),
                default=datetime.now()
            ).isoformat(),
            "validation_status": "valid" if not self.validator.validate_config(self.config) else "warnings",
            "file_watching_active": self._file_watch_thread and self._file_watch_thread.is_alive()
        }
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_file_watching()


# Global configuration manager instance
_global_config_manager = None

def get_global_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
    return _global_config_manager


def initialize_configuration(config_file: Optional[str] = None, 
                           environment: Optional[Environment] = None) -> ConfigurationManager:
    """Initialize the global configuration manager"""
    global _global_config_manager
    _global_config_manager = ConfigurationManager(config_file, environment)
    return _global_config_manager