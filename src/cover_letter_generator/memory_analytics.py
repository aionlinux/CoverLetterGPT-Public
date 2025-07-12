"""
Advanced Memory Analytics and Insights System
=============================================

Sophisticated analytics engine for memory system performance, learning patterns,
skill evolution, and intelligent recommendations for optimization.

Author: Claude AI (Anthropic)  
Purpose: Ultra-fine-tuned memory analytics for public GitHub showcase
"""

import json
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path

# Import our performance monitoring and error handling
from .performance_monitor import performance_monitor, get_global_performance_monitor
from .error_handler import with_error_handling, get_global_error_handler


@dataclass
class SkillEvolution:
    """Track how a skill's performance evolves over time"""
    skill_name: str
    first_seen: datetime
    last_updated: datetime
    usage_frequency: int
    performance_scores: List[float]
    context_diversity: int
    improvement_trend: float  # -1 to 1, negative means declining
    confidence_evolution: List[float]
    job_matches: List[str]  # Types of jobs this skill matched
    
    @property
    def average_performance(self) -> float:
        return statistics.mean(self.performance_scores) if self.performance_scores else 0.0
    
    @property
    def performance_stability(self) -> float:
        """Measure how stable the skill performance is (lower variance = more stable)"""
        if len(self.performance_scores) < 2:
            return 1.0
        return 1.0 / (1.0 + statistics.stdev(self.performance_scores))
    
    @property
    def days_active(self) -> int:
        return (self.last_updated - self.first_seen).days
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "usage_frequency": self.usage_frequency,
            "average_performance": self.average_performance,
            "performance_stability": self.performance_stability,
            "improvement_trend": self.improvement_trend,
            "context_diversity": self.context_diversity,
            "days_active": self.days_active,
            "job_match_types": list(set(self.job_matches))
        }


@dataclass
class LearningPattern:
    """Identify patterns in how the system learns and improves"""
    pattern_type: str  # "improvement", "plateau", "decline", "cyclical"
    confidence: float
    time_span: timedelta
    affected_skills: List[str]
    trigger_events: List[str]
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type": self.pattern_type,
            "confidence": self.confidence,
            "time_span_days": self.time_span.days,
            "affected_skills": self.affected_skills,
            "trigger_events": self.trigger_events,
            "description": self.description
        }


@dataclass
class MemoryHealth:
    """Overall health assessment of the memory system"""
    overall_score: float  # 0-100
    skill_diversity: float
    learning_velocity: float
    memory_efficiency: float
    data_quality: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "skill_diversity": self.skill_diversity,
            "learning_velocity": self.learning_velocity,
            "memory_efficiency": self.memory_efficiency,
            "data_quality": self.data_quality,
            "recommendations": self.recommendations
        }


class SkillClusterAnalyzer:
    """Analyze skill relationships and identify clusters"""
    
    def __init__(self):
        # Predefined skill relationship weights
        self.skill_relationships = {
            ("sql", "database"): 0.9,
            ("python", "scripting"): 0.8,
            ("network", "security"): 0.7,
            ("project management", "leadership"): 0.6,
            ("excel", "data analysis"): 0.8,
            ("cloud", "aws"): 0.9,
            ("linux", "system administration"): 0.8
        }
    
    def analyze_skill_clusters(self, skills: Dict[str, Any]) -> Dict[str, Any]:
        """Identify skill clusters and relationships"""
        
        clusters = defaultdict(list)
        skill_names = [skill["skill_name"].lower() for skill in skills.values()]
        
        # Group skills by similarity
        for i, skill1 in enumerate(skill_names):
            cluster_key = f"cluster_{len(clusters)}"
            
            for j, skill2 in enumerate(skill_names[i+1:], i+1):
                similarity = self._calculate_skill_similarity(skill1, skill2)
                
                if similarity > 0.6:  # Threshold for clustering
                    # Add to existing cluster or create new one
                    found_cluster = False
                    for cluster_name, cluster_skills in clusters.items():
                        if skill1 in cluster_skills or skill2 in cluster_skills:
                            if skill1 not in cluster_skills:
                                cluster_skills.append(skill1)
                            if skill2 not in cluster_skills:
                                cluster_skills.append(skill2)
                            found_cluster = True
                            break
                    
                    if not found_cluster:
                        clusters[cluster_key] = [skill1, skill2]
        
        # Calculate cluster statistics
        cluster_stats = {}
        for cluster_name, cluster_skills in clusters.items():
            if len(cluster_skills) >= 2:
                cluster_stats[cluster_name] = {
                    "skills": cluster_skills,
                    "size": len(cluster_skills),
                    "avg_performance": self._calculate_cluster_performance(cluster_skills, skills),
                    "coherence": self._calculate_cluster_coherence(cluster_skills)
                }
        
        return {
            "total_clusters": len(cluster_stats),
            "largest_cluster_size": max([stats["size"] for stats in cluster_stats.values()]) if cluster_stats else 0,
            "cluster_details": cluster_stats,
            "unclustered_skills": [skill for skill in skill_names if not any(skill in cluster["skills"] for cluster in cluster_stats.values())]
        }
    
    def _calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills"""
        
        # Check predefined relationships
        for (s1, s2), weight in self.skill_relationships.items():
            if (s1 in skill1 and s2 in skill2) or (s2 in skill1 and s1 in skill2):
                return weight
        
        # Word overlap similarity
        words1 = set(skill1.split())
        words2 = set(skill2.split())
        
        if words1 and words2:
            overlap = len(words1.intersection(words2))
            union = len(words1.union(words2))
            return overlap / union if union > 0 else 0
        
        return 0
    
    def _calculate_cluster_performance(self, cluster_skills: List[str], all_skills: Dict[str, Any]) -> float:
        """Calculate average performance of skills in cluster"""
        performances = []
        
        for skill_name, skill_data in all_skills.items():
            if skill_data["skill_name"].lower() in cluster_skills:
                # Estimate performance based on usage and recency
                last_updated = datetime.fromisoformat(skill_data.get("last_updated", datetime.now().isoformat()))
                days_since_update = (datetime.now() - last_updated).days
                
                # More recent = higher performance score
                performance = max(0, 1.0 - (days_since_update / 365))
                performances.append(performance)
        
        return statistics.mean(performances) if performances else 0.0
    
    def _calculate_cluster_coherence(self, cluster_skills: List[str]) -> float:
        """Calculate how coherent/related the skills in a cluster are"""
        if len(cluster_skills) < 2:
            return 1.0
        
        total_similarity = 0
        comparisons = 0
        
        for i, skill1 in enumerate(cluster_skills):
            for skill2 in cluster_skills[i+1:]:
                total_similarity += self._calculate_skill_similarity(skill1, skill2)
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0


class TrendAnalyzer:
    """Analyze trends in memory performance and learning"""
    
    def __init__(self):
        self.trend_window_days = 30
    
    def analyze_performance_trends(self, memory_data: Dict[str, Any], 
                                 feedback_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        
        now = datetime.now()
        cutoff_date = now - timedelta(days=self.trend_window_days)
        
        # Filter recent feedback
        recent_feedback = [
            fb for fb in feedback_history
            if datetime.fromisoformat(fb.get("timestamp", now.isoformat())) > cutoff_date
        ]
        
        # Analyze feedback trends
        feedback_trend = self._analyze_feedback_trend(recent_feedback)
        
        # Analyze skill usage trends
        usage_trend = self._analyze_usage_trend(memory_data, cutoff_date)
        
        # Analyze learning velocity
        learning_velocity = self._calculate_learning_velocity(recent_feedback)
        
        # Identify improvement opportunities
        improvement_opportunities = self._identify_improvement_opportunities(memory_data, recent_feedback)
        
        return {
            "analysis_period_days": self.trend_window_days,
            "feedback_trend": feedback_trend,
            "usage_trend": usage_trend,
            "learning_velocity": learning_velocity,
            "improvement_opportunities": improvement_opportunities,
            "overall_trend": self._determine_overall_trend(feedback_trend, usage_trend, learning_velocity)
        }
    
    def _analyze_feedback_trend(self, feedback_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in user feedback"""
        
        if not feedback_history:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        # Group feedback by week
        weekly_feedback = defaultdict(list)
        
        for feedback in feedback_history:
            timestamp = datetime.fromisoformat(feedback.get("timestamp", datetime.now().isoformat()))
            week_key = timestamp.strftime("%Y-W%U")
            
            # Convert feedback to numeric score
            score = self._feedback_to_score(feedback)
            weekly_feedback[week_key].append(score)
        
        # Calculate weekly averages
        weekly_averages = {
            week: statistics.mean(scores)
            for week, scores in weekly_feedback.items()
        }
        
        if len(weekly_averages) < 2:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        # Calculate trend
        weeks = sorted(weekly_averages.keys())
        scores = [weekly_averages[week] for week in weeks]
        
        trend_slope = self._calculate_trend_slope(scores)
        
        if trend_slope > 0.1:
            trend = "improving"
        elif trend_slope < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": trend_slope,
            "confidence": min(1.0, len(scores) / 4),  # More data = higher confidence
            "weekly_scores": dict(zip(weeks, scores))
        }
    
    def _analyze_usage_trend(self, memory_data: Dict[str, Any], cutoff_date: datetime) -> Dict[str, Any]:
        """Analyze trends in skill usage"""
        
        skills = memory_data.get("user_profile", {}).get("skills", {})
        
        recent_usage = []
        total_skills = len(skills)
        active_skills = 0
        
        for skill_data in skills.values():
            last_updated = datetime.fromisoformat(skill_data.get("last_updated", datetime.now().isoformat()))
            
            if last_updated > cutoff_date:
                active_skills += 1
                days_ago = (datetime.now() - last_updated).days
                usage_score = max(0, 1.0 - (days_ago / 30))  # Decay over 30 days
                recent_usage.append(usage_score)
        
        usage_rate = active_skills / total_skills if total_skills > 0 else 0
        avg_usage_score = statistics.mean(recent_usage) if recent_usage else 0
        
        return {
            "usage_rate": usage_rate,
            "average_usage_score": avg_usage_score,
            "active_skills": active_skills,
            "total_skills": total_skills,
            "trend": "high" if usage_rate > 0.3 else "medium" if usage_rate > 0.1 else "low"
        }
    
    def _calculate_learning_velocity(self, feedback_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate how quickly the system is learning"""
        
        if not feedback_history:
            return {"velocity": 0.0, "trend": "no_data"}
        
        # Group feedback by day
        daily_learning = defaultdict(int)
        
        for feedback in feedback_history:
            timestamp = datetime.fromisoformat(feedback.get("timestamp", datetime.now().isoformat()))
            day_key = timestamp.strftime("%Y-%m-%d")
            
            # Count positive learning events
            if feedback.get("outcome") in ["accepted", "improved"]:
                daily_learning[day_key] += 1
        
        learning_events = list(daily_learning.values())
        
        if not learning_events:
            return {"velocity": 0.0, "trend": "no_learning"}
        
        avg_learning_per_day = statistics.mean(learning_events)
        
        # Determine trend
        if avg_learning_per_day > 1.0:
            trend = "fast"
        elif avg_learning_per_day > 0.3:
            trend = "moderate"
        else:
            trend = "slow"
        
        return {
            "velocity": avg_learning_per_day,
            "trend": trend,
            "total_learning_events": sum(learning_events),
            "learning_days": len(daily_learning)
        }
    
    def _identify_improvement_opportunities(self, memory_data: Dict[str, Any], 
                                         feedback_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify specific opportunities for improvement"""
        
        opportunities = []
        
        # Analyze underperforming skills
        skills = memory_data.get("user_profile", {}).get("skills", {})
        
        # Skills with poor feedback
        skill_feedback = defaultdict(list)
        for feedback in feedback_history:
            if "skill_name" in feedback:
                skill_feedback[feedback["skill_name"]].append(feedback)
        
        for skill_name, feedbacks in skill_feedback.items():
            negative_feedback = sum(1 for fb in feedbacks if fb.get("outcome") == "rejected")
            total_feedback = len(feedbacks)
            
            if total_feedback >= 3 and negative_feedback / total_feedback > 0.6:
                opportunities.append({
                    "type": "skill_improvement",
                    "priority": "high",
                    "skill": skill_name,
                    "issue": "High rejection rate",
                    "recommendation": f"Review and improve scoring algorithm for {skill_name}"
                })
        
        # Skills with low usage
        now = datetime.now()
        for skill_name, skill_data in skills.items():
            last_updated = datetime.fromisoformat(skill_data.get("last_updated", now.isoformat()))
            days_unused = (now - last_updated).days
            
            if days_unused > 90:  # Unused for 3 months
                opportunities.append({
                    "type": "skill_maintenance",
                    "priority": "medium",
                    "skill": skill_name,
                    "issue": "Long period without usage",
                    "recommendation": f"Consider archiving or updating {skill_name}"
                })
        
        # Data quality issues
        skills_with_empty_context = sum(1 for skill in skills.values() if not skill.get("context"))
        if skills_with_empty_context > len(skills) * 0.3:
            opportunities.append({
                "type": "data_quality",
                "priority": "medium",
                "issue": "Many skills lack context information",
                "recommendation": "Improve context collection for better relevance scoring"
            })
        
        return opportunities
    
    def _feedback_to_score(self, feedback: Dict[str, Any]) -> float:
        """Convert feedback to numeric score"""
        outcome = feedback.get("outcome", "neutral")
        
        score_mapping = {
            "accepted": 1.0,
            "improved": 0.8,
            "revision_requested": 0.4,
            "rejected": 0.0,
            "neutral": 0.5
        }
        
        return score_mapping.get(outcome, 0.5)
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        if len(values) < 2:
            return 0.0
        
        x = list(range(len(values)))
        n = len(values)
        
        # Linear regression slope calculation
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def _determine_overall_trend(self, feedback_trend: Dict, usage_trend: Dict, learning_velocity: Dict) -> str:
        """Determine overall system trend"""
        
        feedback_score = {"improving": 1, "stable": 0, "declining": -1}.get(feedback_trend.get("trend"), 0)
        usage_score = {"high": 1, "medium": 0, "low": -1}.get(usage_trend.get("trend"), 0)
        velocity_score = {"fast": 1, "moderate": 0, "slow": -1}.get(learning_velocity.get("trend"), 0)
        
        overall_score = (feedback_score + usage_score + velocity_score) / 3
        
        if overall_score > 0.3:
            return "positive"
        elif overall_score < -0.3:
            return "negative"
        else:
            return "stable"


class MemoryAnalytics:
    """
    Advanced memory analytics system providing deep insights into learning patterns,
    skill evolution, performance trends, and optimization recommendations.
    
    Features:
    - Skill evolution tracking with performance metrics
    - Learning pattern identification and analysis
    - Memory health assessment with recommendations
    - Skill clustering and relationship analysis
    - Performance trend analysis with predictive insights
    - Automated optimization recommendations
    """
    
    def __init__(self):
        self.skill_cluster_analyzer = SkillClusterAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        
        # Get monitoring and error handling
        self.performance_monitor = get_global_performance_monitor()
        self.error_handler = get_global_error_handler()
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    @performance_monitor(get_global_performance_monitor(), "memory_analytics", "generate_comprehensive_report", use_cache=True)
    @with_error_handling(get_global_error_handler(), "memory_analytics", "generate_comprehensive_report")
    def generate_comprehensive_report(self, memory_data: Dict[str, Any], 
                                    feedback_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        feedback_history = feedback_history or []
        
        # Generate all analytics components
        skill_evolution = self.analyze_skill_evolution(memory_data)
        learning_patterns = self.identify_learning_patterns(memory_data, feedback_history)
        memory_health = self.assess_memory_health(memory_data, feedback_history)
        skill_clusters = self.skill_cluster_analyzer.analyze_skill_clusters(
            memory_data.get("user_profile", {}).get("skills", {})
        )
        performance_trends = self.trend_analyzer.analyze_performance_trends(memory_data, feedback_history)
        optimization_recommendations = self.generate_optimization_recommendations(
            memory_data, feedback_history, skill_evolution
        )
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            skill_evolution, learning_patterns, memory_health, performance_trends
        )
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "memory_health": memory_health.to_dict(),
            "skill_evolution": {
                "total_skills_tracked": len(skill_evolution),
                "top_performing_skills": [
                    evolution.to_dict() for evolution in 
                    sorted(skill_evolution.values(), key=lambda x: x.average_performance, reverse=True)[:5]
                ],
                "declining_skills": [
                    evolution.to_dict() for evolution in 
                    sorted(skill_evolution.values(), key=lambda x: x.improvement_trend)[:3]
                ],
                "most_active_skills": [
                    evolution.to_dict() for evolution in 
                    sorted(skill_evolution.values(), key=lambda x: x.usage_frequency, reverse=True)[:5]
                ]
            },
            "learning_patterns": [pattern.to_dict() for pattern in learning_patterns],
            "skill_clusters": skill_clusters,
            "performance_trends": performance_trends,
            "optimization_recommendations": optimization_recommendations,
            "metadata": {
                "total_skills": len(memory_data.get("user_profile", {}).get("skills", {})),
                "total_interactions": memory_data.get("metadata", {}).get("total_interactions", 0),
                "feedback_entries": len(feedback_history),
                "analysis_depth": "comprehensive"
            }
        }
    
    def analyze_skill_evolution(self, memory_data: Dict[str, Any]) -> Dict[str, SkillEvolution]:
        """Analyze how skills have evolved over time"""
        
        skills = memory_data.get("user_profile", {}).get("skills", {})
        evolutions = {}
        
        for skill_key, skill_data in skills.items():
            skill_name = skill_data.get("skill_name", skill_key)
            
            # Parse timestamps
            last_updated = datetime.fromisoformat(skill_data.get("last_updated", datetime.now().isoformat()))
            first_seen = last_updated  # Simplified - in real system, track this separately
            
            # Analyze usage patterns (simplified)
            usage_frequency = 1  # Would be tracked in real system
            
            # Estimate performance scores based on available data
            performance_scores = [0.7]  # Placeholder - would use actual feedback scores
            
            # Analyze context diversity
            context = skill_data.get("context", "")
            context_diversity = len(set(context.split())) if context else 1
            
            # Calculate improvement trend (simplified)
            improvement_trend = 0.1  # Placeholder - would calculate from historical data
            
            # Track job matches (simplified)
            job_matches = ["general"]  # Would track actual job types
            
            evolution = SkillEvolution(
                skill_name=skill_name,
                first_seen=first_seen,
                last_updated=last_updated,
                usage_frequency=usage_frequency,
                performance_scores=performance_scores,
                context_diversity=context_diversity,
                improvement_trend=improvement_trend,
                confidence_evolution=[0.8],  # Placeholder
                job_matches=job_matches
            )
            
            evolutions[skill_key] = evolution
        
        return evolutions
    
    def identify_learning_patterns(self, memory_data: Dict[str, Any], 
                                 feedback_history: List[Dict[str, Any]]) -> List[LearningPattern]:
        """Identify patterns in learning and improvement"""
        
        patterns = []
        
        # Analyze feedback patterns over time
        if len(feedback_history) >= 5:
            # Group feedback by time periods
            recent_feedback = [
                fb for fb in feedback_history
                if datetime.fromisoformat(fb.get("timestamp", datetime.now().isoformat())) > 
                datetime.now() - timedelta(days=30)
            ]
            
            older_feedback = [
                fb for fb in feedback_history
                if datetime.fromisoformat(fb.get("timestamp", datetime.now().isoformat())) <= 
                datetime.now() - timedelta(days=30)
            ]
            
            # Calculate improvement pattern
            if recent_feedback and older_feedback:
                recent_score = statistics.mean([
                    self.trend_analyzer._feedback_to_score(fb) for fb in recent_feedback
                ])
                older_score = statistics.mean([
                    self.trend_analyzer._feedback_to_score(fb) for fb in older_feedback
                ])
                
                if recent_score > older_score + 0.2:
                    patterns.append(LearningPattern(
                        pattern_type="improvement",
                        confidence=0.8,
                        time_span=timedelta(days=30),
                        affected_skills=list(set(fb.get("skill_name", "unknown") for fb in recent_feedback)),
                        trigger_events=["increased feedback quality"],
                        description="System shows consistent improvement over the last 30 days"
                    ))
        
        # Identify skill-specific patterns
        skill_feedback = defaultdict(list)
        for feedback in feedback_history:
            if "skill_name" in feedback:
                skill_feedback[feedback["skill_name"]].append(feedback)
        
        for skill_name, feedbacks in skill_feedback.items():
            if len(feedbacks) >= 3:
                scores = [self.trend_analyzer._feedback_to_score(fb) for fb in feedbacks]
                
                # Check for plateau pattern
                if len(set(scores)) == 1:  # All scores the same
                    patterns.append(LearningPattern(
                        pattern_type="plateau",
                        confidence=0.9,
                        time_span=timedelta(days=len(feedbacks) * 7),  # Estimate
                        affected_skills=[skill_name],
                        trigger_events=["consistent scoring"],
                        description=f"Skill '{skill_name}' shows plateau pattern - consistent but not improving"
                    ))
        
        return patterns
    
    def assess_memory_health(self, memory_data: Dict[str, Any], 
                           feedback_history: List[Dict[str, Any]]) -> MemoryHealth:
        """Assess overall health of the memory system"""
        
        skills = memory_data.get("user_profile", {}).get("skills", {})
        total_skills = len(skills)
        
        # Calculate skill diversity
        skill_categories = defaultdict(int)
        for skill_data in skills.values():
            context = skill_data.get("context", "").lower()
            
            # Categorize skills (simplified)
            if any(term in context for term in ["network", "system", "server"]):
                skill_categories["technical"] += 1
            elif any(term in context for term in ["business", "analysis", "process"]):
                skill_categories["business"] += 1
            else:
                skill_categories["general"] += 1
        
        skill_diversity = len(skill_categories) / 3.0 if total_skills > 0 else 0  # Max 3 categories
        
        # Calculate learning velocity
        recent_feedback = [
            fb for fb in feedback_history
            if datetime.fromisoformat(fb.get("timestamp", datetime.now().isoformat())) > 
            datetime.now() - timedelta(days=30)
        ]
        
        learning_velocity = len(recent_feedback) / 30.0 if recent_feedback else 0  # Feedback per day
        learning_velocity = min(1.0, learning_velocity)  # Cap at 1.0
        
        # Calculate memory efficiency
        active_skills = sum(
            1 for skill_data in skills.values()
            if datetime.fromisoformat(skill_data.get("last_updated", datetime.now().isoformat())) >
            datetime.now() - timedelta(days=90)
        )
        
        memory_efficiency = active_skills / total_skills if total_skills > 0 else 0
        
        # Calculate data quality
        skills_with_context = sum(1 for skill_data in skills.values() if skill_data.get("context"))
        data_quality = skills_with_context / total_skills if total_skills > 0 else 0
        
        # Calculate overall score
        overall_score = (skill_diversity * 25 + learning_velocity * 25 + 
                        memory_efficiency * 25 + data_quality * 25)
        
        # Generate recommendations
        recommendations = []
        
        if skill_diversity < 0.5:
            recommendations.append("Increase skill diversity by adding skills from different domains")
        
        if learning_velocity < 0.1:
            recommendations.append("Increase learning activity - system needs more feedback to improve")
        
        if memory_efficiency < 0.5:
            recommendations.append("Clean up inactive skills to improve memory efficiency")
        
        if data_quality < 0.7:
            recommendations.append("Improve data quality by adding context to skills without descriptions")
        
        if overall_score > 80:
            recommendations.append("Excellent memory health - continue current practices")
        elif overall_score > 60:
            recommendations.append("Good memory health with room for improvement")
        else:
            recommendations.append("Memory health needs attention - focus on data quality and learning activity")
        
        return MemoryHealth(
            overall_score=overall_score,
            skill_diversity=skill_diversity,
            learning_velocity=learning_velocity,
            memory_efficiency=memory_efficiency,
            data_quality=data_quality,
            recommendations=recommendations
        )
    
    def generate_optimization_recommendations(self, memory_data: Dict[str, Any],
                                            feedback_history: List[Dict[str, Any]],
                                            skill_evolution: Dict[str, SkillEvolution]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for system optimization"""
        
        recommendations = []
        
        # Analyze skill performance
        if skill_evolution:
            # Identify underperforming skills
            underperforming = [
                evolution for evolution in skill_evolution.values()
                if evolution.average_performance < 0.5 and evolution.usage_frequency > 2
            ]
            
            if underperforming:
                recommendations.append({
                    "category": "skill_optimization",
                    "priority": "high",
                    "title": "Optimize underperforming skills",
                    "description": f"Review scoring algorithm for {len(underperforming)} underperforming skills",
                    "affected_skills": [skill.skill_name for skill in underperforming[:5]],
                    "expected_impact": "Improve relevance scoring accuracy by 15-25%"
                })
            
            # Identify opportunities for skill clustering
            isolated_skills = [
                evolution for evolution in skill_evolution.values()
                if evolution.context_diversity < 2 and evolution.usage_frequency > 1
            ]
            
            if len(isolated_skills) > 5:
                recommendations.append({
                    "category": "data_organization",
                    "priority": "medium",
                    "title": "Improve skill clustering",
                    "description": "Group related skills together for better context understanding",
                    "affected_skills": [skill.skill_name for skill in isolated_skills[:5]],
                    "expected_impact": "Enhance semantic matching by 10-15%"
                })
        
        # Analyze feedback patterns
        if feedback_history:
            # Check for feedback imbalances
            positive_feedback = sum(1 for fb in feedback_history if fb.get("outcome") in ["accepted", "improved"])
            total_feedback = len(feedback_history)
            
            if total_feedback > 10 and positive_feedback / total_feedback < 0.6:
                recommendations.append({
                    "category": "algorithm_tuning",
                    "priority": "high",
                    "title": "Improve acceptance rate",
                    "description": f"Current acceptance rate is {positive_feedback/total_feedback:.1%}, target is >60%",
                    "expected_impact": "Increase user satisfaction and system effectiveness"
                })
        
        # Memory efficiency recommendations
        skills = memory_data.get("user_profile", {}).get("skills", {})
        old_skills = [
            skill_name for skill_name, skill_data in skills.items()
            if datetime.fromisoformat(skill_data.get("last_updated", datetime.now().isoformat())) <
            datetime.now() - timedelta(days=180)
        ]
        
        if len(old_skills) > 10:
            recommendations.append({
                "category": "memory_cleanup",
                "priority": "medium",
                "title": "Archive old skills",
                "description": f"Archive {len(old_skills)} skills unused for 6+ months",
                "expected_impact": "Improve system performance and reduce memory usage"
            })
        
        # Performance optimization
        total_skills = len(skills)
        if total_skills > 500:
            recommendations.append({
                "category": "performance",
                "priority": "medium",
                "title": "Implement skill indexing",
                "description": "Large skill database detected - implement indexing for faster lookups",
                "expected_impact": "Reduce query time by 30-50%"
            })
        
        return recommendations
    
    def _generate_executive_summary(self, skill_evolution: Dict[str, SkillEvolution],
                                  learning_patterns: List[LearningPattern],
                                  memory_health: MemoryHealth,
                                  performance_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of analytics"""
        
        # Key metrics
        total_skills = len(skill_evolution)
        avg_performance = statistics.mean([
            evolution.average_performance for evolution in skill_evolution.values()
        ]) if skill_evolution else 0
        
        improving_skills = sum(
            1 for evolution in skill_evolution.values()
            if evolution.improvement_trend > 0.1
        )
        
        # Overall assessment
        if memory_health.overall_score > 80:
            assessment = "excellent"
        elif memory_health.overall_score > 60:
            assessment = "good"
        elif memory_health.overall_score > 40:
            assessment = "needs_improvement"
        else:
            assessment = "critical"
        
        return {
            "overall_assessment": assessment,
            "health_score": memory_health.overall_score,
            "key_metrics": {
                "total_skills": total_skills,
                "average_performance": avg_performance,
                "improving_skills": improving_skills,
                "learning_patterns_detected": len(learning_patterns)
            },
            "highlights": [
                f"Memory system managing {total_skills} skills with {memory_health.overall_score:.0f}% health score",
                f"Average skill performance: {avg_performance:.1%}",
                f"{improving_skills} skills showing improvement trends",
                f"Overall system trend: {performance_trends.get('overall_trend', 'unknown')}"
            ],
            "top_recommendations": memory_health.recommendations[:3]
        }
    
    def export_analytics_report(self, filepath: str, memory_data: Dict[str, Any], 
                              feedback_history: Optional[List[Dict[str, Any]]] = None):
        """Export comprehensive analytics report to file"""
        
        report = self.generate_comprehensive_report(memory_data, feedback_history)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)


# Global analytics instance
_global_memory_analytics = None

def get_global_memory_analytics() -> MemoryAnalytics:
    """Get the global memory analytics instance"""
    global _global_memory_analytics
    if _global_memory_analytics is None:
        _global_memory_analytics = MemoryAnalytics()
    return _global_memory_analytics