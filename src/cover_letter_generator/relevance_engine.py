"""
Relevance Engine - Intelligent Memory Selection Based on Job Requirements
Analyzes job descriptions and scores memory items for relevance like a human would
"""

import re
import json
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
from datetime import datetime

class RelevanceEngine:
    """Intelligent system for selecting relevant memories based on job context"""
    
    def __init__(self):
        # Technical domains and their related keywords
        self.tech_domains = {
            "databases": ["sql", "mysql", "postgresql", "oracle", "mongodb", "nosql", "database", "db", "data", "query"],
            "programming": ["python", "java", "c++", "javascript", "nodejs", "php", "ruby", "go", "rust", ".net"],
            "web": ["html", "css", "react", "angular", "vue", "frontend", "backend", "web", "http", "api", "rest"],
            "cloud": ["aws", "azure", "gcp", "cloud", "docker", "kubernetes", "serverless", "microservices"],
            "networking": ["network", "tcp", "ip", "dns", "firewall", "vpn", "router", "switch", "security"],
            "systems": ["linux", "windows", "unix", "server", "admin", "infrastructure", "deployment"],
            "data": ["analytics", "visualization", "reporting", "bi", "etl", "data mining", "statistics"],
            "security": ["security", "cybersecurity", "encryption", "authentication", "authorization", "compliance"],
            "automation": ["automation", "scripting", "powershell", "bash", "workflow", "ci/cd", "devops"],
            "support": ["helpdesk", "support", "troubleshooting", "customer service", "technical support"]
        }
        
        # Business domains for analyst/finance/process roles
        self.business_domains = {
            "business_analysis": ["business analyst", "process analyst", "systems analyst", "business analysis", "requirements", "process improvement", "workflow", "documentation"],
            "finance": ["finance", "financial", "accounting", "order to cash", "otc", "cash application", "collections", "credit", "deductions", "ap", "ar", "gl", "revenue"],
            "process_improvement": ["process improvement", "lean", "six sigma", "process optimization", "efficiency", "streamline", "process redesign", "continuous improvement"],
            "project_management": ["project management", "project manager", "project coordination", "stakeholder management", "timeline", "deliverables", "milestones"],
            "business_intelligence": ["business intelligence", "bi", "power bi", "tableau", "data visualization", "dashboard", "reporting", "analytics", "insights"],
            "erp_systems": ["sap", "oracle", "erp", "enterprise systems", "crm", "salesforce", "workday", "peoplesoft"],
            "rpa_automation": ["rpa", "robotic process automation", "uipath", "automation anywhere", "blue prism", "process automation"],
            "change_management": ["change management", "training", "user adoption", "stakeholder engagement", "communication", "transformation"],
            "data_analysis": ["data analysis", "excel", "pivot tables", "vlookup", "data modeling", "statistical analysis", "metrics"]
        }
        
        # Job role classification patterns
        self.role_types = {
            "technical_it": ["technician", "engineer", "developer", "administrator", "support specialist", "network", "system admin", "it specialist", 
                            "security analyst", "identity analyst", "access analyst", "iam analyst", "technical analyst", "it analyst", "systems analyst"],
            "business_analyst": ["business analyst", "process analyst", "functional analyst", "process development analyst", "business systems analyst"],
            "finance": ["accountant", "financial analyst", "controller", "finance manager", "accounts payable", "accounts receivable"],
            "project_management": ["project manager", "program manager", "scrum master", "project coordinator"],
            "management": ["manager", "director", "supervisor", "team lead", "department head"]
        }
        
        # Cache for job analysis to avoid re-processing
        self.job_analysis_cache = {}
        
    def analyze_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description and extract requirements based on job role type"""
        
        # Create cache key
        cache_key = hash(job_description.lower().strip())
        if cache_key in self.job_analysis_cache:
            return self.job_analysis_cache[cache_key]
        
        job_lower = job_description.lower()
        
        analysis = {
            "required_skills": [],
            "preferred_skills": [],
            "tech_domains": defaultdict(float),
            "business_domains": defaultdict(float),
            "experience_level": "mid",
            "key_responsibilities": [],
            "company_focus": "",
            "explicit_technologies": [],
            "job_role_type": "unknown",
            "primary_focus": "unknown"
        }
        
        # STEP 1: Classify the job role type
        analysis["job_role_type"] = self._classify_job_role(job_lower)
        
        # STEP 2: Analyze domains based on role type
        if analysis["job_role_type"] in ["business_analyst", "finance", "project_management"]:
            # Business-focused analysis
            analysis["primary_focus"] = "business"
            self._analyze_business_requirements(job_lower, analysis)
        elif analysis["job_role_type"] == "technical_it":
            # Technical IT analysis
            analysis["primary_focus"] = "technical"
            self._analyze_technical_requirements(job_lower, analysis)
        else:
            # Mixed or unknown - analyze both but prioritize based on content
            business_score = self._score_business_content(job_lower)
            technical_score = self._score_technical_content(job_lower)
            
            if business_score > technical_score:
                analysis["primary_focus"] = "business"
                self._analyze_business_requirements(job_lower, analysis)
                self._analyze_technical_requirements(job_lower, analysis, weight=0.3)  # Lower weight
            else:
                analysis["primary_focus"] = "technical"
                self._analyze_technical_requirements(job_lower, analysis)
                self._analyze_business_requirements(job_lower, analysis, weight=0.3)  # Lower weight
        
        # Extract required vs preferred skills (applies to all role types)
        required_patterns = [
            r"required?:?\s*([^.]*)",
            r"must have:?\s*([^.]*)",
            r"essential:?\s*([^.]*)",
            r"minimum requirements?:?\s*([^.]*)",
            r"qualifications?:?\s*([^.]*)"
        ]
        
        preferred_patterns = [
            r"preferred?:?\s*([^.]*)",
            r"nice to have:?\s*([^.]*)",
            r"bonus:?\s*([^.]*)",
            r"plus:?\s*([^.]*)",
            r"desired:?\s*([^.]*)"
        ]
        
        # Extract required skills
        for pattern in required_patterns:
            matches = re.findall(pattern, job_lower, re.IGNORECASE)
            for match in matches:
                analysis["required_skills"].extend(self._extract_all_terms(match))
        
        # Extract preferred skills
        for pattern in preferred_patterns:
            matches = re.findall(pattern, job_lower, re.IGNORECASE)
            for match in matches:
                analysis["preferred_skills"].extend(self._extract_all_terms(match))
        
        # Determine experience level
        if any(term in job_lower for term in ["senior", "lead", "principal", "architect"]):
            analysis["experience_level"] = "senior"
        elif any(term in job_lower for term in ["junior", "entry", "associate", "1-2 years"]):
            analysis["experience_level"] = "junior"
        
        # Extract key responsibilities (for context matching)
        responsibility_patterns = [
            r"responsibilities?:?\s*([^.]*)",
            r"duties:?\s*([^.]*)",
            r"you will:?\s*([^.]*)"
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, job_lower, re.IGNORECASE)
            analysis["key_responsibilities"].extend(matches)
        
        # Cache the analysis
        self.job_analysis_cache[cache_key] = analysis
        return analysis
    
    def _classify_job_role(self, job_lower: str) -> str:
        """Classify the job role type based on title and description"""
        
        # Check each role type against the job description
        role_scores = {}
        
        for role_type, patterns in self.role_types.items():
            score = 0
            for pattern in patterns:
                # Count matches in job description
                score += len(re.findall(r'\b' + pattern + r'\b', job_lower))
                # Higher weight for matches in title area (first 200 chars)
                if pattern in job_lower[:200]:
                    score += 3
            role_scores[role_type] = score
        
        # Context-based adjustments for better classification
        technical_context_indicators = [
            "active directory", "powershell", "server", "network", "windows", "linux", 
            "infrastructure", "security", "authentication", "user accounts", "provisioning",
            "system administration", "it professional", "technical", "hardware", "software"
        ]
        
        business_context_indicators = [
            "process improvement", "business requirements", "stakeholder", "workflow", 
            "order to cash", "otc", "collections", "finance", "accounting", "rpa", 
            "business intelligence", "transformation", "change management", "business case"
        ]
        
        technical_context_count = sum(1 for indicator in technical_context_indicators if indicator in job_lower)
        business_context_count = sum(1 for indicator in business_context_indicators if indicator in job_lower)
        
        # Adjust scores based on context
        if technical_context_count > business_context_count + 2:
            role_scores["technical_it"] += technical_context_count * 2
        elif business_context_count > technical_context_count + 2:
            role_scores["business_analyst"] += business_context_count * 2
        
        # Special case: If "analyst" appears but in technical context, prefer technical_it
        if "analyst" in job_lower and technical_context_count >= 3:
            role_scores["technical_it"] += 5
        
        # Return the role type with highest score, or 'unknown' if all scores are 0
        if max(role_scores.values()) > 0:
            return max(role_scores, key=role_scores.get)
        return "unknown"
    
    def _score_business_content(self, job_lower: str) -> float:
        """Score how business-focused the job content is"""
        score = 0
        for domain, keywords in self.business_domains.items():
            for keyword in keywords:
                score += len(re.findall(r'\b' + keyword + r'\b', job_lower))
        return score
    
    def _score_technical_content(self, job_lower: str) -> float:
        """Score how technical the job content is"""
        score = 0
        for domain, keywords in self.tech_domains.items():
            for keyword in keywords:
                score += len(re.findall(r'\b' + keyword + r'\b', job_lower))
        return score
    
    def _analyze_business_requirements(self, job_lower: str, analysis: dict, weight: float = 1.0):
        """Analyze business requirements and score business domains"""
        
        # Score business domains based on frequency and context
        for domain, keywords in self.business_domains.items():
            domain_score = 0
            for keyword in keywords:
                count = len(re.findall(r'\b' + keyword + r'\b', job_lower))
                domain_score += count * weight
            
            if domain_score > 0:
                analysis["business_domains"][domain] = domain_score
    
    def _analyze_technical_requirements(self, job_lower: str, analysis: dict, weight: float = 1.0):
        """Analyze technical requirements and score technical domains"""
        
        # Score technical domains based on frequency and context
        for domain, keywords in self.tech_domains.items():
            domain_score = 0
            for keyword in keywords:
                count = len(re.findall(r'\b' + keyword + r'\b', job_lower))
                domain_score += count * weight
            
            if domain_score > 0:
                analysis["tech_domains"][domain] = domain_score
    
    def _extract_all_terms(self, text: str) -> List[str]:
        """Extract both technical and business terms from text"""
        terms = []
        text_lower = text.lower()
        
        # Extract technical terms
        for domain, keywords in self.tech_domains.items():
            for keyword in keywords:
                if keyword in text_lower:
                    terms.append(keyword)
        
        # Extract business terms  
        for domain, keywords in self.business_domains.items():
            for keyword in keywords:
                if keyword in text_lower:
                    terms.append(keyword)
        
        return list(set(terms))
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        # Common technical terms and patterns
        tech_terms = []
        text_lower = text.lower()
        
        # Extract specific technologies mentioned
        for domain, keywords in self.tech_domains.items():
            for keyword in keywords:
                if keyword in text_lower:
                    tech_terms.append(keyword)
        
        return list(set(tech_terms))
    
    def score_skill_relevance(self, skill_data: Dict, job_analysis: Dict[str, Any]) -> float:
        """Score a skill's relevance to the job based on role type (0.0 to 1.0)"""
        score = 0.0
        skill_name = skill_data['skill_name'].lower()
        skill_context = skill_data.get('context', '').lower()
        
        job_role_type = job_analysis.get("job_role_type", "unknown")
        primary_focus = job_analysis.get("primary_focus", "unknown")
        
        # Direct match with required skills (highest priority for all roles)
        for required_skill in job_analysis["required_skills"]:
            if required_skill in skill_name or required_skill in skill_context:
                score += 0.8
        
        # Match with preferred skills
        for preferred_skill in job_analysis["preferred_skills"]:
            if preferred_skill in skill_name or preferred_skill in skill_context:
                score += 0.5
        
        # Role-specific scoring based on primary focus
        if primary_focus == "business":
            score += self._score_business_skill(skill_name, skill_context, job_analysis)
        elif primary_focus == "technical":
            score += self._score_technical_skill(skill_name, skill_context, job_analysis)
        else:
            # Mixed role - score both but with lower weights
            score += self._score_business_skill(skill_name, skill_context, job_analysis) * 0.6
            score += self._score_technical_skill(skill_name, skill_context, job_analysis) * 0.6
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _score_business_skill(self, skill_name: str, skill_context: str, job_analysis: Dict[str, Any]) -> float:
        """Score business-related skills for business roles"""
        score = 0.0
        
        # Business domain matching
        for domain, domain_score in job_analysis.get("business_domains", {}).items():
            domain_keywords = self.business_domains[domain]
            for keyword in domain_keywords:
                if keyword in skill_name or keyword in skill_context:
                    # Higher scores for business skills in business roles
                    domain_weight = min(domain_score / 10.0, 0.8)  # Max 0.8 for business matches
                    score += domain_weight
        
        # Penalize purely technical skills for business roles (unless they're business-technical)
        technical_only_terms = ["technical support", "network security", "windows administration", "hardware"]
        business_technical_terms = ["data analysis", "sql", "database", "automation", "reporting", "excel", "power bi"]
        
        is_technical_only = any(term in skill_name for term in technical_only_terms)
        is_business_technical = any(term in skill_name for term in business_technical_terms)
        
        if is_technical_only and not is_business_technical:
            score = max(score - 0.6, 0.1)  # Penalize pure technical skills for business roles
        
        return score
    
    def _score_technical_skill(self, skill_name: str, skill_context: str, job_analysis: Dict[str, Any]) -> float:
        """Score technical skills for technical roles"""
        score = 0.0
        
        # Technical domain matching
        for domain, domain_score in job_analysis.get("tech_domains", {}).items():
            domain_keywords = self.tech_domains[domain]
            for keyword in domain_keywords:
                if keyword in skill_name or keyword in skill_context:
                    # Higher scores for technical skills in technical roles
                    domain_weight = min(domain_score / 10.0, 0.8)  # Max 0.8 for technical matches
                    score += domain_weight
        
        # Special scoring for specific technical role types
        job_role_type = job_analysis.get("job_role_type", "unknown")
        
        if job_role_type == "technical_it":
            # Boost relevant technical skills
            if any(term in skill_name for term in ["network", "security", "system", "server", "administration"]):
                score += 0.7
            if any(term in skill_name for term in ["active directory", "powershell", "windows", "linux"]):
                score += 0.6
            if "technical support" in skill_name:
                score += 0.4  # Lower but still relevant for IT roles
        
        return score
    
    def score_style_relevance(self, style_data: Dict, job_analysis: Dict[str, Any]) -> float:
        """Score style preference relevance to job context"""
        # Style preferences are generally applicable, but some may be more relevant
        base_score = 0.7  # Most style preferences are relevant
        
        rule = style_data.get('rule', '').lower()
        
        # Higher relevance for communication-heavy roles
        if any(term in job_analysis.get("key_responsibilities", []) 
               for term in ["communicate", "present", "write", "document"]):
            if any(term in rule for term in ["tone", "communication", "writing"]):
                base_score = 0.9
        
        return base_score
    
    def get_relevant_memories(self, memory_core, job_description: str, max_skills: int = 15, max_styles: int = 5) -> Dict[str, Any]:
        """Get the most relevant memories for a specific job"""
        
        # Analyze the job
        job_analysis = self.analyze_job_requirements(job_description)
        
        # Score and filter skills
        skills = memory_core.get_current_skills()
        scored_skills = []
        
        for skill_key, skill_data in skills.items():
            relevance_score = self.score_skill_relevance(skill_data, job_analysis)
            if relevance_score > 0.1:  # Lower threshold to capture more relevant skills
                scored_skills.append((skill_data, relevance_score))
        
        # Sort by relevance and take top N
        scored_skills.sort(key=lambda x: x[1], reverse=True)
        top_skills = scored_skills[:max_skills]
        
        # Score and filter style preferences
        style_prefs = memory_core.get_style_preferences()
        relevant_styles = defaultdict(list)
        
        for category, prefs in style_prefs.items():
            for pref in prefs:
                relevance_score = self.score_style_relevance(pref, job_analysis)
                if relevance_score > 0.5:  # Higher threshold for style preferences
                    relevant_styles[category].append((pref, relevance_score))
        
        # Sort each category and limit
        for category in relevant_styles:
            relevant_styles[category].sort(key=lambda x: x[1], reverse=True)
            relevant_styles[category] = [item[0] for item in relevant_styles[category][:max_styles]]
        
        # Get all temporal events (they're usually relevant to personal context)
        temporal_events = memory_core.get_current_temporal_events()
        
        return {
            "relevant_skills": [skill[0] for skill in top_skills],
            "skill_scores": {skill[0]['skill_name']: skill[1] for skill in top_skills},
            "relevant_styles": dict(relevant_styles),
            "temporal_events": temporal_events,
            "job_analysis": job_analysis
        }
    
    def generate_focused_memory_summary(self, relevant_memories: Dict[str, Any]) -> str:
        """Generate a focused memory summary with only relevant information"""
        summary_parts = []
        
        # Only include relevant skills
        relevant_skills = relevant_memories["relevant_skills"]
        if relevant_skills:
            summary_parts.append("RELEVANT TECHNICAL SKILLS:")
            for skill_data in relevant_skills:
                score = relevant_memories["skill_scores"].get(skill_data['skill_name'], 0)
                summary_parts.append(f"- {skill_data['skill_name']}: {skill_data['proficiency_level']} (relevance: {score:.1f})")
                if skill_data.get('context') and len(skill_data['context']) < 100:
                    summary_parts.append(f"  Context: {skill_data['context']}")
        
        # Include relevant style preferences
        relevant_styles = relevant_memories["relevant_styles"]
        if any(relevant_styles.values()):
            summary_parts.append("\nAPPLICABLE WRITING PREFERENCES:")
            
            if relevant_styles.get("avoid_phrases"):
                avoid_list = [p["rule"] for p in relevant_styles["avoid_phrases"]]
                summary_parts.append(f"- AVOID: {', '.join(avoid_list[:3])}")  # Limit to top 3
            
            if relevant_styles.get("prefer_phrases"):
                prefer_list = [p["rule"] for p in relevant_styles["prefer_phrases"]]
                summary_parts.append(f"- PREFER: {', '.join(prefer_list[:3])}")
            
            if relevant_styles.get("tone_preferences"):
                tone_list = [p["rule"] for p in relevant_styles["tone_preferences"]]
                summary_parts.append(f"- TONE: {', '.join(tone_list[:2])}")
        
        # Include temporal events (usually relevant for personal context)
        temporal_events = relevant_memories["temporal_events"]
        if temporal_events:
            summary_parts.append("\nCURRENT PERSONAL CONTEXT:")
            for event in temporal_events[:3]:  # Limit to top 3
                summary_parts.append(f"- {event['description']} ({event['status']})")
        
        return "\n".join(summary_parts)
    
    def clear_cache(self):
        """Clear the job analysis cache"""
        self.job_analysis_cache.clear()