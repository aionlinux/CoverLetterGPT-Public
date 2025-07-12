"""
Feedback Analyzer - AI-Powered Learning Engine
Analyzes user feedback to extract actionable insights and update memory
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from .memory_core import MemoryCore, SkillMemory, StyleMemory, TemporalMemory, FeedbackMemory

# Try to import OpenAI dependencies, but handle gracefully if missing
try:
    from .openai_client import call_openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    call_openai = None

class FeedbackAnalyzer:
    """Intelligent feedback analysis and learning system"""
    
    def __init__(self, memory_core: MemoryCore):
        self.memory = memory_core
        
    def analyze_feedback(self, feedback_text: str, cover_letter_context: str, outcome: str) -> Dict[str, Any]:
        """Intelligently analyze feedback with fast-track for simple cases"""
        
        # Fast-track simple approvals to avoid unnecessary processing
        if self._is_simple_approval(feedback_text, outcome):
            return self._handle_simple_approval(cover_letter_context, outcome)
        
        # For meaningful feedback, do full analysis
        if OPENAI_AVAILABLE and call_openai and self._feedback_needs_ai_analysis(feedback_text):
            ai_insights = self._extract_insights_with_ai(feedback_text, cover_letter_context)
        else:
            ai_insights = {}
        
        # Always apply rule-based extraction for specific patterns
        rule_based_insights = self._extract_rule_based_insights(feedback_text)
        
        # Combine and process insights
        combined_insights = self._combine_insights(ai_insights, rule_based_insights)
        
        # Update memory based on insights
        self._update_memory_from_insights(combined_insights, feedback_text, cover_letter_context, outcome)
        
        return combined_insights
    
    def _is_simple_approval(self, feedback_text: str, outcome: str) -> bool:
        """Determine if this is a simple approval that doesn't need heavy analysis"""
        if outcome != "accepted":
            return False
        
        # Simple approval patterns
        simple_patterns = [
            r"^(cover letter approved|approved|accepted).*user$",
            r"^perfect!?$",
            r"^good!?$", 
            r"^looks good!?$",
            r"^this is great!?$",
            r"^fine$",
            r"^ok$",
            r"^okay$"
        ]
        
        feedback_lower = feedback_text.lower().strip()
        
        # Check for simple patterns
        for pattern in simple_patterns:
            if re.match(pattern, feedback_lower):
                return True
        
        # If feedback is very short and contains no specific content
        if len(feedback_text) < 20 and not any(keyword in feedback_lower 
                                              for keyword in ["skill", "experience", "mention", "change", "add", "remove"]):
            return True
        
        return False
    
    def _feedback_needs_ai_analysis(self, feedback_text: str) -> bool:
        """Determine if feedback is complex enough to warrant AI analysis"""
        feedback_lower = feedback_text.lower()
        
        # Indicators that AI analysis would be valuable
        ai_indicators = [
            "mention", "add", "include", "highlight", "emphasize",
            "skill", "experience", "project", "achievement",
            "tone", "style", "rewrite", "change", "improve",
            "more", "less", "instead", "rather", "prefer"
        ]
        
        return any(indicator in feedback_lower for indicator in ai_indicators)
    
    def _handle_simple_approval(self, cover_letter_context: str, outcome: str) -> Dict[str, Any]:
        """Handle simple approval with minimal processing"""
        
        # Create a basic feedback entry without heavy analysis
        basic_feedback = FeedbackMemory(
            feedback_text="Simple approval - cover letter accepted",
            cover_letter_snippet=cover_letter_context[:200] + "..." if len(cover_letter_context) > 200 else cover_letter_context,
            outcome=outcome,
            extracted_insights=["User approved cover letter without specific feedback"],
            applied_changes=[],
            effectiveness_score=0.9,  # High score for approval
            timestamp=datetime.now().isoformat()
        )
        
        # Add to memory with minimal processing
        self.memory.add_feedback_memory(basic_feedback)
        
        # Update success metrics
        self.memory.memory_data["metadata"]["successful_generations"] += 1
        self.memory.memory_data["metadata"]["total_interactions"] += 1
        self.memory.memory_data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.memory.save_memory()
        
        return {
            "simple_approval": True,
            "processing_time": "fast",
            "insights_extracted": 0
        }
    
    def _extract_insights_with_ai(self, feedback_text: str, cover_letter_context: str) -> Dict[str, Any]:
        """Use AI to extract structured insights from feedback"""
        
        if not OPENAI_AVAILABLE or not call_openai:
            return {}
        
        analysis_prompt = f"""
        You are an expert at analyzing user feedback to extract actionable insights for improving AI-generated content.
        
        Analyze the following user feedback about a cover letter and extract structured insights.
        
        FEEDBACK: {feedback_text}
        
        COVER LETTER CONTEXT: {cover_letter_context[:500]}...
        
        Please extract and return a JSON object with the following structure:
        {{
            "skills_mentioned": [
                {{
                    "skill_name": "skill name",
                    "proficiency_context": "context about proficiency",
                    "importance": "high/medium/low"
                }}
            ],
            "phrases_to_avoid": [
                {{
                    "phrase": "exact phrase to avoid",
                    "reason": "why to avoid it"
                }}
            ],
            "phrases_to_prefer": [
                {{
                    "phrase": "preferred phrasing",
                    "context": "when to use it"
                }}
            ],
            "style_preferences": [
                {{
                    "preference": "style preference",
                    "description": "detailed description"
                }}
            ],
            "temporal_information": [
                {{
                    "event_type": "education/employment/project",
                    "description": "description of event",
                    "timing": "timing information",
                    "status": "upcoming/current/completed"
                }}
            ],
            "tone_guidance": [
                {{
                    "guidance": "tone instruction",
                    "examples": ["example phrases"]
                }}
            ],
            "content_priorities": [
                {{
                    "priority": "what to emphasize",
                    "reason": "why it's important"
                }}
            ]
        }}
        
        Focus on extracting specific, actionable insights that can be applied to future cover letter generation.
        """
        
        try:
            # Use a fresh context for analysis
            context = []
            response, _ = call_openai(
                messages=[{"role": "user", "content": analysis_prompt}],
                context=context,
                temperature=0.3,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return {}
    
    def _extract_rule_based_insights(self, feedback_text: str) -> Dict[str, Any]:
        """Extract insights using rule-based pattern matching"""
        insights = {
            "skills_mentioned": [],
            "phrases_to_avoid": [],
            "temporal_information": [],
            "style_preferences": []
        }
        
        # Common technical skills pattern
        skill_patterns = [
            r"(?:experience with|familiar with|worked with|know|use)\s+([A-Z][A-Za-z0-9\s\+\#\.]+?)(?:\s+(?:and|,|\.|\;))",
            r"([A-Z][A-Za-z0-9\s\+\#\.]{3,}?)\s+(?:experience|knowledge|skills|proficiency)",
            r"(?:mention|include|add)\s+(?:that\s+)?(?:I\s+)?(?:have\s+)?(?:experience\s+with\s+)?([A-Z][A-Za-z0-9\s\+\#\.]+)"
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, feedback_text, re.IGNORECASE)
            for match in matches:
                skill = match.group(1).strip()
                if len(skill) > 2 and skill not in [m["skill_name"] for m in insights["skills_mentioned"]]:
                    insights["skills_mentioned"].append({
                        "skill_name": skill,
                        "proficiency_context": "mentioned in feedback",
                        "importance": "high"
                    })
        
        # Phrases to avoid pattern
        avoid_patterns = [
            r"Don't say\s+[\"']([^\"']+)[\"']",
            r"avoid\s+[\"']([^\"']+)[\"']",
            r"not\s+(?:like|want)\s+[\"']([^\"']+)[\"']",
            r"remove\s+[\"']([^\"']+)[\"']"
        ]
        
        for pattern in avoid_patterns:
            matches = re.finditer(pattern, feedback_text, re.IGNORECASE)
            for match in matches:
                phrase = match.group(1).strip()
                insights["phrases_to_avoid"].append({
                    "phrase": phrase,
                    "reason": "explicitly mentioned in feedback"
                })
        
        # Educational/temporal information
        temporal_patterns = [
            r"(?:starting|beginning|enrolled?\s+(?:in|at)|attending)\s+([^\.]+?)(?:next\s+month|in\s+\w+|this\s+\w+)",
            r"(?:will\s+be|am)\s+(?:starting|beginning|attending)\s+([^\.]+)",
            r"Master\s+of\s+Science\s+in\s+([^\.]+?)(?:\s+at\s+([^\.]+?))?(?:\s+next\s+month|\s+in\s+\w+)"
        ]
        
        for pattern in temporal_patterns:
            matches = re.finditer(pattern, feedback_text, re.IGNORECASE)
            for match in matches:
                description = match.group(0).strip()
                insights["temporal_information"].append({
                    "event_type": "education",
                    "description": description,
                    "timing": self._extract_timing_from_text(description),
                    "status": "upcoming"
                })
        
        return insights
    
    def _extract_timing_from_text(self, text: str) -> str:
        """Extract timing information from text"""
        current_date = datetime.now()
        
        if "next month" in text.lower():
            next_month = current_date + timedelta(days=30)
            return next_month.isoformat()
        elif "this month" in text.lower():
            return current_date.isoformat()
        elif re.search(r"in\s+(\w+)", text, re.IGNORECASE):
            # Could be enhanced to parse specific months
            return (current_date + timedelta(days=30)).isoformat()
        
        return current_date.isoformat()
    
    def _combine_insights(self, ai_insights: Dict, rule_insights: Dict) -> Dict[str, Any]:
        """Combine AI and rule-based insights intelligently"""
        combined = {
            "skills_mentioned": [],
            "phrases_to_avoid": [],
            "phrases_to_prefer": [],
            "style_preferences": [],
            "temporal_information": [],
            "tone_guidance": [],
            "content_priorities": []
        }
        
        # Combine skills (prioritize AI insights but add rule-based ones)
        all_skills = {}
        
        for skill in ai_insights.get("skills_mentioned", []):
            skill_key = skill["skill_name"].lower()
            all_skills[skill_key] = skill
        
        for skill in rule_insights.get("skills_mentioned", []):
            skill_key = skill["skill_name"].lower()
            if skill_key not in all_skills:
                all_skills[skill_key] = skill
        
        combined["skills_mentioned"] = list(all_skills.values())
        
        # Combine other insights similarly
        for key in ["phrases_to_avoid", "phrases_to_prefer", "style_preferences", 
                   "temporal_information", "tone_guidance", "content_priorities"]:
            combined[key] = ai_insights.get(key, []) + rule_insights.get(key, [])
        
        return combined
    
    def _update_memory_from_insights(self, insights: Dict, feedback_text: str, 
                                   cover_letter_context: str, outcome: str):
        """Update memory based on extracted insights"""
        
        # Update skills
        for skill_data in insights.get("skills_mentioned", []):
            skill_memory = SkillMemory(
                skill_name=skill_data["skill_name"],
                proficiency_level=skill_data.get("proficiency_context", "experienced"),
                context=skill_data.get("importance", "mentioned in feedback"),
                examples=[],
                last_updated=datetime.now().isoformat()
            )
            self.memory.add_skill_memory(skill_memory)
        
        # Update style preferences for phrases to avoid
        for phrase_data in insights.get("phrases_to_avoid", []):
            style_memory = StyleMemory(
                preference_type="avoid_phrases",
                rule=phrase_data["phrase"],
                examples=[feedback_text[:100] + "..."],
                success_rate=1.0 if outcome == "accepted" else 0.5,
                last_applied=datetime.now().isoformat()
            )
            self.memory.add_style_preference(style_memory)
        
        # Update style preferences for preferred phrases
        for phrase_data in insights.get("phrases_to_prefer", []):
            style_memory = StyleMemory(
                preference_type="prefer_phrases",
                rule=phrase_data["phrase"],
                examples=[phrase_data.get("context", "")],
                success_rate=1.0 if outcome == "accepted" else 0.5,
                last_applied=datetime.now().isoformat()
            )
            self.memory.add_style_preference(style_memory)
        
        # Update temporal events
        for temporal_data in insights.get("temporal_information", []):
            temporal_memory = TemporalMemory(
                event_type=temporal_data["event_type"],
                description=temporal_data["description"],
                start_date=temporal_data.get("timing"),
                end_date=None,
                status=temporal_data.get("status", "upcoming"),
                auto_update_rules={
                    "update_frequency": "monthly",
                    "status_transitions": {
                        "upcoming": "current",
                        "current": "completed"
                    }
                }
            )
            self.memory.add_temporal_event(temporal_memory)
        
        # Update tone preferences
        for tone_data in insights.get("tone_guidance", []):
            style_memory = StyleMemory(
                preference_type="tone_preferences",
                rule=tone_data["guidance"],
                examples=tone_data.get("examples", []),
                success_rate=1.0 if outcome == "accepted" else 0.5,
                last_applied=datetime.now().isoformat()
            )
            self.memory.add_style_preference(style_memory)
        
        # Store feedback memory
        feedback_memory = FeedbackMemory(
            feedback_text=feedback_text,
            cover_letter_context=cover_letter_context[:500],
            outcome=outcome,
            extracted_insights=[str(insights)],
            applied_changes=[f"Updated {len(insights.get('skills_mentioned', []))} skills, "
                           f"{len(insights.get('phrases_to_avoid', []))} avoid phrases, "
                           f"{len(insights.get('temporal_information', []))} temporal events"],
            effectiveness_score=1.0 if outcome == "accepted" else 0.3
        )
        self.memory.add_feedback_memory(feedback_memory)
    
    def get_learning_summary(self) -> str:
        """Generate a summary of recent learning and improvements"""
        recent_feedback = self.memory.memory_data["feedback_history"][-5:]  # Last 5 feedback entries
        
        if not recent_feedback:
            return "No recent feedback to analyze."
        
        summary_parts = [
            f"RECENT LEARNING SUMMARY ({len(recent_feedback)} interactions):",
            ""
        ]
        
        accepted_count = sum(1 for f in recent_feedback if f["outcome"] == "accepted")
        success_rate = (accepted_count / len(recent_feedback)) * 100
        
        summary_parts.append(f"Success Rate: {success_rate:.1f}% ({accepted_count}/{len(recent_feedback)} accepted)")
        summary_parts.append("")
        
        # Analyze common themes
        all_insights = []
        for feedback in recent_feedback:
            if feedback.get("extracted_insights"):
                all_insights.extend(feedback["extracted_insights"])
        
        if all_insights:
            summary_parts.append("Key Learning Areas:")
            summary_parts.append("- Skills and technical abilities")
            summary_parts.append("- Writing style and tone preferences") 
            summary_parts.append("- Phrases and language patterns")
            summary_parts.append("- Educational and career timeline")
        
        return "\n".join(summary_parts)