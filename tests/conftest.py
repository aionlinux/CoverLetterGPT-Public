"""
PyTest Configuration and Fixtures
=================================

Shared test fixtures and configuration for the Cover Letter GPT test suite.
Provides comprehensive test utilities and mock data for all test scenarios.

Author: Claude AI (Anthropic
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cover_letter_generator.config_manager import ApplicationConfig, Environment
from cover_letter_generator.memory_core import MemoryCore
from cover_letter_generator.error_handler import ErrorHandler
from cover_letter_generator.performance_monitor import PerformanceMonitor


@pytest.fixture(scope="session")
def temp_directory():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    Senior Security Analyst - Healthcare Technology
    
    We are seeking an experienced Security Analyst to join our healthcare technology team.
    The ideal candidate will have strong experience in network security, HIPAA compliance,
    and vulnerability assessment. This role requires expertise in security tools like
    Wireshark, Nessus, and SIEM platforms.
    
    Required Skills:
    - Network Security fundamentals
    - HIPAA compliance knowledge
    - Vulnerability assessment tools
    - Active Directory management
    - Incident response procedures
    
    Preferred Skills:
    - CISSP or equivalent certification
    - Experience with cloud security (AWS/Azure)
    - Python scripting for automation
    - Risk management frameworks
    
    This is a senior-level position requiring 5+ years of experience in cybersecurity.
    """


@pytest.fixture
def sample_skills_data():
    """Sample skills data for testing"""
    return {
        "skill_001": {
            "skill_name": "Network Security",
            "context": "Implemented network security protocols and firewalls for enterprise environments",
            "experience_years": 5,
            "last_updated": datetime.now().isoformat(),
            "confidence_score": 0.9,
            "usage_count": 15
        },
        "skill_002": {
            "skill_name": "HIPAA Compliance",
            "context": "Ensured healthcare data protection and regulatory compliance",
            "experience_years": 3,
            "last_updated": datetime.now().isoformat(),
            "confidence_score": 0.8,
            "usage_count": 8
        },
        "skill_003": {
            "skill_name": "MySQL Database",
            "context": "Database administration and query optimization",
            "experience_years": 4,
            "last_updated": datetime.now().isoformat(),
            "confidence_score": 0.7,
            "usage_count": 12
        },
        "skill_004": {
            "skill_name": "Social Media Marketing",
            "context": "Managed social media campaigns and content strategy",
            "experience_years": 2,
            "last_updated": datetime.now().isoformat(),
            "confidence_score": 0.6,
            "usage_count": 5
        }
    }


@pytest.fixture
def sample_feedback_history():
    """Sample feedback history for testing"""
    return [
        {
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "outcome": "accepted",
            "feedback_text": "Great match for the security analyst role",
            "skill_name": "Network Security",
            "job_type": "security_analyst"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
            "outcome": "rejected",
            "feedback_text": "MySQL not relevant for this networking position",
            "skill_name": "MySQL Database",
            "job_type": "network_engineer"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "outcome": "improved",
            "feedback_text": "Good but could emphasize compliance more",
            "skill_name": "HIPAA Compliance",
            "job_type": "healthcare_analyst"
        }
    ]


@pytest.fixture
def mock_memory_data(sample_skills_data, sample_feedback_history):
    """Mock memory data structure"""
    return {
        "user_profile": {
            "skills": sample_skills_data,
            "preferences": {
                "industry_focus": "healthcare_technology",
                "role_preferences": ["security_analyst", "network_engineer"],
                "location_preferences": ["remote", "hybrid"]
            },
            "interaction_history": sample_feedback_history
        },
        "metadata": {
            "total_interactions": len(sample_feedback_history),
            "last_updated": datetime.now().isoformat(),
            "version": "2.0.0"
        }
    }


@pytest.fixture
def mock_config():
    """Mock application configuration"""
    config = ApplicationConfig()
    config.environment = Environment.TESTING
    config.openai.api_key = "test-key"
    config.performance.cache_size = 100
    config.memory.max_skills = 100
    return config


@pytest.fixture
def mock_memory_core(temp_directory, mock_memory_data):
    """Mock memory core with test data"""
    memory_file = Path(temp_directory) / "test_memory.json"
    
    # Write test data to file
    with open(memory_file, 'w') as f:
        json.dump(mock_memory_data, f)
    
    memory = MemoryCore(str(memory_file))
    return memory


@pytest.fixture
def mock_error_handler():
    """Mock error handler for testing"""
    return ErrorHandler()


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitor for testing"""
    return PerformanceMonitor()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = Mock()
    mock_client.generate_cover_letter.return_value = {
        "content": "This is a test cover letter generated for testing purposes.",
        "success": True,
        "tokens_used": 150
    }
    mock_client.analyze_feedback.return_value = {
        "insights": ["Skill relevance was appropriate", "Good industry match"],
        "confidence": 0.8
    }
    return mock_client


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for file monitoring tests"""
    return """skill_name,context,experience_years
Network Security,Implemented firewalls and intrusion detection systems,5
Python Programming,Developed automation scripts and data analysis tools,4
Project Management,Led cross-functional teams and managed project timelines,3
"""


@pytest.fixture
def sample_criteria_content():
    """Sample criteria content for file monitoring tests"""
    return """
# Cover Letter Generation Criteria

## Tone and Style
- Professional yet personable
- Confident but not arrogant
- Industry-specific terminology

## Key Points to Emphasize
- Technical expertise relevant to the role
- Problem-solving abilities
- Team collaboration skills
- Continuous learning mindset

## Customization Rules
- Match 70%+ of required skills
- Highlight industry-specific experience
- Adapt tone to company culture
"""


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("COVER_LETTER_ENV", "testing")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")


@pytest.fixture
def performance_benchmarks():
    """Performance benchmark targets for testing"""
    return {
        "job_analysis_time_ms": 2000,
        "skill_scoring_time_ms": 50,
        "memory_operations_time_ms": 10,
        "cache_hit_rate_min": 0.80,
        "error_recovery_rate_min": 0.90
    }


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing"""
    return {
        "skill_evolution": {
            "network_security": {
                "average_performance": 0.85,
                "improvement_trend": 0.1,
                "usage_frequency": 15
            },
            "hipaa_compliance": {
                "average_performance": 0.78,
                "improvement_trend": 0.05,
                "usage_frequency": 8
            }
        },
        "memory_health": {
            "overall_score": 75.0,
            "skill_diversity": 0.8,
            "learning_velocity": 0.6,
            "data_quality": 0.9
        }
    }


class MockFileWatcher:
    """Mock file watcher for testing file monitoring"""
    
    def __init__(self):
        self.is_monitoring = False
        self.changes_detected = []
    
    def start_monitoring(self):
        self.is_monitoring = True
    
    def stop_monitoring(self):
        self.is_monitoring = False
    
    def simulate_file_change(self, filepath: str, change_type: str):
        self.changes_detected.append({
            "filepath": filepath,
            "change_type": change_type,
            "timestamp": datetime.now().isoformat()
        })


@pytest.fixture
def mock_file_watcher():
    """Mock file watcher fixture"""
    return MockFileWatcher()


# Test data validation helpers
def validate_job_analysis_result(result: Dict[str, Any]) -> bool:
    """Validate job analysis result structure"""
    required_fields = [
        "job_role_type", "primary_focus", "confidence_score",
        "required_skills", "tech_domains", "industry_context"
    ]
    return all(field in result for field in required_fields)


def validate_skill_relevance_score(score: Dict[str, Any]) -> bool:
    """Validate skill relevance score structure"""
    required_fields = [
        "skill_name", "final_score", "explanation", "confidence"
    ]
    return all(field in score for field in required_fields)


# Performance testing utilities
def measure_execution_time(func, *args, **kwargs):
    """Measure function execution time"""
    import time
    start_time = time.time()
    result = func(*args, **kwargs)
    execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    return result, execution_time
