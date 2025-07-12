#!/usr/bin/env python3
"""
Memory Navigator - Human-Readable Interface for Cover Letter GPT Memory
Provides intuitive navigation and understanding of the AI's learned knowledge
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.cover_letter_generator.memory_core import MemoryCore
    from src.cover_letter_generator.file_monitor import FileMonitor
    from src.cover_letter_generator.visual_interface import VisualInterface
except ImportError:
    print("❌ Could not import memory modules. Please run from the project root directory.")
    sys.exit(1)

class MemoryNavigator:
    """User-friendly interface for exploring and understanding memory"""
    
    def __init__(self):
        self.ui = VisualInterface()
        try:
            self.memory = MemoryCore()
            self.file_monitor = FileMonitor(self.memory)
        except Exception as e:
            print(f"❌ Error initializing memory system: {e}")
            sys.exit(1)
    
    def show_main_menu(self):
        """Display main navigation menu"""
        self.ui.print_banner()
        self.ui.print_section_header("MEMORY NAVIGATOR")
        self.ui.print_info("Explore what your AI assistant has learned about your preferences")
        self.ui.print_section_footer()
        
        # Auto-sync files first
        self.ui.print_info("Checking for file changes...")
        sync_results = self.file_monitor.auto_sync_files()
        
        if sync_results["changes_detected"]:
            self.ui.print_success("Files synchronized with memory!")
            if sync_results["skillset_changes"]:
                changes = sync_results["skillset_changes"]
                self.ui.print_info(f"Skills: +{changes['added']} -{changes['removed']} ~{changes['updated']}")
        
        if sync_results["cleanup_results"]["invalid_skills_removed"] > 0:
            cleanup = sync_results["cleanup_results"]
            self.ui.print_success(f"Cleaned up {cleanup['invalid_skills_removed']} invalid entries")
        
        print()
        
        # Memory statistics
        stats = self.memory.memory_data["metadata"]
        skills_count = len(self.memory.get_current_skills())
        interactions = stats["total_interactions"]
        success_rate = (stats["successful_generations"] / max(1, interactions)) * 100
        
        self.ui.print_section_header("MEMORY OVERVIEW")
        self.ui.print_info(f"Total Skills Learned: {skills_count}")
        self.ui.print_info(f"Total Interactions: {interactions}")
        self.ui.print_info(f"Success Rate: {success_rate:.1f}%")
        self.ui.print_info(f"Last Updated: {stats['last_updated'][:19].replace('T', ' ')}")
        self.ui.print_section_footer()
        
        # Menu options
        self.ui.print_section_header("NAVIGATION OPTIONS")
        self.ui.print_info("[1] Browse Technical Skills")
        self.ui.print_info("[2] Review Writing Preferences")
        self.ui.print_info("[3] View Life Timeline Events")
        self.ui.print_info("[4] Analyze Feedback History")
        self.ui.print_info("[5] Search Memory")
        self.ui.print_info("[6] Export Human-Readable Report")
        self.ui.print_info("[7] Clean & Optimize Memory")
        self.ui.print_info("[8] Sync Files (criteria.txt, skillset.csv)")
        self.ui.print_info("[0] Exit")
        self.ui.print_section_footer()
    
    def browse_technical_skills(self):
        """Browse technical skills in an organized way"""
        self.ui.print_section_header("TECHNICAL SKILLS LEARNED")
        
        skills = self.memory.get_current_skills()
        if not skills:
            self.ui.print_warning("No skills learned yet.")
            return
        
        # Categorize skills
        categories = {
            "Programming & Scripting": [],
            "Databases & Data": [],
            "Networks & Security": [],
            "Systems Administration": [],
            "Cloud & Infrastructure": [],
            "Support & Troubleshooting": [],
            "Other Technical Skills": []
        }
        
        # Categorize each skill
        for skill_key, skill_data in skills.items():
            skill_name = skill_data["skill_name"].lower()
            categorized = False
            
            # Programming
            if any(term in skill_name for term in ["python", "scripting", "bash", "powershell", "programming", "automation", ".net"]):
                categories["Programming & Scripting"].append(skill_data)
                categorized = True
            # Databases
            elif any(term in skill_name for term in ["sql", "mysql", "database", "data", "bi", "reporting", "crystal"]):
                categories["Databases & Data"].append(skill_data)
                categorized = True
            # Networks
            elif any(term in skill_name for term in ["network", "firewall", "vpn", "security", "tcp", "ip"]):
                categories["Networks & Security"].append(skill_data)
                categorized = True
            # Systems
            elif any(term in skill_name for term in ["windows", "linux", "active directory", "system", "admin", "patch", "backup"]):
                categories["Systems Administration"].append(skill_data)
                categorized = True
            # Cloud
            elif any(term in skill_name for term in ["cloud", "infrastructure", "vm", "virtual", "modernization"]):
                categories["Cloud & Infrastructure"].append(skill_data)
                categorized = True
            # Support
            elif any(term in skill_name for term in ["support", "troubleshooting", "help", "hardware", "software"]):
                categories["Support & Troubleshooting"].append(skill_data)
                categorized = True
            
            if not categorized:
                categories["Other Technical Skills"].append(skill_data)
        
        # Display categorized skills
        for category, skills_list in categories.items():
            if skills_list:
                print(f"\n{self.ui.print_info.__class__.__module__}")  # Spacing
                self.ui.print_info(f"📂 {category} ({len(skills_list)} skills)")
                
                for skill in skills_list[:5]:  # Show top 5 per category
                    proficiency = skill["proficiency_level"]
                    if len(proficiency) > 50:
                        proficiency = proficiency[:47] + "..."
                    
                    self.ui.print_info(f"   • {skill['skill_name']}")
                    self.ui.print_info(f"     Level: {proficiency}")
                    
                    if skill.get("context") and len(skill["context"]) < 50:
                        self.ui.print_info(f"     Source: {skill['context']}")
                
                if len(skills_list) > 5:
                    self.ui.print_info(f"   ... and {len(skills_list) - 5} more skills")
        
        self.ui.print_section_footer()
    
    def review_writing_preferences(self):
        """Review writing style preferences"""
        self.ui.print_section_header("WRITING STYLE PREFERENCES")
        
        style_prefs = self.memory.get_style_preferences()
        
        for category, preferences in style_prefs.items():
            if preferences:
                category_name = category.replace('_', ' ').title()
                self.ui.print_info(f"\n📝 {category_name} ({len(preferences)} rules)")
                
                for i, pref in enumerate(preferences[:3], 1):  # Show top 3
                    rule = pref["rule"]
                    if len(rule) > 80:
                        rule = rule[:77] + "..."
                    
                    success_rate = pref.get("success_rate", 0) * 100
                    self.ui.print_info(f"   {i}. {rule}")
                    self.ui.print_info(f"      Success Rate: {success_rate:.0f}%")
                    
                    if pref.get("context"):
                        context = pref["context"]
                        if len(context) > 60:
                            context = context[:57] + "..."
                        self.ui.print_info(f"      Source: {context}")
                
                if len(preferences) > 3:
                    self.ui.print_info(f"   ... and {len(preferences) - 3} more rules")
        
        if not any(style_prefs.values()):
            self.ui.print_warning("No writing preferences learned yet.")
        
        self.ui.print_section_footer()
    
    def view_timeline_events(self):
        """View life timeline and temporal events"""
        self.ui.print_section_header("LIFE TIMELINE & EVENTS")
        
        events = self.memory.memory_data["temporal_events"]
        if not events:
            self.ui.print_warning("No timeline events tracked yet.")
            return
        
        # Group by status
        status_groups = {"current": [], "upcoming": [], "completed": [], "other": []}
        
        for event in events:
            status = event.get("status", "other")
            if status in status_groups:
                status_groups[status].append(event)
            else:
                status_groups["other"].append(event)
        
        # Display each group
        for status, group in status_groups.items():
            if group:
                status_icon = {"current": "🔄", "upcoming": "📅", "completed": "✅", "other": "📋"}
                self.ui.print_info(f"\n{status_icon[status]} {status.title()} Events ({len(group)})")
                
                for event in group:
                    description = event["description"]
                    if len(description) > 70:
                        description = description[:67] + "..."
                    
                    self.ui.print_info(f"   • {description}")
                    
                    if event.get("start_date"):
                        start_date = event["start_date"]
                        if "T" in start_date:
                            start_date = start_date[:19].replace("T", " ")
                        self.ui.print_info(f"     Starts: {start_date}")
                    
                    event_type = event.get("event_type", "general")
                    self.ui.print_info(f"     Type: {event_type}")
        
        self.ui.print_section_footer()
    
    def analyze_feedback_history(self):
        """Analyze feedback patterns and learning"""
        self.ui.print_section_header("FEEDBACK ANALYSIS")
        
        feedback_history = self.memory.memory_data["feedback_history"]
        if not feedback_history:
            self.ui.print_warning("No feedback history available.")
            return
        
        # Calculate statistics
        total_feedback = len(feedback_history)
        accepted = len([f for f in feedback_history if f["outcome"] == "accepted"])
        revisions = len([f for f in feedback_history if f["outcome"] == "revision_requested"])
        rejected = len([f for f in feedback_history if f["outcome"] == "rejected"])
        
        avg_effectiveness = sum(f.get("effectiveness_score", 0) for f in feedback_history) / total_feedback
        
        self.ui.print_info(f"📊 Feedback Statistics")
        self.ui.print_info(f"   Total Feedback: {total_feedback}")
        self.ui.print_info(f"   Accepted: {accepted} ({accepted/total_feedback*100:.1f}%)")
        self.ui.print_info(f"   Revisions: {revisions} ({revisions/total_feedback*100:.1f}%)")
        self.ui.print_info(f"   Rejected: {rejected} ({rejected/total_feedback*100:.1f}%)")
        self.ui.print_info(f"   Avg Effectiveness: {avg_effectiveness:.2f}/1.0")
        
        # Recent feedback
        self.ui.print_info(f"\n📝 Recent Feedback (Last 3)")
        recent = feedback_history[-3:] if len(feedback_history) >= 3 else feedback_history
        
        for i, feedback in enumerate(reversed(recent), 1):
            outcome_emoji = {"accepted": "✅", "revision_requested": "🔄", "rejected": "❌"}
            emoji = outcome_emoji.get(feedback["outcome"], "📝")
            
            feedback_text = feedback["feedback_text"]
            if len(feedback_text) > 60:
                feedback_text = feedback_text[:57] + "..."
            
            self.ui.print_info(f"   {emoji} {feedback_text}")
            self.ui.print_info(f"      Outcome: {feedback['outcome']}")
            self.ui.print_info(f"      Effectiveness: {feedback.get('effectiveness_score', 0):.2f}")
        
        self.ui.print_section_footer()
    
    def search_memory(self):
        """Search through memory content"""
        self.ui.print_section_header("MEMORY SEARCH")
        
        try:
            query = input("Enter search term: ").strip()
            if not query:
                self.ui.print_warning("No search term provided.")
                return
            
            results = self.memory.search_memory(query)
            
            if not results:
                self.ui.print_warning(f"No results found for '{query}'")
                return
            
            self.ui.print_success(f"Found {len(results)} results for '{query}':")
            
            for result in results[:10]:  # Limit to 10 results
                result_type = result["type"]
                data = result["data"]
                
                if result_type == "skill":
                    self.ui.print_info(f"   🛠️  Skill: {data['skill_name']}")
                    self.ui.print_info(f"      Level: {data['proficiency_level']}")
                elif result_type == "style":
                    self.ui.print_info(f"   📝 Style: {data['rule'][:60]}...")
                elif result_type == "feedback":
                    self.ui.print_info(f"   💬 Feedback: {data['feedback_text'][:60]}...")
            
            if len(results) > 10:
                self.ui.print_info(f"   ... and {len(results) - 10} more results")
                
        except KeyboardInterrupt:
            self.ui.print_info("\nSearch cancelled.")
        
        self.ui.print_section_footer()
    
    def export_readable_report(self):
        """Export a human-readable memory report"""
        self.ui.print_section_header("EXPORT MEMORY REPORT")
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = f"/mnt/d/Claude/output/memory_report_{timestamp}.txt"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("COVER LETTER GPT - MEMORY REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Statistics
                stats = self.memory.memory_data["metadata"]
                skills_count = len(self.memory.get_current_skills())
                f.write("OVERVIEW\n")
                f.write("-" * 20 + "\n")
                f.write(f"Skills Learned: {skills_count}\n")
                f.write(f"Total Interactions: {stats['total_interactions']}\n")
                f.write(f"Success Rate: {(stats['successful_generations']/max(1,stats['total_interactions']))*100:.1f}%\n\n")
                
                # Skills
                skills = self.memory.get_current_skills()
                if skills:
                    f.write("TECHNICAL SKILLS\n")
                    f.write("-" * 20 + "\n")
                    for skill_data in list(skills.values())[:20]:  # Top 20 skills
                        f.write(f"• {skill_data['skill_name']}\n")
                        f.write(f"  Level: {skill_data['proficiency_level']}\n")
                        if skill_data.get("context"):
                            f.write(f"  Source: {skill_data['context']}\n")
                        f.write("\n")
                
                # Style preferences
                style_prefs = self.memory.get_style_preferences()
                f.write("WRITING PREFERENCES\n")
                f.write("-" * 20 + "\n")
                
                for category, prefs in style_prefs.items():
                    if prefs:
                        f.write(f"\n{category.replace('_', ' ').title()}:\n")
                        for pref in prefs[:5]:  # Top 5 per category
                            f.write(f"• {pref['rule']}\n")
                
                f.write(f"\n\nReport saved: {report_path}\n")
            
            self.ui.print_success(f"Report exported to: {report_path}")
            
        except Exception as e:
            self.ui.print_error(f"Export failed: {e}")
        
        self.ui.print_section_footer()
    
    def clean_optimize_memory(self):
        """Clean and optimize memory"""
        self.ui.print_section_header("MEMORY CLEANUP & OPTIMIZATION")
        
        self.ui.print_info("Analyzing memory for optimization opportunities...")
        
        # Run cleanup
        cleanup_results = self.file_monitor.clean_memory_pollution()
        
        self.ui.print_success("Memory optimization complete!")
        self.ui.print_info(f"Invalid entries removed: {cleanup_results['invalid_skills_removed']}")
        self.ui.print_info(f"Duplicates removed: {cleanup_results['duplicates_removed']}")
        
        # Show memory size
        memory_size = os.path.getsize(self.memory.memory_file)
        self.ui.print_info(f"Memory file size: {memory_size / 1024:.1f} KB")
        
        self.ui.print_section_footer()
    
    def sync_files(self):
        """Force sync of criteria.txt and skillset.csv"""
        self.ui.print_section_header("FILE SYNCHRONIZATION")
        
        self.ui.print_info("Forcing resync of all user files...")
        sync_results = self.file_monitor.force_resync()
        
        if sync_results["changes_detected"]:
            self.ui.print_success("Files synchronized!")
            
            if sync_results["skillset_changes"]:
                changes = sync_results["skillset_changes"]
                self.ui.print_info(f"Skillset: +{changes['added']} -{changes['removed']} ~{changes['updated']}")
            
            if sync_results["criteria_changes"]:
                changes = sync_results["criteria_changes"]
                self.ui.print_info(f"Criteria: +{changes['added']} updated rules")
        else:
            self.ui.print_info("No changes detected in files.")
        
        self.ui.print_section_footer()
    
    def run(self):
        """Main application loop"""
        while True:
            try:
                self.show_main_menu()
                choice = input("\nSelect option [0-8]: ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self.browse_technical_skills()
                elif choice == '2':
                    self.review_writing_preferences()
                elif choice == '3':
                    self.view_timeline_events()
                elif choice == '4':
                    self.analyze_feedback_history()
                elif choice == '5':
                    self.search_memory()
                elif choice == '6':
                    self.export_readable_report()
                elif choice == '7':
                    self.clean_optimize_memory()
                elif choice == '8':
                    self.sync_files()
                else:
                    self.ui.print_error("Invalid choice. Please try again.")
                
                if choice != '0':
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\nExiting memory navigator...")
                break
            except Exception as e:
                self.ui.print_error(f"Error: {e}")
                input("\nPress Enter to continue...")
        
        self.ui.print_goodbye()

def main():
    """Entry point"""
    navigator = MemoryNavigator()
    navigator.run()

if __name__ == "__main__":
    main()