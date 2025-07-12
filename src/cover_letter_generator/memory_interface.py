"""
Memory Interface - User Interface for Memory Review and Management
Allows users to view, edit, and manage their learned preferences and memory
"""

import json
from typing import Dict, List, Any, Optional
from .memory_core import MemoryCore
from .visual_interface import VisualInterface

class MemoryInterface:
    """Interactive interface for memory review and management"""
    
    def __init__(self, memory_core: MemoryCore):
        self.memory = memory_core
        self.ui = VisualInterface()
    
    def display_memory_dashboard(self):
        """Display comprehensive memory dashboard"""
        self.ui.print_section_header("MEMORY & LEARNING DASHBOARD")
        
        # Memory statistics
        stats = self.memory.memory_data["metadata"]
        self.ui.print_info(f"Total interactions: {stats['total_interactions']}")
        self.ui.print_info(f"Successful generations: {stats['successful_generations']}")
        
        if stats['total_interactions'] > 0:
            success_rate = (stats['successful_generations'] / stats['total_interactions']) * 100
            self.ui.print_info(f"Success rate: {success_rate:.1f}%")
        
        self.ui.print_info(f"Last updated: {stats['last_updated'][:19].replace('T', ' ')}")
        
        # Memory sections
        skills_count = len(self.memory.memory_data["user_profile"]["skills"])
        style_count = sum(len(prefs) for prefs in self.memory.memory_data["style_preferences"].values())
        temporal_count = len(self.memory.memory_data["temporal_events"])
        feedback_count = len(self.memory.memory_data["feedback_history"])
        
        self.ui.print_section_footer()
        
        self.ui.print_section_header("MEMORY CATEGORIES")
        self.ui.print_info(f"[1] Skills & Experience ({skills_count} entries)")
        self.ui.print_info(f"[2] Style Preferences ({style_count} entries)")
        self.ui.print_info(f"[3] Temporal Events ({temporal_count} entries)")
        self.ui.print_info(f"[4] Feedback History ({feedback_count} entries)")
        self.ui.print_info(f"[5] Export Memory Data")
        self.ui.print_info(f"[6] Clear Specific Memory Category")
        self.ui.print_info(f"[0] Return to main menu")
        self.ui.print_section_footer()
    
    def review_skills_memory(self):
        """Review and manage skills memory"""
        self.ui.print_section_header("SKILLS & EXPERIENCE MEMORY")
        
        skills = self.memory.get_current_skills()
        if not skills:
            self.ui.print_warning("No skills learned yet.")
            self.ui.print_section_footer()
            return
        
        self.ui.print_info(f"Found {len(skills)} learned skills:")
        self.ui.print_section_footer()
        
        for i, (skill_key, skill_data) in enumerate(skills.items(), 1):
            self.ui.print_data_loading_status(f"{i}. {skill_data['skill_name']}", True)
            self.ui.print_info(f"   Proficiency: {skill_data['proficiency_level']}")
            self.ui.print_info(f"   Context: {skill_data['context']}")
            self.ui.print_info(f"   Last updated: {skill_data['last_updated'][:19].replace('T', ' ')}")
            print()
    
    def review_style_preferences(self):
        """Review and manage style preferences"""
        self.ui.print_section_header("STYLE PREFERENCES MEMORY")
        
        style_prefs = self.memory.get_style_preferences()
        
        for category, preferences in style_prefs.items():
            if preferences:
                self.ui.print_info(f"\n{category.upper().replace('_', ' ')}:")
                for i, pref in enumerate(preferences, 1):
                    self.ui.print_data_loading_status(f"  {i}. {pref['rule'][:60]}...", True)
                    self.ui.print_info(f"     Success rate: {pref['success_rate']:.1f}")
                    self.ui.print_info(f"     Last applied: {pref['last_applied'][:19].replace('T', ' ')}")
                    if pref.get('examples'):
                        self.ui.print_info(f"     Example: {pref['examples'][0][:50]}...")
        
        if not any(style_prefs.values()):
            self.ui.print_warning("No style preferences learned yet.")
        
        self.ui.print_section_footer()
    
    def review_temporal_events(self):
        """Review and manage temporal events"""
        self.ui.print_section_header("TEMPORAL EVENTS MEMORY")
        
        events = self.memory.memory_data["temporal_events"]
        if not events:
            self.ui.print_warning("No temporal events tracked yet.")
            self.ui.print_section_footer()
            return
        
        # Group by status
        status_groups = {}
        for event in events:
            status = event["status"]
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(event)
        
        for status, group_events in status_groups.items():
            self.ui.print_info(f"\n{status.upper().replace('_', ' ')} ({len(group_events)}):")
            for i, event in enumerate(group_events, 1):
                self.ui.print_data_loading_status(f"  {i}. {event['description'][:60]}...", True)
                self.ui.print_info(f"     Type: {event['event_type']}")
                if event.get('start_date'):
                    self.ui.print_info(f"     Start: {event['start_date'][:19].replace('T', ' ')}")
                if event.get('end_date'):
                    self.ui.print_info(f"     End: {event['end_date'][:19].replace('T', ' ')}")
        
        self.ui.print_section_footer()
    
    def review_feedback_history(self):
        """Review feedback history with insights"""
        self.ui.print_section_header("FEEDBACK HISTORY")
        
        feedback_history = self.memory.memory_data["feedback_history"]
        if not feedback_history:
            self.ui.print_warning("No feedback history available.")
            self.ui.print_section_footer()
            return
        
        # Show recent feedback (last 10)
        recent_feedback = feedback_history[-10:]
        self.ui.print_info(f"Showing {len(recent_feedback)} most recent feedback entries:")
        self.ui.print_section_footer()
        
        for i, feedback in enumerate(reversed(recent_feedback), 1):
            outcome_color = "success" if feedback["outcome"] == "accepted" else "warning" if feedback["outcome"] == "revision_requested" else "error"
            
            self.ui.print_info(f"\n{len(recent_feedback) - i + 1}. {feedback['outcome'].upper()}")
            self.ui.print_info(f"   Effectiveness: {feedback['effectiveness_score']:.1f}")
            self.ui.print_info(f"   Feedback: {feedback['feedback_text'][:100]}...")
            
            if feedback.get('extracted_insights'):
                insights_summary = str(feedback['extracted_insights'])[:80] + "..."
                self.ui.print_info(f"   Insights: {insights_summary}")
            
            if feedback.get('applied_changes'):
                changes = "; ".join(feedback['applied_changes'])[:80] + "..."
                self.ui.print_info(f"   Changes: {changes}")
    
    def export_memory_data(self):
        """Export memory data to a readable format"""
        self.ui.print_section_header("EXPORT MEMORY DATA")
        
        export_data = {
            "export_timestamp": self.memory.memory_data["metadata"]["last_updated"],
            "statistics": self.memory.memory_data["metadata"],
            "skills_summary": self.memory.get_current_skills(),
            "style_preferences": self.memory.get_style_preferences(),
            "temporal_events": self.memory.get_current_temporal_events(),
            "recent_feedback": self.memory.memory_data["feedback_history"][-5:],  # Last 5
            "memory_summary": self.memory.get_memory_summary()
        }
        
        # Save to file
        export_path = f"/mnt/d/Claude/output/memory_export_{self.memory.memory_data['metadata']['last_updated'][:10]}.json"
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.ui.print_success(f"Memory data exported to: {export_path}")
            self.ui.print_info("Export includes:")
            self.ui.print_info("- Skills and experience")
            self.ui.print_info("- Style preferences")
            self.ui.print_info("- Current temporal events")
            self.ui.print_info("- Recent feedback history")
            self.ui.print_info("- Generated memory summary")
            
        except Exception as e:
            self.ui.print_error(f"Export failed: {e}")
        
        self.ui.print_section_footer()
    
    def clear_memory_category(self):
        """Allow user to clear specific memory categories"""
        self.ui.print_section_header("CLEAR MEMORY CATEGORY")
        self.ui.print_warning("WARNING: This will permanently delete data!")
        
        self.ui.print_info("[1] Clear all skills")
        self.ui.print_info("[2] Clear style preferences")
        self.ui.print_info("[3] Clear temporal events")
        self.ui.print_info("[4] Clear feedback history")
        self.ui.print_info("[5] Clear ALL memory data")
        self.ui.print_info("[0] Cancel")
        
        try:
            choice = input("\nSelect category to clear [0-5]: ").strip()
            
            if choice == '0':
                self.ui.print_info("Cancelled.")
                return
            
            # Double confirmation
            self.ui.print_warning("Are you ABSOLUTELY sure? This cannot be undone!")
            confirm = input("Type 'DELETE' to confirm: ").strip()
            
            if confirm != 'DELETE':
                self.ui.print_info("Cancelled.")
                return
            
            if choice == '1':
                self.memory.memory_data["user_profile"]["skills"] = {}
                self.ui.print_success("Skills memory cleared.")
            elif choice == '2':
                self.memory.memory_data["style_preferences"] = {
                    "avoid_phrases": [],
                    "prefer_phrases": [],
                    "tone_preferences": [],
                    "structure_preferences": []
                }
                self.ui.print_success("Style preferences cleared.")
            elif choice == '3':
                self.memory.memory_data["temporal_events"] = []
                self.ui.print_success("Temporal events cleared.")
            elif choice == '4':
                self.memory.memory_data["feedback_history"] = []
                self.memory.memory_data["metadata"]["total_interactions"] = 0
                self.memory.memory_data["metadata"]["successful_generations"] = 0
                self.ui.print_success("Feedback history cleared.")
            elif choice == '5':
                self.memory.memory_data = self.memory._load_memory()  # Reset to empty structure
                self.ui.print_success("ALL memory data cleared.")
            else:
                self.ui.print_error("Invalid choice.")
                return
            
            self.memory.save_memory()
            
        except KeyboardInterrupt:
            self.ui.print_info("\nCancelled.")
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        self.ui.print_section_footer()
    
    def run_interactive_memory_manager(self):
        """Main interactive memory management loop"""
        while True:
            try:
                self.display_memory_dashboard()
                choice = input("\nSelect option [0-6]: ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self.review_skills_memory()
                elif choice == '2':
                    self.review_style_preferences()
                elif choice == '3':
                    self.review_temporal_events()
                elif choice == '4':
                    self.review_feedback_history()
                elif choice == '5':
                    self.export_memory_data()
                elif choice == '6':
                    self.clear_memory_category()
                else:
                    self.ui.print_error("Invalid choice. Please try again.")
                
                if choice != '0':
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                self.ui.print_info("\nExiting memory manager...")
                break
            except Exception as e:
                self.ui.print_error(f"Error: {e}")
                input("\nPress Enter to continue...")
    
    def get_learning_insights(self) -> str:
        """Generate insights about learning patterns"""
        feedback_history = self.memory.memory_data["feedback_history"]
        
        if len(feedback_history) < 2:
            return "Insufficient data for learning insights."
        
        # Analyze trends
        recent_feedback = feedback_history[-5:]
        success_trend = [f for f in recent_feedback if f["outcome"] == "accepted"]
        
        insights = []
        insights.append(f"LEARNING INSIGHTS ({len(feedback_history)} total interactions):")
        insights.append(f"Recent success rate: {len(success_trend)}/{len(recent_feedback)} ({len(success_trend)/len(recent_feedback)*100:.1f}%)")
        
        # Common feedback themes
        all_feedback_text = " ".join([f["feedback_text"] for f in recent_feedback]).lower()
        
        if "skill" in all_feedback_text or "experience" in all_feedback_text:
            insights.append("Learning focus: Skills and experience highlighting")
        
        if "tone" in all_feedback_text or "style" in all_feedback_text:
            insights.append("Learning focus: Writing tone and style")
        
        if "specific" in all_feedback_text or "detail" in all_feedback_text:
            insights.append("Learning focus: Specificity and detail level")
        
        # Temporal learning
        temporal_events = self.memory.get_current_temporal_events()
        if temporal_events:
            insights.append(f"Temporal awareness: Tracking {len(temporal_events)} current events")
        
        return "\n".join(insights)