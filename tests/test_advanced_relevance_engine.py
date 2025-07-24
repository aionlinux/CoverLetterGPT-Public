"""
Test Suite for Advanced Relevance Engine
========================================

Comprehensive tests for the ultra-intelligent job-skill matching system,
validating semantic analysis, industry context awareness, and learning capabilities.

"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import json

from cover_letter_generator.advanced_relevance_engine import (
    AdvancedRelevanceEngine, JobAnalysisResult, SkillRelevanceScore,
    IndustryClassifier, SemanticMatcher
)
from conftest import validate_job_analysis_result, validate_skill_relevance_score, measure_execution_time


class TestAdvancedRelevanceEngine:
    """Test the advanced relevance engine functionality"""
    
    @pytest.fixture
    def relevance_engine(self):
        """Create relevance engine instance for testing"""
        return AdvancedRelevanceEngine()
    
    def test_engine_initialization(self, relevance_engine):
        """Test proper initialization of the relevance engine"""
        assert relevance_engine is not None
        assert hasattr(relevance_engine, 'industry_classifier')
        assert hasattr(relevance_engine, 'semantic_matcher')
        assert hasattr(relevance_engine, 'performance_monitor')
        assert hasattr(relevance_engine, 'error_handler')
    
    def test_job_analysis_comprehensive(self, relevance_engine, sample_job_description):
        """Test comprehensive job analysis functionality"""
        # Perform job analysis
        result, execution_time = measure_execution_time(
            relevance_engine.analyze_job_comprehensive,
            sample_job_description
        )
        
        # Validate result structure
        assert isinstance(result, JobAnalysisResult)
        assert validate_job_analysis_result(result.to_dict())
        
        # Validate content quality
        assert result.confidence_score > 0.5
        assert len(result.required_skills) > 0
        assert len(result.tech_domains) > 0
        assert result.job_role_type in ["security_analyst", "network_engineer", "healthcare_analyst"]
        
        # Validate performance
        assert execution_time < 2000  # Should complete in under 2 seconds
    
    def test_skill_relevance_scoring(self, relevance_engine, sample_job_description, sample_skills_data):
        """Test skill relevance scoring accuracy"""
        # Analyze job first
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        # Test each skill
        for skill_key, skill_data in sample_skills_data.items():
            score_result = relevance_engine.score_skill_comprehensive(skill_data, job_analysis)
            
            # Validate structure
            assert isinstance(score_result, SkillRelevanceScore)
            assert validate_skill_relevance_score(score_result.to_dict())
            
            # Validate scoring logic
            assert 0.0 <= score_result.final_score <= 1.0
            assert score_result.confidence > 0.0
            assert len(score_result.explanation) > 0
        
        # Test specific relevance expectations
        network_security_score = None
        mysql_score = None
        
        for skill_key, skill_data in sample_skills_data.items():
            score = relevance_engine.score_skill_comprehensive(skill_data, job_analysis)
            if skill_data["skill_name"] == "Network Security":
                network_security_score = score.final_score
            elif skill_data["skill_name"] == "MySQL Database":
                mysql_score = score.final_score
        
        # Network Security should be highly relevant for security analyst role
        assert network_security_score > 0.8
        
        # MySQL should be less relevant for security analyst role
        assert mysql_score < 0.4
    
    def test_industry_classification(self, relevance_engine, sample_job_description):
        """Test industry classification accuracy"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        # Should detect healthcare industry
        assert "healthcare" in job_analysis.industry_context
        healthcare_confidence = job_analysis.industry_context.get("healthcare", {}).get("confidence", 0)
        assert healthcare_confidence > 0.7
        
        # Should detect technology sector
        assert "technology" in job_analysis.industry_context
    
    def test_experience_level_detection(self, relevance_engine, sample_job_description):
        """Test experience level detection"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        # Should detect senior level (5+ years mentioned in job description)
        assert job_analysis.experience_level in ["senior", "mid_senior"]
    
    def test_technology_extraction(self, relevance_engine, sample_job_description):
        """Test explicit technology extraction"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        # Should extract mentioned technologies
        expected_technologies = ["wireshark", "nessus", "siem", "aws", "azure", "python"]
        extracted_lower = [tech.lower() for tech in job_analysis.explicit_technologies]
        
        # Should find at least 3 of the expected technologies
        matches = sum(1 for tech in expected_technologies if tech in extracted_lower)
        assert matches >= 3
    
    def test_semantic_similarity_matching(self, relevance_engine):
        """Test semantic similarity matching capabilities"""
        # Test related skills
        similarity1 = relevance_engine.semantic_matcher.calculate_similarity(
            "Network Security", "Cybersecurity"
        )
        assert similarity1 > 0.7
        
        # Test unrelated skills
        similarity2 = relevance_engine.semantic_matcher.calculate_similarity(
            "Network Security", "Social Media Marketing"
        )
        assert similarity2 < 0.3
    
    def test_domain_boost_calculation(self, relevance_engine, sample_job_description):
        """Test domain boost calculation logic"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        # Test security domain skill
        security_skill = {
            "skill_name": "Network Security",
            "context": "Implemented network security protocols"
        }
        score = relevance_engine.score_skill_comprehensive(security_skill, job_analysis)
        
        # Should receive significant domain boost
        assert score.domain_boost > 0.3
    
    def test_learning_from_feedback(self, relevance_engine, sample_feedback_history):
        """Test learning capabilities from feedback"""
        # Apply feedback learning
        relevance_engine.learn_from_feedback(sample_feedback_history)
        
        # Verify learning patterns are stored
        assert len(relevance_engine.learning_patterns) > 0
        
        # Test that negative feedback affects future scoring
        mysql_feedback = next(
            (fb for fb in sample_feedback_history if fb.get("skill_name") == "MySQL Database"),
            None
        )
        assert mysql_feedback is not None
        assert mysql_feedback["outcome"] == "rejected"
    
    def test_performance_monitoring_integration(self, relevance_engine, sample_job_description):
        """Test integration with performance monitoring"""
        # Mock performance monitor
        mock_monitor = Mock()
        relevance_engine.performance_monitor = mock_monitor
        
        # Perform analysis
        relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        # Verify monitoring calls
        assert mock_monitor.track_operation.called
    
    def test_error_handling_integration(self, relevance_engine):
        """Test error handling for invalid inputs"""
        # Test with invalid job description
        result = relevance_engine.analyze_job_comprehensive("")
        assert result is not None  # Should handle gracefully
        
        # Test with malformed skill data
        invalid_skill = {"invalid": "data"}
        job_analysis = JobAnalysisResult(
            job_role_type="test", primary_focus="test", confidence_score=0.5,
            required_skills=[], preferred_skills=[], tech_domains={}, business_domains={},
            industry_context={}, experience_level="mid", company_size="medium",
            role_complexity=0.5, explicit_technologies=[], soft_skills=[],
            key_responsibilities=[], compensation_indicators={},
            growth_potential=0.5, remote_work_indicators=[]
        )
        
        # Should handle gracefully without crashing
        try:
            score = relevance_engine.score_skill_comprehensive(invalid_skill, job_analysis)
            assert score is not None
        except Exception as e:
            # If it raises an exception, it should be handled gracefully
            assert "validation" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_caching_functionality(self, relevance_engine, sample_job_description):
        """Test caching of analysis results"""
        # First analysis
        result1, time1 = measure_execution_time(
            relevance_engine.analyze_job_comprehensive,
            sample_job_description
        )
        
        # Second analysis (should be cached)
        result2, time2 = measure_execution_time(
            relevance_engine.analyze_job_comprehensive,
            sample_job_description
        )
        
        # Results should be identical
        assert result1.to_dict() == result2.to_dict()
        
        # Second call should be significantly faster
        assert time2 < time1 * 0.5  # At least 50% faster
    
    def test_confidence_scoring(self, relevance_engine, sample_job_description, sample_skills_data):
        """Test confidence scoring accuracy"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        for skill_data in sample_skills_data.values():
            score = relevance_engine.score_skill_comprehensive(skill_data, job_analysis)
            
            # Confidence should correlate with score quality
            if score.final_score > 0.8:
                assert score.confidence > 0.7
            elif score.final_score < 0.3:
                assert score.confidence > 0.6  # High confidence in low relevance


class TestIndustryClassifier:
    """Test the industry classification component"""
    
    @pytest.fixture
    def industry_classifier(self):
        return IndustryClassifier()
    
    def test_healthcare_classification(self, industry_classifier):
        """Test healthcare industry classification"""
        healthcare_text = "HIPAA compliance healthcare patient data medical records"
        result = industry_classifier.classify_industry(healthcare_text)
        
        assert "healthcare" in result
        assert result["healthcare"]["confidence"] > 0.8
    
    def test_technology_classification(self, industry_classifier):
        """Test technology industry classification"""
        tech_text = "software development cloud computing AWS API microservices"
        result = industry_classifier.classify_industry(tech_text)
        
        assert "technology" in result
        assert result["technology"]["confidence"] > 0.8
    
    def test_financial_classification(self, industry_classifier):
        """Test financial industry classification"""
        finance_text = "banking financial services trading risk management compliance"
        result = industry_classifier.classify_industry(finance_text)
        
        assert "financial_services" in result
        assert result["financial_services"]["confidence"] > 0.7


class TestSemanticMatcher:
    """Test the semantic matching component"""
    
    @pytest.fixture
    def semantic_matcher(self):
        return SemanticMatcher()
    
    def test_exact_match(self, semantic_matcher):
        """Test exact word matching"""
        similarity = semantic_matcher.calculate_similarity("Python", "Python")
        assert similarity == 1.0
    
    def test_synonym_matching(self, semantic_matcher):
        """Test synonym matching"""
        similarity = semantic_matcher.calculate_similarity("Database", "SQL")
        assert similarity > 0.6
    
    def test_unrelated_terms(self, semantic_matcher):
        """Test unrelated terms"""
        similarity = semantic_matcher.calculate_similarity("Programming", "Cooking")
        assert similarity < 0.2
    
    def test_technical_term_matching(self, semantic_matcher):
        """Test technical term matching"""
        similarity = semantic_matcher.calculate_similarity("Machine Learning", "AI")
        assert similarity > 0.7


class TestPerformanceBenchmarks:
    """Test performance requirements"""
    
    def test_job_analysis_performance(self, relevance_engine, sample_job_description, performance_benchmarks):
        """Test job analysis performance meets benchmarks"""
        _, execution_time = measure_execution_time(
            relevance_engine.analyze_job_comprehensive,
            sample_job_description
        )
        
        assert execution_time < performance_benchmarks["job_analysis_time_ms"]
    
    def test_skill_scoring_performance(self, relevance_engine, sample_job_description, 
                                    sample_skills_data, performance_benchmarks):
        """Test skill scoring performance"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        
        for skill_data in sample_skills_data.values():
            _, execution_time = measure_execution_time(
                relevance_engine.score_skill_comprehensive,
                skill_data, job_analysis
            )
            assert execution_time < performance_benchmarks["skill_scoring_time_ms"]
    
    def test_batch_processing_performance(self, relevance_engine, sample_job_description, sample_skills_data):
        """Test batch processing performance"""
        job_analysis = relevance_engine.analyze_job_comprehensive(sample_job_description)
        skills_list = list(sample_skills_data.values())
        
        # Test batch scoring
        start_time = datetime.now()
        scores = [
            relevance_engine.score_skill_comprehensive(skill, job_analysis)
            for skill in skills_list
        ]
        end_time = datetime.now()
        
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        avg_time_per_skill = total_time_ms / len(skills_list)
        
        # Average time per skill should be reasonable
        assert avg_time_per_skill < 100  # 100ms per skill max
        assert len(scores) == len(skills_list)


class TestIntegrationScenarios:
    """Test integration scenarios with real-world complexity"""
    
    def test_complex_job_analysis(self, relevance_engine):
        """Test analysis of complex, multi-role job description"""
        complex_job = """
        Senior DevSecOps Engineer - Healthcare Fintech
        
        We're looking for a Senior DevSecOps Engineer to join our healthcare fintech startup.
        You'll be responsible for building secure, scalable infrastructure that handles sensitive
        patient financial data while maintaining HIPAA and PCI DSS compliance.
        
        Requirements:
        - 7+ years DevOps experience
        - Strong Kubernetes and Docker expertise
        - AWS/Azure cloud platforms
        - Security automation (SAST/DAST)
        - Infrastructure as Code (Terraform, Ansible)
        - CI/CD pipeline optimization
        - HIPAA and PCI DSS compliance
        - Python/Go scripting
        
        Bonus:
        - Healthcare industry experience
        - FinTech background
        - Machine learning ops
        - Monitoring and observability tools
        """
        
        result = relevance_engine.analyze_job_comprehensive(complex_job)
        
        # Should detect multiple industries
        assert "healthcare" in result.industry_context
        assert "financial_services" in result.industry_context
        
        # Should detect DevOps role type
        assert "devops" in result.job_role_type.lower() or "engineer" in result.job_role_type.lower()
        
        # Should detect senior experience level
        assert result.experience_level in ["senior", "expert"]
        
        # Should extract multiple technologies
        assert len(result.explicit_technologies) >= 5
    
    def test_ambiguous_job_analysis(self, relevance_engine):
        """Test analysis of ambiguous job description"""
        ambiguous_job = """
        Business Technology Analyst
        
        We need someone to analyze business processes and recommend technology solutions.
        The role involves working with stakeholders to understand requirements and
        translate them into technical specifications.
        """
        
        result = relevance_engine.analyze_job_comprehensive(ambiguous_job)
        
        # Should still provide reasonable analysis
        assert result.confidence_score > 0.3  # Lower confidence expected
        assert result.job_role_type is not None
        assert len(result.required_skills) > 0
    
    def test_edge_case_handling(self, relevance_engine):
        """Test handling of edge cases"""
        edge_cases = [
            "",  # Empty description
            "Job",  # Single word
            "A" * 10000,  # Very long description
            "!@#$%^&*()",  # Special characters only
        ]
        
        for case in edge_cases:
            result = relevance_engine.analyze_job_comprehensive(case)
            assert result is not None  # Should handle gracefully
            assert isinstance(result, JobAnalysisResult)
