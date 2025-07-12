"""
Memory Core - Intelligent Learning and Memory Management System
Provides persistent memory, learning capabilities, and temporal awareness for Cover Letter GPT
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from .config import OUTPUT_PATH

@dataclass
class MemoryEntry:
    """Base class for memory entries"""
    id: str
    timestamp: str
    category: str
    content: Any
    confidence: float = 1.0
    source: str = "user_feedback"
    
@dataclass
class SkillMemory:
    """Memory entry for skills and technical abilities"""
    skill_name: str
    proficiency_level: str
    context: str
    examples: List[str]
    last_updated: str
    
@dataclass
class StyleMemory:
    """Memory entry for writing style preferences"""
    preference_type: str  # avoid_phrases, prefer_phrases, tone, structure
    rule: str
    examples: List[str]
    success_rate: float
    last_applied: str
    context: str = ""  # Additional context about this preference
    
@dataclass
class TemporalMemory:
    """Memory entry for time-sensitive information"""
    event_type: str  # education, employment, project, certification
    description: str
    start_date: Optional[str]
    end_date: Optional[str]
    status: str  # upcoming, current, completed
    auto_update_rules: Dict[str, Any]

@dataclass
class FeedbackMemory:
    """Memory entry for user feedback and outcomes"""
    feedback_text: str
    cover_letter_context: str
    outcome: str  # accepted, rejected, revised
    extracted_insights: List[str]
    applied_changes: List[str]
    effectiveness_score: float

class MemoryCore:
    """Central memory management system with learning capabilities"""
    
    def __init__(self):
        self.memory_file = os.path.join(OUTPUT_PATH, "user_memory.json")
        self.memory_data = self._load_memory()
        self._temporal_manager = None  # Will be initialized when first needed
        self._relevance_engine = None  # Will be initialized when first needed
    
    @property
    def temporal_manager(self):
        """Lazy-loaded temporal manager to avoid circular imports"""
        if self._temporal_manager is None:
            from .temporal_manager import TemporalManager
            self._temporal_manager = TemporalManager(self)
        return self._temporal_manager
    
    @property
    def relevance_engine(self):
        """Lazy-loaded relevance engine to avoid circular imports"""
        if self._relevance_engine is None:
            from .relevance_engine import RelevanceEngine
            self._relevance_engine = RelevanceEngine()
        return self._relevance_engine
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load existing memory or create new memory structure"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Initialize new memory structure
        return {
            "user_profile": {
                "personal_info": {},
                "education": [],
                "skills": {},
                "experiences": {},
                "preferences": {}
            },
            "style_preferences": {
                "avoid_phrases": [],
                "prefer_phrases": [],
                "tone_preferences": [],
                "structure_preferences": []
            },
            "temporal_events": [],
            "feedback_history": [],
            "learning_patterns": {
                "successful_approaches": [],
                "failed_approaches": [],
                "preference_trends": {}
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_interactions": 0,
                "successful_generations": 0
            }
        }
    
    def save_memory(self):
        """Save memory to persistent storage"""
        self.memory_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_data, f, indent=2, ensure_ascii=False)
    
    def add_skill_memory(self, skill: SkillMemory):
        """Add or update skill information"""
        skill_key = skill.skill_name.lower().replace(" ", "_")
        self.memory_data["user_profile"]["skills"][skill_key] = asdict(skill)
        self.save_memory()
    
    def add_style_preference(self, style: StyleMemory):
        """Add style preference to memory"""
        category = style.preference_type
        if category not in self.memory_data["style_preferences"]:
            self.memory_data["style_preferences"][category] = []
        
        # Check if preference already exists and update, otherwise add new
        existing = next((p for p in self.memory_data["style_preferences"][category] 
                        if p.get("rule") == style.rule), None)
        
        if existing:
            existing.update(asdict(style))
        else:
            self.memory_data["style_preferences"][category].append(asdict(style))
        
        self.save_memory()
    
    def add_temporal_event(self, event: TemporalMemory):
        """Add time-sensitive information"""
        self.memory_data["temporal_events"].append(asdict(event))
        self.save_memory()
    
    def add_feedback_memory(self, feedback: FeedbackMemory):
        """Store feedback and learning outcomes"""
        self.memory_data["feedback_history"].append(asdict(feedback))
        self.memory_data["metadata"]["total_interactions"] += 1
        
        if feedback.outcome == "accepted":
            self.memory_data["metadata"]["successful_generations"] += 1
        
        self.save_memory()
    
    def get_current_skills(self) -> Dict[str, Any]:
        """Get all current skills"""
        return self.memory_data["user_profile"]["skills"]
    
    def get_style_preferences(self) -> Dict[str, List]:
        """Get all style preferences"""
        return self.memory_data["style_preferences"]
    
    def get_current_temporal_events(self) -> List[Dict]:
        """Get current and upcoming temporal events"""
        current_events = []
        for event in self.memory_data["temporal_events"]:
            if event["status"] in ["current", "upcoming"]:
                current_events.append(event)
        return current_events
    
    def update_temporal_events(self):
        """Update time-sensitive information using enhanced temporal manager"""
        return self.temporal_manager.update_all_temporal_events()
    
    def get_memory_summary(self) -> str:
        """Generate a comprehensive memory summary for AI context"""
        summary_parts = []
        
        # Skills summary
        skills = self.get_current_skills()
        if skills:
            summary_parts.append("TECHNICAL SKILLS AND EXPERIENCE:")
            for skill_key, skill_data in skills.items():
                summary_parts.append(f"- {skill_data['skill_name']}: {skill_data['proficiency_level']}")
                if skill_data['context']:
                    summary_parts.append(f"  Context: {skill_data['context']}")
        
        # Style preferences
        style_prefs = self.get_style_preferences()
        if any(style_prefs.values()):
            summary_parts.append("\nWRITING STYLE PREFERENCES:")
            
            if style_prefs.get("avoid_phrases"):
                avoid_list = [p["rule"] for p in style_prefs["avoid_phrases"]]
                summary_parts.append(f"- AVOID these phrases: {', '.join(avoid_list)}")
            
            if style_prefs.get("prefer_phrases"):
                prefer_list = [p["rule"] for p in style_prefs["prefer_phrases"]]
                summary_parts.append(f"- PREFER these approaches: {', '.join(prefer_list)}")
            
            if style_prefs.get("tone_preferences"):
                tone_list = [p["rule"] for p in style_prefs["tone_preferences"]]
                summary_parts.append(f"- TONE preferences: {', '.join(tone_list)}")
        
        # Current temporal events
        current_events = self.get_current_temporal_events()
        if current_events:
            summary_parts.append("\nCURRENT/UPCOMING EVENTS:")
            for event in current_events:
                summary_parts.append(f"- {event['description']} (Status: {event['status']})")
        
        # Learning patterns
        feedback_count = len(self.memory_data["feedback_history"])
        success_rate = (self.memory_data["metadata"]["successful_generations"] / 
                       max(1, self.memory_data["metadata"]["total_interactions"]) * 100)
        
        summary_parts.append(f"\nLEARNING STATISTICS:")
        summary_parts.append(f"- Total feedback interactions: {feedback_count}")
        summary_parts.append(f"- Success rate: {success_rate:.1f}%")
        
        return "\n".join(summary_parts)
    
    def get_job_aware_memory_summary(self, job_description: str) -> str:
        """Generate an intelligent, job-focused memory summary using relevance scoring"""
        
        # Get relevant memories for this specific job
        relevant_memories = self.relevance_engine.get_relevant_memories(
            self, job_description, max_skills=8, max_styles=5
        )
        
        # Generate focused summary with only relevant information
        return self.relevance_engine.generate_focused_memory_summary(relevant_memories)
    
    def get_memory_analysis_for_job(self, job_description: str) -> Dict[str, Any]:
        """Get detailed analysis of memory relevance for a specific job"""
        return self.relevance_engine.get_relevant_memories(self, job_description)
    
    def search_memory(self, query: str) -> List[Dict]:
        """Search through memory for relevant information"""
        results = []
        query_lower = query.lower()
        
        # Search skills
        for skill_key, skill_data in self.memory_data["user_profile"]["skills"].items():
            if (query_lower in skill_data["skill_name"].lower() or 
                query_lower in skill_data["context"].lower()):
                results.append({"type": "skill", "data": skill_data})
        
        # Search feedback history
        for feedback in self.memory_data["feedback_history"]:
            if query_lower in feedback["feedback_text"].lower():
                results.append({"type": "feedback", "data": feedback})
        
        return results