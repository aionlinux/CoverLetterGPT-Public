"""
Test Suite for Memory Analytics System
======================================

Comprehensive tests for the advanced memory analytics system,
validating learning pattern detection, skill evolution tracking, and optimization recommendations.

Author: Claude AI (Anthropic)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from cover_letter_generator.memory_analytics import (
    MemoryAnalytics, SkillEvolution, LearningPattern, MemoryHealth,
    SkillClusterAnalyzer, TrendAnalyzer
)
from conftest import measure_execution_time


class TestMemoryAnalytics:
    """Test the memory analytics main functionality"""
    
    @pytest.fixture
    def memory_analytics(self):
        """Create memory analytics instance for testing"""
        return MemoryAnalytics()
    
    def test_analytics_initialization(self, memory_analytics):
        """Test proper initialization of memory analytics"""
        assert memory_analytics is not None
        assert hasattr(memory_analytics, 'skill_cluster_analyzer')
        assert hasattr(memory_analytics, 'trend_analyzer')
        assert hasattr(memory_analytics, 'performance_monitor')
        assert hasattr(memory_analytics, 'error_handler')
    
    def test_comprehensive_report_generation(self, memory_analytics, mock_memory_data, sample_feedback_history):
        """Test comprehensive analytics report generation"""
        result, execution_time = measure_execution_time(
            memory_analytics.generate_comprehensive_report,
            mock_memory_data, sample_feedback_history
        )
        
        # Validate report structure
        assert isinstance(result, dict)
        required_sections = [
            "report_timestamp", "executive_summary", "memory_health",
            "skill_evolution", "learning_patterns", "skill_clusters",
            "performance_trends", "optimization_recommendations", "metadata"
        ]
        for section in required_sections:
            assert section in result
        
        # Validate executive summary
        summary = result["executive_summary"]
        assert "overall_assessment" in summary
        assert "health_score" in summary
        assert "key_metrics" in summary
        assert "highlights" in summary
        
        # Validate performance
        assert execution_time < 5000  # Should complete in under 5 seconds
    
    def test_skill_evolution_analysis(self, memory_analytics, mock_memory_data):
        """Test skill evolution tracking"""
        evolutions = memory_analytics.analyze_skill_evolution(mock_memory_data)
        
        assert isinstance(evolutions, dict)
        assert len(evolutions) > 0
        
        # Test each evolution object
        for skill_key, evolution in evolutions.items():
            assert isinstance(evolution, SkillEvolution)
            assert evolution.skill_name is not None
            assert evolution.usage_frequency >= 0
            assert 0.0 <= evolution.average_performance <= 1.0
            assert 0.0 <= evolution.performance_stability <= 1.0
            assert evolution.days_active >= 0
    
    def test_learning_pattern_identification(self, memory_analytics, mock_memory_data, sample_feedback_history):
        """Test learning pattern identification"""
        patterns = memory_analytics.identify_learning_patterns(mock_memory_data, sample_feedback_history)
        
        assert isinstance(patterns, list)
        
        for pattern in patterns:
            assert isinstance(pattern, LearningPattern)
            assert pattern.pattern_type in ["improvement", "plateau", "decline", "cyclical"]
            assert 0.0 <= pattern.confidence <= 1.0
            assert isinstance(pattern.affected_skills, list)
            assert isinstance(pattern.trigger_events, list)
    
    def test_memory_health_assessment(self, memory_analytics, mock_memory_data, sample_feedback_history):
        """Test memory health assessment"""
        health = memory_analytics.assess_memory_health(mock_memory_data, sample_feedback_history)
        
        assert isinstance(health, MemoryHealth)
        assert 0.0 <= health.overall_score <= 100.0
        assert 0.0 <= health.skill_diversity <= 1.0
        assert 0.0 <= health.learning_velocity <= 1.0
        assert 0.0 <= health.memory_efficiency <= 1.0
        assert 0.0 <= health.data_quality <= 1.0
        assert isinstance(health.recommendations, list)
        assert len(health.recommendations) > 0
    
    def test_optimization_recommendations(self, memory_analytics, mock_memory_data, sample_feedback_history):
        """Test optimization recommendation generation"""
        skill_evolution = memory_analytics.analyze_skill_evolution(mock_memory_data)
        recommendations = memory_analytics.generate_optimization_recommendations(
            mock_memory_data, sample_feedback_history, skill_evolution
        )
        
        assert isinstance(recommendations, list)
        
        for rec in recommendations:
            assert isinstance(rec, dict)
            required_fields = ["category", "priority", "title", "description", "expected_impact"]
            for field in required_fields:
                assert field in rec
            assert rec["priority"] in ["high", "medium", "low"]
    
    def test_export_analytics_report(self, memory_analytics, mock_memory_data, temp_directory):
        """Test analytics report export functionality"""
        export_path = f"{temp_directory}/analytics_report.json"
        
        # Export report
        memory_analytics.export_analytics_report(export_path, mock_memory_data)
        
        # Verify file exists and contains valid JSON
        import os
        assert os.path.exists(export_path)
        
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        # Validate exported data structure
        assert isinstance(exported_data, dict)
        assert "report_timestamp" in exported_data


class TestSkillClusterAnalyzer:
    """Test the skill clustering analysis component"""
    
    @pytest.fixture
    def cluster_analyzer(self):
        return SkillClusterAnalyzer()
    
    def test_skill_cluster_analysis(self, cluster_analyzer, sample_skills_data):
        """Test skill clustering functionality"""
        clusters = cluster_analyzer.analyze_skill_clusters(sample_skills_data)
        
        assert isinstance(clusters, dict)
        assert "total_clusters" in clusters
        assert "largest_cluster_size" in clusters
        assert "cluster_details" in clusters
        assert "unclustered_skills" in clusters
        
        # Validate cluster details
        for cluster_name, cluster_info in clusters["cluster_details"].items():
            assert "skills" in cluster_info
            assert "size" in cluster_info
            assert "avg_performance" in cluster_info
            assert "coherence" in cluster_info
            assert cluster_info["size"] >= 2  # Clusters should have at least 2 skills
    
    def test_skill_similarity_calculation(self, cluster_analyzer):
        """Test skill similarity calculation"""
        # Test related skills
        similarity1 = cluster_analyzer._calculate_skill_similarity("sql", "database")
        assert similarity1 > 0.5
        
        # Test unrelated skills
        similarity2 = cluster_analyzer._calculate_skill_similarity("networking", "cooking")
        assert similarity2 < 0.3
    
    def test_cluster_performance_calculation(self, cluster_analyzer, sample_skills_data):
        """Test cluster performance calculation"""
        cluster_skills = ["network security", "hipaa compliance"]
        performance = cluster_analyzer._calculate_cluster_performance(cluster_skills, sample_skills_data)
        
        assert 0.0 <= performance <= 1.0
    
    def test_cluster_coherence_calculation(self, cluster_analyzer):
        """Test cluster coherence calculation"""
        # Related skills should have high coherence
        related_skills = ["sql", "database", "mysql"]
        coherence1 = cluster_analyzer._calculate_cluster_coherence(related_skills)
        assert coherence1 > 0.3
        
        # Unrelated skills should have low coherence
        unrelated_skills = ["networking", "cooking", "dancing"]
        coherence2 = cluster_analyzer._calculate_cluster_coherence(unrelated_skills)
        assert coherence2 < 0.3


class TestTrendAnalyzer:
    """Test the trend analysis component"""
    
    @pytest.fixture
    def trend_analyzer(self):
        return TrendAnalyzer()
    
    def test_performance_trend_analysis(self, trend_analyzer, mock_memory_data, sample_feedback_history):
        """Test performance trend analysis"""
        trends = trend_analyzer.analyze_performance_trends(mock_memory_data, sample_feedback_history)
        
        assert isinstance(trends, dict)
        required_fields = [
            "analysis_period_days", "feedback_trend", "usage_trend",
            "learning_velocity", "improvement_opportunities", "overall_trend"
        ]
        for field in required_fields:
            assert field in trends
        
        # Validate trend values
        assert trends["overall_trend"] in ["positive", "negative", "stable"]
    
    def test_feedback_trend_analysis(self, trend_analyzer, sample_feedback_history):
        """Test feedback trend analysis"""
        trend = trend_analyzer._analyze_feedback_trend(sample_feedback_history)
        
        assert isinstance(trend, dict)
        assert "trend" in trend
        assert "confidence" in trend
        assert trend["trend"] in ["improving", "declining", "stable", "insufficient_data"]
        assert 0.0 <= trend["confidence"] <= 1.0
    
    def test_usage_trend_analysis(self, trend_analyzer, mock_memory_data):
        """Test usage trend analysis"""
        cutoff_date = datetime.now() - timedelta(days=30)
        trend = trend_analyzer._analyze_usage_trend(mock_memory_data, cutoff_date)
        
        assert isinstance(trend, dict)
        assert "usage_rate" in trend
        assert "average_usage_score" in trend
        assert "trend" in trend
        assert 0.0 <= trend["usage_rate"] <= 1.0
        assert trend["trend"] in ["high", "medium", "low"]
    
    def test_learning_velocity_calculation(self, trend_analyzer, sample_feedback_history):
        """Test learning velocity calculation"""
        velocity = trend_analyzer._calculate_learning_velocity(sample_feedback_history)
        
        assert isinstance(velocity, dict)
        assert "velocity" in velocity
        assert "trend" in velocity
        assert velocity["velocity"] >= 0.0
        assert velocity["trend"] in ["fast", "moderate", "slow", "no_learning", "no_data"]
    
    def test_improvement_opportunities_identification(self, trend_analyzer, mock_memory_data, sample_feedback_history):
        """Test improvement opportunity identification"""
        opportunities = trend_analyzer._identify_improvement_opportunities(mock_memory_data, sample_feedback_history)
        
        assert isinstance(opportunities, list)
        
        for opportunity in opportunities:
            assert isinstance(opportunity, dict)
            required_fields = ["type", "priority", "issue", "recommendation"]
            for field in required_fields:
                assert field in opportunity
            assert opportunity["priority"] in ["high", "medium", "low"]
    
    def test_feedback_to_score_conversion(self, trend_analyzer):
        """Test feedback to score conversion"""
        test_cases = [
            ("accepted", 1.0),
            ("improved", 0.8),
            ("rejected", 0.0),
            ("neutral", 0.5)
        ]
        
        for outcome, expected_score in test_cases:
            feedback = {"outcome": outcome}
            score = trend_analyzer._feedback_to_score(feedback)
            assert abs(score - expected_score) < 0.1
    
    def test_trend_slope_calculation(self, trend_analyzer):
        """Test trend slope calculation"""
        # Increasing trend
        increasing_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        slope1 = trend_analyzer._calculate_trend_slope(increasing_values)
        assert slope1 > 0
        
        # Decreasing trend
        decreasing_values = [5.0, 4.0, 3.0, 2.0, 1.0]
        slope2 = trend_analyzer._calculate_trend_slope(decreasing_values)
        assert slope2 < 0
        
        # Flat trend
        flat_values = [3.0, 3.0, 3.0, 3.0, 3.0]
        slope3 = trend_analyzer._calculate_trend_slope(flat_values)
        assert abs(slope3) < 0.1
    
    def test_overall_trend_determination(self, trend_analyzer):
        """Test overall trend determination"""
        # Positive trend
        positive_trends = {
            "feedback_trend": {"trend": "improving"},
            "usage_trend": {"trend": "high"},
            "learning_velocity": {"trend": "fast"}
        }
        overall1 = trend_analyzer._determine_overall_trend(
            positive_trends["feedback_trend"],
            positive_trends["usage_trend"],
            positive_trends["learning_velocity"]
        )
        assert overall1 == "positive"
        
        # Negative trend
        negative_trends = {
            "feedback_trend": {"trend": "declining"},
            "usage_trend": {"trend": "low"},
            "learning_velocity": {"trend": "slow"}
        }
        overall2 = trend_analyzer._determine_overall_trend(
            negative_trends["feedback_trend"],
            negative_trends["usage_trend"],
            negative_trends["learning_velocity"]
        )
        assert overall2 == "negative"


class TestAnalyticsPerformance:
    """Test performance characteristics of analytics system"""
    
    def test_large_dataset_performance(self, memory_analytics):
        """Test performance with large datasets"""
        # Create large mock dataset
        large_skills = {}
        for i in range(100):
            large_skills[f"skill_{i}"] = {
                "skill_name": f"Skill {i}",
                "context": f"Context for skill {i}",
                "experience_years": i % 10,
                "last_updated": datetime.now().isoformat(),
                "confidence_score": 0.8,
                "usage_count": i % 20
            }
        
        large_memory_data = {
            "user_profile": {"skills": large_skills},
            "metadata": {"total_interactions": 100}
        }
        
        # Generate large feedback history
        large_feedback = []
        for i in range(50):
            large_feedback.append({
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "outcome": ["accepted", "rejected", "improved"][i % 3],
                "skill_name": f"Skill {i % 20}",
                "feedback_text": f"Feedback {i}"
            })
        
        # Test performance
        _, execution_time = measure_execution_time(
            memory_analytics.generate_comprehensive_report,
            large_memory_data, large_feedback
        )
        
        # Should handle large datasets efficiently
        assert execution_time < 10000  # Under 10 seconds for 100 skills + 50 feedback items
    
    def test_analytics_caching(self, memory_analytics, mock_memory_data):
        """Test analytics caching functionality"""
        # First call
        _, time1 = measure_execution_time(
            memory_analytics.generate_comprehensive_report,
            mock_memory_data
        )
        
        # Second call (should use cache)
        _, time2 = measure_execution_time(
            memory_analytics.generate_comprehensive_report,
            mock_memory_data
        )
        
        # Second call should be faster due to caching
        assert time2 < time1 * 0.8  # At least 20% faster
    
    def test_memory_usage_efficiency(self, memory_analytics, mock_memory_data):
        """Test memory usage efficiency"""
        import tracemalloc
        
        # Start tracing
        tracemalloc.start()
        
        # Run analytics
        memory_analytics.generate_comprehensive_report(mock_memory_data)
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage should be reasonable (under 50MB for test data)
        assert peak < 50 * 1024 * 1024  # 50MB limit


class TestAnalyticsIntegration:
    """Test integration scenarios for analytics system"""
    
    def test_analytics_with_empty_data(self, memory_analytics):
        """Test analytics with empty or minimal data"""
        empty_data = {
            "user_profile": {"skills": {}},
            "metadata": {"total_interactions": 0}
        }
        
        result = memory_analytics.generate_comprehensive_report(empty_data, [])
        
        # Should handle empty data gracefully
        assert result is not None
        assert result["metadata"]["total_skills"] == 0
        assert len(result["optimization_recommendations"]) >= 0
    
    def test_analytics_with_corrupted_data(self, memory_analytics):
        """Test analytics with corrupted or malformed data"""
        corrupted_data = {
            "user_profile": {
                "skills": {
                    "skill_1": {"invalid": "structure"},
                    "skill_2": None,
                    "skill_3": "not_a_dict"
                }
            }
        }
        
        # Should handle corrupted data gracefully
        result = memory_analytics.generate_comprehensive_report(corrupted_data, [])
        assert result is not None
    
    def test_real_time_analytics_updates(self, memory_analytics, mock_memory_data):
        """Test real-time analytics updates"""
        # Initial analytics
        initial_report = memory_analytics.generate_comprehensive_report(mock_memory_data)
        initial_health = initial_report["memory_health"]["overall_score"]
        
        # Simulate new skill addition
        new_skill = {
            "skill_name": "New Advanced Skill",
            "context": "Recently acquired advanced skill",
            "experience_years": 1,
            "last_updated": datetime.now().isoformat(),
            "confidence_score": 0.9,
            "usage_count": 1
        }
        mock_memory_data["user_profile"]["skills"]["new_skill"] = new_skill
        
        # Updated analytics
        updated_report = memory_analytics.generate_comprehensive_report(mock_memory_data)
        updated_health = updated_report["memory_health"]["overall_score"]
        
        # Should reflect the change
        assert updated_report["metadata"]["total_skills"] > initial_report["metadata"]["total_skills"]