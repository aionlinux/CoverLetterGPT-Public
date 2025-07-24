"""
Advanced Relevance Engine - Ultra-Intelligent Job-Skill Matching System
=======================================================================

A sophisticated AI-powered system for intelligent job requirement analysis and skill relevance scoring.
Features advanced semantic analysis, industry context awareness, and dynamic learning capabilities.

Purpose: Ultra-fine-tuned relevance matching for public GitHub showcase
"""

import re
import json
import math
import pickle
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
from pathlib import Path

# Import our performance monitoring and error handling
from .performance_monitor import performance_monitor, get_global_performance_monitor
from .error_handler import with_error_handling, get_global_error_handler


@dataclass
class JobAnalysisResult:
    """Comprehensive job analysis result with rich metadata"""
    job_role_type: str
    primary_focus: str
    confidence_score: float
    required_skills: List[str]
    preferred_skills: List[str]
    tech_domains: Dict[str, float]
    business_domains: Dict[str, float]
    industry_context: Dict[str, Any]
    experience_level: str
    company_size: str
    role_complexity: float
    explicit_technologies: List[str]
    soft_skills: List[str]
    key_responsibilities: List[str]
    compensation_indicators: Dict[str, Any]
    growth_potential: float
    remote_work_indicators: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_role_type": self.job_role_type,
            "primary_focus": self.primary_focus,
            "confidence_score": self.confidence_score,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "tech_domains": self.tech_domains,
            "business_domains": self.business_domains,
            "industry_context": self.industry_context,
            "experience_level": self.experience_level,
            "company_size": self.company_size,
            "role_complexity": self.role_complexity,
            "explicit_technologies": self.explicit_technologies,
            "soft_skills": self.soft_skills,
            "key_responsibilities": self.key_responsibilities,
            "compensation_indicators": self.compensation_indicators,
            "growth_potential": self.growth_potential,
            "remote_work_indicators": self.remote_work_indicators
        }


@dataclass
class SkillRelevanceScore:
    """Detailed skill relevance scoring with explanation"""
    skill_name: str
    base_score: float
    domain_boost: float
    experience_alignment: float
    industry_relevance: float
    semantic_similarity: float
    final_score: float
    explanation: str
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "base_score": self.base_score,
            "domain_boost": self.domain_boost,
            "experience_alignment": self.experience_alignment,
            "industry_relevance": self.industry_relevance,
            "semantic_similarity": self.semantic_similarity,
            "final_score": self.final_score,
            "explanation": self.explanation,
            "confidence": self.confidence
        }


class IndustryClassifier:
    """Advanced industry classification with context awareness"""
    
    def __init__(self):
        self.industry_patterns = {
            "healthcare": {
                "keywords": ["healthcare", "medical", "hospital", "clinic", "patient", "hipaa", "epic", "cerner"],
                "context_indicators": ["patient care", "medical records", "clinical", "pharmaceutical"],
                "tech_stack": ["epic", "cerner", "meditech", "allscripts"]
            },
            "finance": {
                "keywords": ["finance", "banking", "financial", "investment", "trading", "risk", "compliance"],
                "context_indicators": ["financial analysis", "risk management", "regulatory", "trading systems"],
                "tech_stack": ["bloomberg", "reuters", "murex", "calypso", "sap", "oracle financials"]
            },
            "technology": {
                "keywords": ["software", "development", "engineering", "tech", "startup", "saas", "platform"],
                "context_indicators": ["software development", "cloud", "agile", "devops", "microservices"],
                "tech_stack": ["aws", "azure", "kubernetes", "docker", "react", "python"]
            },
            "manufacturing": {
                "keywords": ["manufacturing", "production", "factory", "industrial", "supply chain", "quality"],
                "context_indicators": ["production line", "inventory", "lean manufacturing", "six sigma"],
                "tech_stack": ["sap", "oracle", "mes", "scada", "plm"]
            },
            "education": {
                "keywords": ["education", "university", "school", "academic", "research", "student"],
                "context_indicators": ["curriculum", "learning", "research", "academic"],
                "tech_stack": ["canvas", "blackboard", "moodle", "peoplesoft"]
            },
            "retail": {
                "keywords": ["retail", "ecommerce", "customer", "sales", "marketing", "brand"],
                "context_indicators": ["customer experience", "point of sale", "inventory", "merchandising"],
                "tech_stack": ["salesforce", "shopify", "sap retail", "oracle retail"]
            }
        }
    
    def classify_industry(self, job_description: str) -> Dict[str, Any]:
        """Classify industry with confidence scoring"""
        job_lower = job_description.lower()
        industry_scores = {}
        
        for industry, patterns in self.industry_patterns.items():
            score = 0
            
            # Keyword matching
            for keyword in patterns["keywords"]:
                count = len(re.findall(r'\b' + keyword + r'\b', job_lower))
                score += count * 2
            
            # Context indicator matching
            for indicator in patterns["context_indicators"]:
                if indicator in job_lower:
                    score += 3
            
            # Tech stack matching
            for tech in patterns["tech_stack"]:
                if tech in job_lower:
                    score += 4
            
            if score > 0:
                industry_scores[industry] = score
        
        if not industry_scores:
            return {"industry": "general", "confidence": 0.5, "indicators": []}
        
        # Determine primary industry
        primary_industry = max(industry_scores, key=industry_scores.get)
        max_score = industry_scores[primary_industry]
        total_score = sum(industry_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        return {
            "industry": primary_industry,
            "confidence": confidence,
            "all_scores": industry_scores,
            "indicators": self._get_matching_indicators(job_lower, primary_industry)
        }
    
    def _get_matching_indicators(self, job_text: str, industry: str) -> List[str]:
        """Get specific indicators that matched for this industry"""
        if industry not in self.industry_patterns:
            return []
        
        patterns = self.industry_patterns[industry]
        indicators = []
        
        for keyword in patterns["keywords"]:
            if keyword in job_text:
                indicators.append(f"keyword: {keyword}")
        
        for context in patterns["context_indicators"]:
            if context in job_text:
                indicators.append(f"context: {context}")
        
        for tech in patterns["tech_stack"]:
            if tech in job_text:
                indicators.append(f"technology: {tech}")
        
        return indicators


class SemanticMatcher:
    """Advanced semantic similarity matching for skills and requirements"""
    
    def __init__(self):
        # Pre-computed semantic clusters for common IT/business terms
        self.semantic_clusters = {
            "database_management": [
                "database", "sql", "mysql", "postgresql", "oracle", "mongodb", 
                "data management", "database administration", "dba", "query optimization"
            ],
            "network_administration": [
                "network", "networking", "tcp/ip", "dns", "dhcp", "vpn", "firewall",
                "network security", "lan", "wan", "routing", "switching"
            ],
            "system_administration": [
                "system admin", "server management", "linux", "windows", "unix",
                "server administration", "infrastructure", "system maintenance"
            ],
            "cloud_technologies": [
                "cloud", "aws", "azure", "gcp", "cloud computing", "saas", "paas", "iaas",
                "cloud architecture", "cloud migration", "serverless"
            ],
            "business_analysis": [
                "business analyst", "requirements gathering", "process improvement",
                "business requirements", "stakeholder management", "gap analysis"
            ],
            "project_management": [
                "project management", "project manager", "scrum", "agile", "kanban",
                "project coordination", "timeline management", "resource planning"
            ],
            "data_analysis": [
                "data analysis", "analytics", "reporting", "business intelligence",
                "data visualization", "excel", "pivot tables", "dashboards"
            ]
        }
        
        # Synonym mappings
        self.synonyms = {
            "sys admin": "system administrator",
            "sysadmin": "system administrator",
            "net admin": "network administrator",
            "dba": "database administrator",
            "pm": "project manager",
            "ba": "business analyst",
            "dev": "developer",
            "qa": "quality assurance"
        }
    
    def calculate_semantic_similarity(self, skill: str, requirement: str) -> float:
        """Calculate semantic similarity between skill and requirement"""
        skill_lower = skill.lower().strip()
        requirement_lower = requirement.lower().strip()
        
        # Exact match
        if skill_lower == requirement_lower:
            return 1.0
        
        # Check synonyms
        skill_normalized = self.synonyms.get(skill_lower, skill_lower)
        requirement_normalized = self.synonyms.get(requirement_lower, requirement_lower)
        
        if skill_normalized == requirement_normalized:
            return 0.95
        
        # Substring matching
        if skill_lower in requirement_lower or requirement_lower in skill_lower:
            return 0.8
        
        # Semantic cluster matching
        skill_cluster = self._find_cluster(skill_lower)
        requirement_cluster = self._find_cluster(requirement_lower)
        
        if skill_cluster and requirement_cluster and skill_cluster == requirement_cluster:
            return 0.7
        
        # Token overlap similarity
        skill_tokens = set(re.findall(r'\b\w+\b', skill_lower))
        requirement_tokens = set(re.findall(r'\b\w+\b', requirement_lower))
        
        if skill_tokens and requirement_tokens:
            overlap = len(skill_tokens.intersection(requirement_tokens))
            union = len(skill_tokens.union(requirement_tokens))
            jaccard_similarity = overlap / union if union > 0 else 0
            
            if jaccard_similarity > 0.3:
                return jaccard_similarity * 0.6
        
        return 0.0
    
    def _find_cluster(self, term: str) -> Optional[str]:
        """Find which semantic cluster a term belongs to"""
        for cluster_name, terms in self.semantic_clusters.items():
            for cluster_term in terms:
                if cluster_term in term or term in cluster_term:
                    return cluster_name
        return None


class AdvancedRelevanceEngine:
    """
    Ultra-intelligent job-skill matching system with advanced AI capabilities.
    
    Features:
    - Advanced semantic similarity matching
    - Industry-aware context analysis
    - Dynamic learning from user feedback
    - Multi-dimensional relevance scoring
    - Confidence-based recommendations
    - Performance optimization with caching
    """
    
    def __init__(self, cache_ttl: int = 3600):
        # Core components
        self.industry_classifier = IndustryClassifier()
        self.semantic_matcher = SemanticMatcher()
        
        # Get monitoring and error handling
        self.performance_monitor = get_global_performance_monitor()
        self.error_handler = get_global_error_handler()
        
        # Enhanced domain definitions
        self.tech_domains = {
            "databases": {
                "keywords": ["sql", "mysql", "postgresql", "oracle", "mongodb", "nosql", "database", "db", "data", "query"],
                "weight": 1.0,
                "industry_boost": {"finance": 1.5, "healthcare": 1.3, "retail": 1.2}
            },
            "programming": {
                "keywords": ["python", "java", "c++", "javascript", "nodejs", "php", "ruby", "go", "rust", ".net"],
                "weight": 1.2,
                "industry_boost": {"technology": 1.8, "finance": 1.3}
            },
            "web": {
                "keywords": ["html", "css", "react", "angular", "vue", "frontend", "backend", "web", "http", "api", "rest"],
                "weight": 1.1,
                "industry_boost": {"technology": 1.6, "retail": 1.4}
            },
            "cloud": {
                "keywords": ["aws", "azure", "gcp", "cloud", "docker", "kubernetes", "serverless", "microservices"],
                "weight": 1.3,
                "industry_boost": {"technology": 1.7, "finance": 1.4}
            },
            "networking": {
                "keywords": ["network", "tcp", "ip", "dns", "firewall", "vpn", "router", "switch", "security"],
                "weight": 1.2,
                "industry_boost": {"technology": 1.5, "healthcare": 1.3}
            },
            "systems": {
                "keywords": ["linux", "windows", "unix", "server", "admin", "infrastructure", "deployment"],
                "weight": 1.1,
                "industry_boost": {"technology": 1.4, "manufacturing": 1.3}
            },
            "security": {
                "keywords": ["security", "cybersecurity", "encryption", "authentication", "authorization", "compliance"],
                "weight": 1.4,
                "industry_boost": {"finance": 1.8, "healthcare": 1.6}
            },
            "automation": {
                "keywords": ["automation", "scripting", "powershell", "bash", "workflow", "ci/cd", "devops"],
                "weight": 1.2,
                "industry_boost": {"technology": 1.6, "manufacturing": 1.4}
            }
        }
        
        self.business_domains = {
            "business_analysis": {
                "keywords": ["business analyst", "requirements", "process improvement", "workflow", "documentation"],
                "weight": 1.0,
                "industry_boost": {"finance": 1.4, "healthcare": 1.3}
            },
            "finance": {
                "keywords": ["finance", "financial", "accounting", "order to cash", "collections", "credit"],
                "weight": 1.1,
                "industry_boost": {"finance": 1.8, "manufacturing": 1.2}
            },
            "project_management": {
                "keywords": ["project management", "scrum", "agile", "stakeholder management", "timeline"],
                "weight": 1.2,
                "industry_boost": {"technology": 1.5, "manufacturing": 1.4}
            },
            "business_intelligence": {
                "keywords": ["business intelligence", "bi", "power bi", "tableau", "data visualization", "dashboard"],
                "weight": 1.3,
                "industry_boost": {"finance": 1.6, "retail": 1.4}
            }
        }
        
        # Role classification with enhanced patterns
        self.role_types = {
            "technical_it": {
                "patterns": ["technician", "engineer", "developer", "administrator", "support specialist", 
                           "network", "system admin", "security analyst", "devops", "infrastructure"],
                "weight": 1.0,
                "complexity_indicators": ["senior", "lead", "principal", "architect"]
            },
            "business_analyst": {
                "patterns": ["business analyst", "process analyst", "functional analyst", "systems analyst"],
                "weight": 1.0,
                "complexity_indicators": ["senior", "lead", "principal"]
            },
            "management": {
                "patterns": ["manager", "director", "supervisor", "team lead", "department head"],
                "weight": 1.0,
                "complexity_indicators": ["senior", "executive", "vice president", "c-level"]
            }
        }
        
        # Caching for performance
        self.analysis_cache = {}
        self.cache_ttl = cache_ttl
        
        # Learning system
        self.feedback_patterns = defaultdict(list)
        self.skill_performance_history = defaultdict(list)
    
    @performance_monitor(get_global_performance_monitor(), "relevance_engine", "analyze_job_comprehensive", use_cache=True, cache_ttl=3600)
    @with_error_handling(get_global_error_handler(), "relevance_engine", "analyze_job_comprehensive")
    def analyze_job_comprehensive(self, job_description: str) -> JobAnalysisResult:
        """
        Perform comprehensive job analysis with advanced AI techniques
        """
        
        # Create cache key
        cache_key = hashlib.md5(job_description.encode()).hexdigest()
        
        # Check cache
        if cache_key in self.analysis_cache:
            cached_result, timestamp = self.analysis_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return JobAnalysisResult(**cached_result)
        
        job_lower = job_description.lower()
        
        # Industry classification
        industry_analysis = self.industry_classifier.classify_industry(job_description)
        
        # Role type classification with confidence
        role_analysis = self._classify_role_advanced(job_lower)
        
        # Extract skills and requirements
        skills_analysis = self._extract_skills_advanced(job_lower)
        
        # Analyze company context
        company_analysis = self._analyze_company_context(job_lower)
        
        # Determine experience level and complexity
        experience_analysis = self._analyze_experience_requirements(job_lower)
        
        # Analyze compensation and growth indicators
        career_analysis = self._analyze_career_indicators(job_lower)
        
        # Score domains with industry context
        tech_domains = self._score_domains_advanced(job_lower, self.tech_domains, industry_analysis)
        business_domains = self._score_domains_advanced(job_lower, self.business_domains, industry_analysis)
        
        # Determine primary focus
        tech_score = sum(tech_domains.values())
        business_score = sum(business_domains.values())
        
        if role_analysis["role_type"] in ["business_analyst", "management"]:
            primary_focus = "business"
        elif role_analysis["role_type"] == "technical_it":
            primary_focus = "technical"
        else:
            primary_focus = "business" if business_score > tech_score else "technical"
        
        # Create comprehensive result
        result = JobAnalysisResult(
            job_role_type=role_analysis["role_type"],
            primary_focus=primary_focus,
            confidence_score=role_analysis["confidence"],
            required_skills=skills_analysis["required"],
            preferred_skills=skills_analysis["preferred"],
            tech_domains=tech_domains,
            business_domains=business_domains,
            industry_context=industry_analysis,
            experience_level=experience_analysis["level"],
            company_size=company_analysis["size"],
            role_complexity=experience_analysis["complexity"],
            explicit_technologies=skills_analysis["technologies"],
            soft_skills=skills_analysis["soft_skills"],
            key_responsibilities=skills_analysis["responsibilities"],
            compensation_indicators=career_analysis["compensation"],
            growth_potential=career_analysis["growth_potential"],
            remote_work_indicators=career_analysis["remote_indicators"]
        )
        
        # Cache result
        self.analysis_cache[cache_key] = (result.to_dict(), datetime.now())
        
        return result
    
    def _classify_role_advanced(self, job_text: str) -> Dict[str, Any]:
        """Advanced role classification with confidence scoring"""
        role_scores = {}
        
        for role_type, config in self.role_types.items():
            score = 0
            
            # Pattern matching with position weighting
            for pattern in config["patterns"]:
                matches = len(re.findall(r'\b' + pattern + r'\b', job_text))
                score += matches
                
                # Higher weight for title matches (first 200 chars)
                if pattern in job_text[:200]:
                    score += 3
            
            # Complexity indicators
            for indicator in config["complexity_indicators"]:
                if indicator in job_text:
                    score += 2
            
            if score > 0:
                role_scores[role_type] = score
        
        if not role_scores:
            return {"role_type": "unknown", "confidence": 0.0}
        
        # Calculate confidence based on score distribution
        max_score = max(role_scores.values())
        total_score = sum(role_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        return {
            "role_type": max(role_scores, key=role_scores.get),
            "confidence": confidence,
            "all_scores": role_scores
        }
    
    def _extract_skills_advanced(self, job_text: str) -> Dict[str, List[str]]:
        """Advanced skill extraction with categorization"""
        
        # Required skills patterns
        required_patterns = [
            r"required?:?\s*([^.!?]*)",
            r"must have:?\s*([^.!?]*)",
            r"essential:?\s*([^.!?]*)",
            r"minimum requirements?:?\s*([^.!?]*)",
            r"qualifications?:?\s*([^.!?]*)"
        ]
        
        # Preferred skills patterns
        preferred_patterns = [
            r"preferred?:?\s*([^.!?]*)",
            r"nice to have:?\s*([^.!?]*)",
            r"bonus:?\s*([^.!?]*)",
            r"plus:?\s*([^.!?]*)",
            r"desired:?\s*([^.!?]*)"
        ]
        
        # Extract technologies
        tech_patterns = [
            r"\b(?:java|python|javascript|sql|aws|azure|linux|windows|oracle|mysql)\b",
            r"\b(?:react|angular|vue|docker|kubernetes|git|jenkins)\b"
        ]
        
        # Extract soft skills
        soft_skill_patterns = [
            r"communication", r"leadership", r"teamwork", r"problem.solving",
            r"analytical", r"detail.oriented", r"time.management", r"adaptability"
        ]
        
        # Extract responsibilities
        responsibility_patterns = [
            r"responsibilities?:?\s*([^.!?]*)",
            r"duties:?\s*([^.!?]*)",
            r"you will:?\s*([^.!?]*)",
            r"the role involves:?\s*([^.!?]*)"
        ]
        
        required_skills = []
        preferred_skills = []
        technologies = []
        soft_skills = []
        responsibilities = []
        
        # Extract each category
        for pattern in required_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            required_skills.extend([match.strip() for match in matches])
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            preferred_skills.extend([match.strip() for match in matches])
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            technologies.extend(matches)
        
        for pattern in soft_skill_patterns:
            if re.search(pattern, job_text, re.IGNORECASE):
                soft_skills.append(pattern.replace(".", " "))
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            responsibilities.extend([match.strip() for match in matches])
        
        return {
            "required": required_skills,
            "preferred": preferred_skills,
            "technologies": list(set(technologies)),
            "soft_skills": soft_skills,
            "responsibilities": responsibilities
        }
    
    def _analyze_company_context(self, job_text: str) -> Dict[str, Any]:
        """Analyze company size and context indicators"""
        
        # Company size indicators
        large_company_indicators = [
            "enterprise", "fortune 500", "global", "multinational", "corporation",
            "thousands of employees", "worldwide", "international"
        ]
        
        small_company_indicators = [
            "startup", "small business", "growing company", "entrepreneurial",
            "close-knit team", "wear many hats", "fast-paced"
        ]
        
        large_score = sum(1 for indicator in large_company_indicators if indicator in job_text)
        small_score = sum(1 for indicator in small_company_indicators if indicator in job_text)
        
        if large_score > small_score:
            company_size = "large"
        elif small_score > large_score:
            company_size = "small"
        else:
            company_size = "medium"
        
        return {
            "size": company_size,
            "large_indicators": large_score,
            "small_indicators": small_score
        }
    
    def _analyze_experience_requirements(self, job_text: str) -> Dict[str, Any]:
        """Analyze experience level and role complexity"""
        
        # Experience level indicators
        senior_indicators = ["senior", "lead", "principal", "architect", "5+ years", "7+ years"]
        junior_indicators = ["junior", "entry", "associate", "0-2 years", "recent graduate"]
        
        senior_score = sum(1 for indicator in senior_indicators if indicator in job_text)
        junior_score = sum(1 for indicator in junior_indicators if indicator in job_text)
        
        if senior_score > junior_score:
            experience_level = "senior"
            complexity = 0.8
        elif junior_score > senior_score:
            experience_level = "junior"
            complexity = 0.3
        else:
            experience_level = "mid"
            complexity = 0.5
        
        # Adjust complexity based on responsibilities
        complex_responsibilities = [
            "architect", "design", "lead", "mentor", "strategy", "planning",
            "cross-functional", "stakeholder management"
        ]
        
        complexity_boost = sum(0.1 for resp in complex_responsibilities if resp in job_text)
        complexity = min(1.0, complexity + complexity_boost)
        
        return {
            "level": experience_level,
            "complexity": complexity,
            "senior_indicators": senior_score,
            "junior_indicators": junior_score
        }
    
    def _analyze_career_indicators(self, job_text: str) -> Dict[str, Any]:
        """Analyze compensation and growth potential indicators"""
        
        # Compensation indicators
        high_comp_indicators = [
            "competitive salary", "excellent benefits", "equity", "stock options",
            "bonus", "401k", "health insurance", "remote work"
        ]
        
        # Growth indicators
        growth_indicators = [
            "career growth", "advancement", "mentorship", "learning", "development",
            "training", "certification", "conference", "education"
        ]
        
        # Remote work indicators
        remote_indicators = [
            "remote", "work from home", "distributed team", "flexible location",
            "telecommute", "virtual", "anywhere"
        ]
        
        comp_score = sum(1 for indicator in high_comp_indicators if indicator in job_text)
        growth_score = sum(1 for indicator in growth_indicators if indicator in job_text)
        remote_matches = [indicator for indicator in remote_indicators if indicator in job_text]
        
        return {
            "compensation": {
                "indicators": comp_score,
                "likely_competitive": comp_score >= 3
            },
            "growth_potential": min(1.0, growth_score / 5),
            "remote_indicators": remote_matches
        }
    
    def _score_domains_advanced(self, job_text: str, domains: Dict, industry_analysis: Dict) -> Dict[str, float]:
        """Score domains with industry context and weighting"""
        
        domain_scores = {}
        industry = industry_analysis.get("industry", "general")
        
        for domain, config in domains.items():
            score = 0
            
            # Base keyword scoring
            for keyword in config["keywords"]:
                count = len(re.findall(r'\b' + keyword + r'\b', job_text))
                score += count * config["weight"]
            
            # Apply industry boost
            if industry in config.get("industry_boost", {}):
                score *= config["industry_boost"][industry]
            
            if score > 0:
                domain_scores[domain] = score
        
        return domain_scores
    
    @performance_monitor(get_global_performance_monitor(), "relevance_engine", "score_skill_comprehensive", use_cache=True)
    def score_skill_comprehensive(self, skill_data: Dict, job_analysis: JobAnalysisResult) -> SkillRelevanceScore:
        """
        Comprehensive skill relevance scoring with multi-dimensional analysis
        """
        
        skill_name = skill_data['skill_name'].lower()
        skill_context = skill_data.get('context', '').lower()
        
        # Base scoring components
        base_score = 0.0
        domain_boost = 0.0
        experience_alignment = 0.0
        industry_relevance = 0.0
        semantic_similarity = 0.0
        
        # 1. Direct requirement matching
        for required_skill in job_analysis.required_skills:
            similarity = self.semantic_matcher.calculate_semantic_similarity(skill_name, required_skill.lower())
            base_score = max(base_score, similarity * 0.9)
        
        for preferred_skill in job_analysis.preferred_skills:
            similarity = self.semantic_matcher.calculate_semantic_similarity(skill_name, preferred_skill.lower())
            base_score = max(base_score, similarity * 0.6)
        
        # 2. Domain relevance with focus-based weighting
        if job_analysis.primary_focus == "technical":
            for domain, score in job_analysis.tech_domains.items():
                domain_config = self.tech_domains.get(domain, {})
                for keyword in domain_config.get("keywords", []):
                    if keyword in skill_name or keyword in skill_context:
                        domain_boost += min(score / 15.0, 0.8) * domain_config.get("weight", 1.0)
        
        elif job_analysis.primary_focus == "business":
            for domain, score in job_analysis.business_domains.items():
                domain_config = self.business_domains.get(domain, {})
                for keyword in domain_config.get("keywords", []):
                    if keyword in skill_name or keyword in skill_context:
                        domain_boost += min(score / 10.0, 0.8) * domain_config.get("weight", 1.0)
        
        # 3. Experience level alignment
        if job_analysis.experience_level == "senior" and "senior" in skill_context:
            experience_alignment = 0.2
        elif job_analysis.experience_level == "junior" and any(term in skill_context for term in ["basic", "entry", "beginner"]):
            experience_alignment = 0.1
        elif job_analysis.experience_level == "mid":
            experience_alignment = 0.1
        
        # 4. Industry relevance boost
        industry = job_analysis.industry_context.get("industry", "general")
        if industry != "general":
            # Check if skill is particularly relevant to this industry
            if job_analysis.primary_focus == "technical":
                for domain, config in self.tech_domains.items():
                    if industry in config.get("industry_boost", {}):
                        for keyword in config["keywords"]:
                            if keyword in skill_name:
                                industry_relevance = 0.15 * (config["industry_boost"][industry] - 1.0)
                                break
            else:
                for domain, config in self.business_domains.items():
                    if industry in config.get("industry_boost", {}):
                        for keyword in config["keywords"]:
                            if keyword in skill_name:
                                industry_relevance = 0.15 * (config["industry_boost"][industry] - 1.0)
                                break
        
        # 5. Semantic similarity with explicit technologies
        for tech in job_analysis.explicit_technologies:
            similarity = self.semantic_matcher.calculate_semantic_similarity(skill_name, tech)
            semantic_similarity = max(semantic_similarity, similarity * 0.3)
        
        # 6. Role-specific penalties for mismatched skills
        penalty = 0.0
        if job_analysis.primary_focus == "business":
            # Penalize pure technical skills for business roles
            technical_only_terms = ["network security", "server administration", "hardware troubleshooting"]
            if any(term in skill_name for term in technical_only_terms):
                penalty = 0.4
        
        # Calculate final score
        final_score = (base_score + domain_boost + experience_alignment + 
                      industry_relevance + semantic_similarity) - penalty
        final_score = max(0.0, min(1.0, final_score))
        
        # Generate explanation
        explanation = self._generate_score_explanation(
            skill_name, base_score, domain_boost, experience_alignment, 
            industry_relevance, semantic_similarity, penalty, job_analysis
        )
        
        # Calculate confidence based on score components
        confidence = self._calculate_confidence(base_score, domain_boost, semantic_similarity)
        
        return SkillRelevanceScore(
            skill_name=skill_data['skill_name'],
            base_score=base_score,
            domain_boost=domain_boost,
            experience_alignment=experience_alignment,
            industry_relevance=industry_relevance,
            semantic_similarity=semantic_similarity,
            final_score=final_score,
            explanation=explanation,
            confidence=confidence
        )
    
    def _generate_score_explanation(self, skill_name: str, base_score: float, 
                                  domain_boost: float, experience_alignment: float,
                                  industry_relevance: float, semantic_similarity: float, 
                                  penalty: float, job_analysis: JobAnalysisResult) -> str:
        """Generate human-readable explanation for the score"""
        
        explanations = []
        
        if base_score > 0.7:
            explanations.append("Strong match with job requirements")
        elif base_score > 0.4:
            explanations.append("Moderate match with job requirements")
        elif base_score > 0.1:
            explanations.append("Weak match with job requirements")
        
        if domain_boost > 0.5:
            explanations.append(f"High relevance to {job_analysis.primary_focus} role")
        elif domain_boost > 0.2:
            explanations.append(f"Moderate relevance to {job_analysis.primary_focus} role")
        
        if industry_relevance > 0.1:
            industry = job_analysis.industry_context.get("industry", "general")
            explanations.append(f"Valuable for {industry} industry")
        
        if semantic_similarity > 0.2:
            explanations.append("Semantic similarity with mentioned technologies")
        
        if penalty > 0:
            explanations.append("Some mismatch with role focus")
        
        return "; ".join(explanations) if explanations else "Basic relevance assessment"
    
    def _calculate_confidence(self, base_score: float, domain_boost: float, semantic_similarity: float) -> float:
        """Calculate confidence in the relevance score"""
        
        # High confidence if we have strong direct matches
        if base_score > 0.8:
            return 0.95
        
        # Medium-high confidence with good domain relevance
        if base_score > 0.5 or domain_boost > 0.6:
            return 0.8
        
        # Medium confidence with some indicators
        if base_score > 0.2 or domain_boost > 0.3 or semantic_similarity > 0.3:
            return 0.6
        
        # Low confidence
        return 0.4
    
    def learn_from_feedback(self, skill_name: str, job_description: str, 
                          feedback_type: str, user_score: Optional[float] = None):
        """Learn from user feedback to improve future scoring"""
        
        # Store feedback pattern
        feedback_entry = {
            "skill": skill_name.lower(),
            "job_context": job_description[:200].lower(),  # First 200 chars for context
            "feedback_type": feedback_type,  # "positive", "negative", "neutral"
            "user_score": user_score,
            "timestamp": datetime.now()
        }
        
        self.feedback_patterns[skill_name.lower()].append(feedback_entry)
        
        # Update skill performance history
        if user_score is not None:
            self.skill_performance_history[skill_name.lower()].append({
                "score": user_score,
                "timestamp": datetime.now(),
                "context": job_description[:100].lower()
            })
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from the learning system"""
        
        insights = {
            "total_feedback_entries": sum(len(patterns) for patterns in self.feedback_patterns.values()),
            "skills_with_feedback": len(self.feedback_patterns),
            "top_performing_skills": [],
            "underperforming_skills": [],
            "feedback_trends": {}
        }
        
        # Analyze skill performance
        for skill, history in self.skill_performance_history.items():
            if len(history) >= 3:
                avg_score = sum(entry["score"] for entry in history) / len(history)
                
                if avg_score > 0.8:
                    insights["top_performing_skills"].append({
                        "skill": skill,
                        "avg_score": avg_score,
                        "feedback_count": len(history)
                    })
                elif avg_score < 0.4:
                    insights["underperforming_skills"].append({
                        "skill": skill,
                        "avg_score": avg_score,
                        "feedback_count": len(history)
                    })
        
        # Analyze feedback trends
        positive_feedback = sum(1 for patterns in self.feedback_patterns.values() 
                               for entry in patterns if entry["feedback_type"] == "positive")
        negative_feedback = sum(1 for patterns in self.feedback_patterns.values() 
                               for entry in patterns if entry["feedback_type"] == "negative")
        
        insights["feedback_trends"] = {
            "positive_ratio": positive_feedback / (positive_feedback + negative_feedback) if (positive_feedback + negative_feedback) > 0 else 0,
            "total_positive": positive_feedback,
            "total_negative": negative_feedback
        }
        
        return insights
    
    def clear_cache(self):
        """Clear analysis cache"""
        self.analysis_cache.clear()
    
    def export_learning_data(self, filepath: str):
        """Export learning data for analysis"""
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "feedback_patterns": {
                skill: [
                    {**entry, "timestamp": entry["timestamp"].isoformat()}
                    for entry in patterns
                ]
                for skill, patterns in self.feedback_patterns.items()
            },
            "skill_performance_history": {
                skill: [
                    {**entry, "timestamp": entry["timestamp"].isoformat()}
                    for entry in history
                ]
                for skill, history in self.skill_performance_history.items()
            },
            "learning_insights": self.get_learning_insights()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)


# Global instance for backwards compatibility
_global_advanced_relevance_engine = None

def get_global_advanced_relevance_engine() -> AdvancedRelevanceEngine:
    """Get the global advanced relevance engine instance"""
    global _global_advanced_relevance_engine
    if _global_advanced_relevance_engine is None:
        _global_advanced_relevance_engine = AdvancedRelevanceEngine()
    return _global_advanced_relevance_engine
