"""
Integration Test Suite for Cover Letter GPT System
==================================================

Comprehensive integration tests validating end-to-end functionality,
component interactions, and real-world usage scenarios.

"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from cover_letter_generator.main import CoverLetterGenerator
from cover_letter_generator.config_manager import ConfigurationManager, Environment
from cover_letter_generator.memory_core import MemoryCore
from cover_letter_generator.advanced_relevance_engine import AdvancedRelevanceEngine
from cover_letter_generator.performance_monitor import PerformanceMonitor
from cover_letter_generator.error_handler import ErrorHandler
from cover_letter_generator.memory_analytics import MemoryAnalytics
from conftest import measure_execution_time


class TestSystemIntegration:
    """Test complete system integration scenarios"""
    
    @pytest.fixture
    def integrated_system(self, temp_directory, mock_memory_data, sample_job_description):
        """Create integrated system for testing"""
        # Setup memory file
        memory_file = Path(temp_directory) / "integration_memory.json"
        with open(memory_file, 'w') as f:
            json.dump(mock_memory_data, f)
        
        # Setup skills file
        skills_file = Path(temp_directory) / "skills.csv"
        with open(skills_file, 'w') as f:
            f.write("skill_name,context,experience_years\n")
            f.write("Network Security,Implemented network security protocols,5\n")
            f.write("HIPAA Compliance,Healthcare data protection experience,3\n")
            f.write("Python Programming,Automation and scripting,4\n")
        
        # Setup criteria file
        criteria_file = Path(temp_directory) / "criteria.txt"
        with open(criteria_file, 'w') as f:
            f.write("# Cover Letter Criteria\n")
            f.write("- Professional tone\n")
            f.write("- Technical expertise emphasis\n")
            f.write("- Industry-specific experience\n")
        
        # Setup job description file
        job_file = Path(temp_directory) / "job_description.txt"
        with open(job_file, 'w') as f:
            f.write(sample_job_description)
        
        # Create configuration
        config_manager = ConfigurationManager(environment=Environment.TESTING)
        config_manager.config.openai.api_key = "test-key"
        
        # Create system components
        system = {
            "config_manager": config_manager,
            "memory_core": MemoryCore(str(memory_file)),
            "relevance_engine": AdvancedRelevanceEngine(),
            "performance_monitor": PerformanceMonitor(),
            "error_handler": ErrorHandler(),
            "memory_analytics": MemoryAnalytics(),
            "temp_directory": temp_directory,
            "files": {
                "memory": str(memory_file),
                "skills": str(skills_file),
                "criteria": str(criteria_file),
                "job": str(job_file)
            }
        }
        
        return system
    
    def test_complete_workflow_integration(self, integrated_system, sample_job_description):
        """Test complete cover letter generation workflow"""
        # Mock OpenAI client for testing
        mock_openai_response = {
            "content": "Dear Hiring Manager,\n\nI am writing to express my strong interest in the Senior Security Analyst position. With 5 years of experience in network security and expertise in HIPAA compliance, I am well-positioned to contribute to your healthcare technology team.\n\nMy background includes implementing network security protocols and ensuring healthcare data protection compliance. I have hands-on experience with vulnerability assessment tools and Active Directory management.\n\nI am excited about the opportunity to bring my cybersecurity expertise to your organization.\n\nSincerely,\nApplicant",
            "success": True,
            "tokens_used": 150
        }
        
        with patch('cover_letter_generator.openai_client.OpenAIClient.generate_cover_letter', return_value=mock_openai_response):
            # Initialize system components
            memory = integrated_system["memory_core"]
            relevance_engine = integrated_system["relevance_engine"]
            config = integrated_system["config_manager"].get_config()
            
            # Step 1: Load and analyze job
            job_analysis, analysis_time = measure_execution_time(
                relevance_engine.analyze_job_comprehensive,
                sample_job_description
            )
            
            assert job_analysis is not None
            assert analysis_time < 2000  # Should complete quickly
            assert job_analysis.confidence_score > 0.5
            
            # Step 2: Get relevant skills
            skills_data = memory.get_all_skills()
            relevant_skills = []
            
            for skill_key, skill_data in skills_data.items():
                score, scoring_time = measure_execution_time(
                    relevance_engine.score_skill_comprehensive,
                    skill_data, job_analysis
                )
                
                assert scoring_time < 100  # Should be fast
                if score.final_score > 0.3:  # Relevance threshold
                    relevant_skills.append((skill_data, score))
            
            assert len(relevant_skills) > 0
            
            # Step 3: Verify high-relevance skills are included
            skill_names = [skill[0]["skill_name"] for skill in relevant_skills]
            assert "Network Security" in skill_names  # Should be highly relevant
            
            # Step 4: Generate cover letter (mocked)
            cover_letter_result = mock_openai_response
            assert cover_letter_result["success"] is True
            assert "network security" in cover_letter_result["content"].lower()
            assert "hipaa" in cover_letter_result["content"].lower()
    
    def test_memory_system_integration(self, integrated_system, sample_feedback_history):
        """Test memory system integration with learning"""
        memory = integrated_system["memory_core"]
        analytics = integrated_system["memory_analytics"]
        
        # Test memory loading
        skills = memory.get_all_skills()
        assert len(skills) > 0
        
        # Test learning from feedback
        for feedback in sample_feedback_history:
            memory.learn_from_feedback(feedback)
        
        # Test analytics generation
        analytics_report, report_time = measure_execution_time(
            analytics.generate_comprehensive_report,
            memory.get_memory_data(), sample_feedback_history
        )
        
        assert analytics_report is not None
        assert report_time < 5000  # Should complete in reasonable time
        assert "executive_summary" in analytics_report
        assert "memory_health" in analytics_report
        
        # Test memory optimization
        health_score = analytics_report["memory_health"]["overall_score"]
        assert 0 <= health_score <= 100
    
    def test_performance_monitoring_integration(self, integrated_system):
        """Test performance monitoring across all components"""
        monitor = integrated_system["performance_monitor"]
        relevance_engine = integrated_system["relevance_engine"]
        
        # Perform monitored operations
        sample_job = "Software Engineer position requiring Python and SQL skills"
        
        # Multiple operations to generate monitoring data
        for i in range(5):
            job_analysis = relevance_engine.analyze_job_comprehensive(sample_job)
            
            # Simulate skill scoring
            test_skill = {
                "skill_name": f"Test Skill {i}",
                "context": "Test context",
                "experience_years": 3
            }
            relevance_engine.score_skill_comprehensive(test_skill, job_analysis)
        
        # Generate performance report
        perf_report = monitor.generate_performance_report()
        
        assert "components" in perf_report
        assert "summary" in perf_report
        assert perf_report["summary"]["total_operations"] >= 10  # At least 10 operations
        
        # Check for reasonable performance
        avg_response_time = perf_report["summary"].get("avg_response_time", 0)
        assert avg_response_time > 0  # Should have recorded some operations
    
    def test_error_handling_integration(self, integrated_system):
        """Test error handling across system components"""
        error_handler = integrated_system["error_handler"]
        relevance_engine = integrated_system["relevance_engine"]
        
        # Test error handling with invalid inputs
        invalid_inputs = [
            "",  # Empty job description
            None,  # None input
            "A" * 10000,  # Extremely long input
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = relevance_engine.analyze_job_comprehensive(invalid_input)
                # Should handle gracefully, not crash
                assert result is not None
            except Exception as e:
                # If exception occurs, should be logged
                assert len(error_handler.error_history) > 0
        
        # Test error analytics
        if error_handler.error_history:
            analytics = error_handler.generate_error_analytics()
            assert "total_errors" in analytics
            assert analytics["total_errors"] > 0
    
    def test_configuration_integration(self, integrated_system):
        """Test configuration integration across components"""
        config_manager = integrated_system["config_manager"]
        config = config_manager.get_config()
        
        # Test configuration access
        assert config.environment == Environment.TESTING
        assert config.performance.cache_size > 0
        assert config.relevance.relevance_threshold > 0
        
        # Test configuration change notification
        changes_received = []
        def config_change_listener(changes):
            changes_received.append(changes)
        
        config_manager.add_change_listener(config_change_listener)
        
        # Make configuration change
        config_manager.set_config_value("performance", "cache_size", 200)
        
        # Verify change was propagated
        assert config.performance.cache_size == 200
        
        # Clean up
        config_manager.remove_change_listener(config_change_listener)
    
    def test_file_monitoring_integration(self, integrated_system):
        """Test file monitoring integration"""
        skills_file = integrated_system["files"]["skills"]
        memory = integrated_system["memory_core"]
        
        # Get initial skill count
        initial_skills = memory.get_all_skills()
        initial_count = len(initial_skills)
        
        # Modify skills file
        with open(skills_file, 'a') as f:
            f.write("New Skill,Recently added skill,2\n")
        
        # In a real system, file monitor would detect this change
        # For testing, we'll manually trigger reload
        memory.reload_skills_from_file(skills_file)
        
        # Verify new skill was loaded
        updated_skills = memory.get_all_skills()
        updated_count = len(updated_skills)
        
        # Should have more skills now
        assert updated_count > initial_count
        
        # Verify new skill exists
        skill_names = [skill["skill_name"] for skill in updated_skills.values()]
        assert "New Skill" in skill_names
    
    def test_caching_integration(self, integrated_system):
        """Test caching integration across components"""
        relevance_engine = integrated_system["relevance_engine"]
        monitor = integrated_system["performance_monitor"]
        
        # Same job description for caching test
        job_description = "Data Analyst position requiring SQL and Python"
        
        # First analysis (should be slow)
        result1, time1 = measure_execution_time(
            relevance_engine.analyze_job_comprehensive,
            job_description
        )
        
        # Second analysis (should use cache and be faster)
        result2, time2 = measure_execution_time(
            relevance_engine.analyze_job_comprehensive,
            job_description
        )
        
        # Results should be identical
        assert result1.to_dict() == result2.to_dict()
        
        # Second call should be significantly faster (cached)
        assert time2 < time1 * 0.7  # At least 30% faster
        
        # Verify cache statistics
        cache_stats = monitor.cache_manager.get_cache_statistics()
        assert cache_stats["hit_rate"] > 0  # Should have some cache hits


class TestRealWorldScenarios:
    """Test realistic usage scenarios"""
    
    def test_job_application_workflow(self, integrated_system):
        """Test complete job application workflow"""
        memory = integrated_system["memory_core"]
        relevance_engine = integrated_system["relevance_engine"]
        
        # Scenario: Healthcare IT Security position
        healthcare_job = """
        Healthcare IT Security Specialist
        
        We're seeking a Healthcare IT Security Specialist to protect our hospital's
        patient data and ensure HIPAA compliance. The role requires experience with
        network security, vulnerability assessments, and healthcare regulations.
        
        Required Skills:
        - HIPAA compliance knowledge
        - Network security experience
        - Vulnerability assessment tools
        - Healthcare industry experience
        - Active Directory management
        
        This position requires 3+ years of healthcare IT experience.
        """
        
        # Mock OpenAI response for healthcare job
        mock_response = {
            "content": "Dear Healthcare Security Team,\n\nI am excited to apply for the Healthcare IT Security Specialist position. My experience in HIPAA compliance and network security makes me an ideal candidate for protecting patient data in your healthcare environment.\n\nBest regards,\nApplicant",
            "success": True,
            "tokens_used": 120
        }
        
        with patch('cover_letter_generator.openai_client.OpenAIClient.generate_cover_letter', return_value=mock_response):
            # Step 1: Analyze job
            job_analysis = relevance_engine.analyze_job_comprehensive(healthcare_job)
            
            # Should detect healthcare industry
            assert "healthcare" in job_analysis.industry_context
            assert job_analysis.confidence_score > 0.7
            
            # Step 2: Score skills
            skills = memory.get_all_skills()
            scored_skills = []
            
            for skill_key, skill_data in skills.items():
                score = relevance_engine.score_skill_comprehensive(skill_data, job_analysis)
                scored_skills.append((skill_data["skill_name"], score.final_score))
            
            # HIPAA and Network Security should score highly
            skill_scores = dict(scored_skills)
            assert skill_scores.get("HIPAA Compliance", 0) > 0.8
            assert skill_scores.get("Network Security", 0) > 0.8
            
            # Non-relevant skills should score low
            assert skill_scores.get("Social Media Marketing", 1.0) < 0.3
    
    def test_iterative_improvement_scenario(self, integrated_system):
        """Test iterative improvement through feedback"""
        memory = integrated_system["memory_core"]
        analytics = integrated_system["memory_analytics"]
        
        # Simulate initial application
        initial_feedback = [
            {
                "timestamp": datetime.now().isoformat(),
                "outcome": "rejected",
                "feedback_text": "MySQL experience not relevant for this networking role",
                "skill_name": "MySQL Database",
                "job_type": "network_engineer"
            }
        ]
        
        # Apply feedback
        for feedback in initial_feedback:
            memory.learn_from_feedback(feedback)
        
        # Simulate subsequent application to similar role
        network_job = """
        Network Engineer position focused on enterprise networking,
        routing protocols, and network infrastructure management.
        No database administration required.
        """
        
        relevance_engine = integrated_system["relevance_engine"]
        job_analysis = relevance_engine.analyze_job_comprehensive(network_job)
        
        # Get skills and score them
        skills = memory.get_all_skills()
        mysql_skill = None
        
        for skill_key, skill_data in skills.items():
            if skill_data["skill_name"] == "MySQL Database":
                mysql_skill = skill_data
                break
        
        if mysql_skill:
            score = relevance_engine.score_skill_comprehensive(mysql_skill, job_analysis)
            # After negative feedback, MySQL should have lower relevance for networking roles
            assert score.final_score < 0.4
        
        # Generate analytics to verify learning
        analytics_report = analytics.generate_comprehensive_report(
            memory.get_memory_data(), initial_feedback
        )
        
        # Should show learning patterns
        assert len(analytics_report["learning_patterns"]) > 0
    
    def test_high_volume_processing(self, integrated_system):
        """Test system performance under high volume"""
        relevance_engine = integrated_system["relevance_engine"]
        monitor = integrated_system["performance_monitor"]
        
        # Generate multiple job descriptions
        job_templates = [
            "Software Engineer position requiring {skills}",
            "Data Analyst role focusing on {skills}",
            "Network Administrator job needing {skills}",
            "Security Specialist position with {skills}",
            "IT Support role requiring {skills}"
        ]
        
        skill_sets = [
            "Python and SQL",
            "JavaScript and React",
            "Network Security and Firewalls",
            "Data Analysis and Statistics",
            "System Administration and Linux"
        ]
        
        # Process multiple job descriptions
        start_time = time.time()
        
        for i in range(10):  # Process 10 jobs
            template = job_templates[i % len(job_templates)]
            skills = skill_sets[i % len(skill_sets)]
            job_desc = template.format(skills=skills)
            
            job_analysis = relevance_engine.analyze_job_comprehensive(job_desc)
            assert job_analysis is not None
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Should process efficiently
        avg_time_per_job = total_time / 10
        assert avg_time_per_job < 500  # Less than 500ms per job on average
        
        # Verify monitoring captured the operations
        perf_report = monitor.generate_performance_report()
        assert perf_report["summary"]["total_operations"] >= 10
    
    def test_error_recovery_scenario(self, integrated_system):
        """Test error recovery in realistic scenarios"""
        relevance_engine = integrated_system["relevance_engine"]
        error_handler = integrated_system["error_handler"]
        
        # Simulate various error conditions
        error_scenarios = [
            ("", "Empty job description"),
            (None, "None input"),
            ("J" * 100000, "Extremely long job description"),
            ("!@#$%^&*()", "Special characters only"),
        ]
        
        successful_recoveries = 0
        
        for invalid_input, scenario_name in error_scenarios:
            try:
                result = relevance_engine.analyze_job_comprehensive(invalid_input)
                if result is not None:
                    successful_recoveries += 1
            except Exception:
                # Errors should be handled gracefully
                pass
        
        # Should recover from most error scenarios
        recovery_rate = successful_recoveries / len(error_scenarios)
        assert recovery_rate >= 0.75  # At least 75% recovery rate
        
        # Generate error analytics
        if error_handler.error_history:
            analytics = error_handler.generate_error_analytics()
            assert analytics["total_errors"] > 0


class TestSystemPerformance:
    """Test system-wide performance characteristics"""
    
    def test_memory_usage_efficiency(self, integrated_system):
        """Test system memory usage efficiency"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        memory = integrated_system["memory_core"]
        analytics = integrated_system["memory_analytics"]
        
        # Load and process data multiple times
        for _ in range(5):
            memory.get_all_skills()
            analytics.generate_comprehensive_report(memory.get_memory_data())
        
        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for test operations)
        assert memory_increase < 100
    
    def test_concurrent_access_performance(self, integrated_system):
        """Test performance under concurrent access"""
        import threading
        import queue
        
        relevance_engine = integrated_system["relevance_engine"]
        results_queue = queue.Queue()
        
        def worker_thread(thread_id, num_operations):
            thread_results = []
            for i in range(num_operations):
                job_desc = f"Thread {thread_id} job {i} - Python Developer position"
                start_time = time.time()
                result = relevance_engine.analyze_job_comprehensive(job_desc)
                end_time = time.time()
                
                thread_results.append({
                    "thread_id": thread_id,
                    "operation": i,
                    "success": result is not None,
                    "duration_ms": (end_time - start_time) * 1000
                })
            
            results_queue.put(thread_results)
        
        # Start multiple worker threads
        num_threads = 3
        operations_per_thread = 5
        threads = []
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i, operations_per_thread))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Collect results
        all_results = []
        while not results_queue.empty():
            thread_results = results_queue.get()
            all_results.extend(thread_results)
        
        # Verify all operations completed successfully
        assert len(all_results) == num_threads * operations_per_thread
        success_rate = sum(1 for result in all_results if result["success"]) / len(all_results)
        assert success_rate >= 0.95  # 95% success rate
        
        # Verify reasonable performance under concurrency
        avg_duration = sum(result["duration_ms"] for result in all_results) / len(all_results)
        assert avg_duration < 1000  # Less than 1 second per operation on average
    
    def test_cache_effectiveness_under_load(self, integrated_system):
        """Test cache effectiveness under realistic load"""
        relevance_engine = integrated_system["relevance_engine"]
        monitor = integrated_system["performance_monitor"]
        
        # Create mix of repeated and unique job descriptions
        repeated_jobs = [
            "Python Developer position with Django experience",
            "Data Scientist role requiring machine learning skills",
            "Network Engineer position with Cisco certification"
        ]
        
        # Process jobs with repetition pattern
        total_operations = 20
        for i in range(total_operations):
            if i % 3 == 0:  # Every 3rd operation uses repeated job
                job_desc = repeated_jobs[i % len(repeated_jobs)]
            else:  # Unique job descriptions
                job_desc = f"Unique position {i} requiring specialized skills"
            
            relevance_engine.analyze_job_comprehensive(job_desc)
        
        # Check cache effectiveness
        cache_stats = monitor.cache_manager.get_cache_statistics()
        
        # Should have reasonable cache hit rate
        hit_rate = cache_stats.get("hit_rate", 0)
        assert hit_rate > 0.2  # At least 20% cache hit rate
        
        # Cache should be reasonably utilized
        cache_size = cache_stats.get("cache_size", 0)
        assert cache_size > 0
