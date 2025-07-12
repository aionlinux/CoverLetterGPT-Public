"""
File Monitor - Automatic Detection and Processing of criteria.txt and skillset.csv Changes
Provides seamless integration between user-friendly files and computer-optimized memory
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Optional
from .config import DATA_PROFILE_PATH
from .memory_core import MemoryCore, SkillMemory, StyleMemory

class FileMonitor:
    """Monitors and processes changes to user-editable files"""
    
    def __init__(self, memory_core: MemoryCore):
        self.memory = memory_core
        self.criteria_path = os.path.join(DATA_PROFILE_PATH, 'criteria.txt')
        self.skillset_path = os.path.join(DATA_PROFILE_PATH, 'skillset.csv')
        self.checksums_file = os.path.join(DATA_PROFILE_PATH, '.file_checksums.json')
        
    def _get_file_checksum(self, file_path: str) -> str:
        """Get MD5 checksum of a file"""
        if not os.path.exists(file_path):
            return ""
        
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _load_stored_checksums(self) -> Dict[str, str]:
        """Load previously stored file checksums"""
        if os.path.exists(self.checksums_file):
            try:
                with open(self.checksums_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_checksums(self, checksums: Dict[str, str]):
        """Save current file checksums"""
        with open(self.checksums_file, 'w') as f:
            json.dump(checksums, f, indent=2)
    
    def check_for_changes(self) -> Dict[str, bool]:
        """Check if criteria.txt or skillset.csv have changed"""
        current_checksums = {
            'criteria.txt': self._get_file_checksum(self.criteria_path),
            'skillset.csv': self._get_file_checksum(self.skillset_path)
        }
        
        stored_checksums = self._load_stored_checksums()
        
        changes = {
            'criteria_changed': current_checksums['criteria.txt'] != stored_checksums.get('criteria.txt', ''),
            'skillset_changed': current_checksums['skillset.csv'] != stored_checksums.get('skillset.csv', ''),
            'any_changes': False
        }
        
        changes['any_changes'] = changes['criteria_changed'] or changes['skillset_changed']
        
        if changes['any_changes']:
            self._save_checksums(current_checksums)
        
        return changes
    
    def process_skillset_changes(self) -> Dict[str, int]:
        """Process skillset.csv changes and update memory intelligently"""
        if not os.path.exists(self.skillset_path):
            return {"added": 0, "updated": 0, "removed": 0}
        
        # Read and parse skillset.csv properly
        new_skills = self._parse_skillset_file()
        existing_skills = set(self.memory.get_current_skills().keys())
        
        # Track changes
        added = 0
        updated = 0
        removed = 0
        
        # Process new/updated skills
        for skill_name in new_skills:
            skill_key = self._normalize_skill_key(skill_name)
            
            if skill_key not in existing_skills:
                # Add new skill
                skill_memory = SkillMemory(
                    skill_name=skill_name,
                    proficiency_level="Listed in skillset.csv",
                    context="User-maintained skill list",
                    examples=[],
                    last_updated=datetime.now().isoformat()
                )
                self.memory.add_skill_memory(skill_memory)
                added += 1
            else:
                # Update existing skill if it's from the original skillset
                skill_data = self.memory.memory_data["user_profile"]["skills"][skill_key]
                if "skillset.csv" in skill_data.get("context", ""):
                    skill_data["last_updated"] = datetime.now().isoformat()
                    updated += 1
        
        # Remove skills that are no longer in skillset.csv (but only if they came from skillset originally)
        current_skillset_skills = {self._normalize_skill_key(name) for name in new_skills}
        
        for skill_key, skill_data in list(self.memory.memory_data["user_profile"]["skills"].items()):
            if ("skillset.csv" in skill_data.get("context", "") and 
                skill_key not in current_skillset_skills):
                # Remove skill that's no longer in skillset.csv
                del self.memory.memory_data["user_profile"]["skills"][skill_key]
                removed += 1
        
        self.memory.save_memory()
        return {"added": added, "updated": updated, "removed": removed}
    
    def _parse_skillset_file(self) -> Set[str]:
        """Parse skillset.csv and extract clean skill names"""
        skills = set()
        
        with open(self.skillset_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Handle different separators
            if '\t' in content:
                raw_skills = content.split('\t')
            elif ',' in content:
                raw_skills = content.split(',')
            else:
                # Single line, try other separators
                for sep in ['|', ';', '\n']:
                    if sep in content:
                        raw_skills = content.split(sep)
                        break
                else:
                    raw_skills = [content]  # Single skill
            
            # Clean and validate skills
            for skill in raw_skills:
                clean_skill = skill.strip()
                if len(clean_skill) > 1 and len(clean_skill) < 100:  # Reasonable length
                    skills.add(clean_skill)
        
        return skills
    
    def process_criteria_changes(self) -> Dict[str, int]:
        """Process criteria.txt changes and update style preferences"""
        if not os.path.exists(self.criteria_path):
            return {"added": 0, "updated": 0}
        
        # Read criteria.txt
        with open(self.criteria_path, 'r', encoding='utf-8') as f:
            criteria_content = f.read()
        
        # Extract style rules from criteria (enhanced extraction)
        new_rules = self._extract_style_rules_from_criteria(criteria_content)
        
        added = 0
        updated = 0
        
        # Process each rule
        for rule_data in new_rules:
            # Check if this rule already exists
            existing = False
            for category, prefs in self.memory.memory_data["style_preferences"].items():
                if any(p["rule"] == rule_data["rule"] for p in prefs):
                    existing = True
                    break
            
            if not existing:
                style_pref = StyleMemory(
                    preference_type=rule_data["type"],
                    rule=rule_data["rule"],
                    examples=[],
                    success_rate=1.0,  # High confidence for criteria-based rules
                    last_applied=datetime.now().isoformat(),
                    context=rule_data["context"]
                )
                self.memory.add_style_preference(style_pref)
                added += 1
            else:
                updated += 1
        
        self.memory.save_memory()
        return {"added": added, "updated": updated}
    
    def _extract_style_rules_from_criteria(self, criteria_content: str) -> List[Dict[str, str]]:
        """Extract style rules from criteria.txt content"""
        rules = []
        
        # Basic rules from criteria content
        lines = criteria_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Substantial content
                if 'avoid' in line.lower():
                    rules.append({
                        "type": "avoid_phrases",
                        "rule": line,
                        "context": "From criteria.txt guidance"
                    })
                elif 'prefer' in line.lower() or 'use' in line.lower():
                    rules.append({
                        "type": "structure_preferences", 
                        "rule": line,
                        "context": "From criteria.txt guidance"
                    })
                elif 'tone' in line.lower() or 'write' in line.lower():
                    rules.append({
                        "type": "tone_preferences",
                        "rule": line,
                        "context": "From criteria.txt guidance"
                    })
        
        # Extract specific patterns
        if "350 words" in criteria_content:
            rules.append({
                "type": "structure_preferences",
                "rule": "Write cover letters with appropriate length for the role - focus on quality over brevity",
                "context": "Updated from criteria.txt - no artificial word limits"
            })
        
        if "contraction" in criteria_content.lower():
            rules.append({
                "type": "structure_preferences",
                "rule": "Use contractions occasionally for natural flow (I've, I'm, that's)",
                "context": "From criteria.txt natural writing instruction"
            })
        
        return rules
    
    def _normalize_skill_key(self, skill_name: str) -> str:
        """Create normalized key for skill storage"""
        return skill_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace('.', '')
    
    def clean_memory_pollution(self) -> Dict[str, int]:
        """Clean up polluted memory entries"""
        cleaned = {
            "invalid_skills_removed": 0,
            "consolidated_entries": 0,
            "duplicates_removed": 0
        }
        
        # Remove invalid skills
        invalid_skill_keys = []
        for skill_key, skill_data in self.memory.memory_data["user_profile"]["skills"].items():
            skill_name = skill_data["skill_name"]
            
            # Remove skills that are clearly not skills
            if (len(skill_name) > 200 or  # Too long
                '\t' in skill_name or  # Contains tabs (parsing error)
                skill_name.count(' ') > 10 or  # Too many words
                'This captures my voice' in skill_name or  # Feedback artifact
                'Cover letter approved' in skill_name):  # Feedback artifact
                invalid_skill_keys.append(skill_key)
                cleaned["invalid_skills_removed"] += 1
        
        # Remove invalid skills
        for key in invalid_skill_keys:
            del self.memory.memory_data["user_profile"]["skills"][key]
        
        # Find and remove duplicates
        skill_names_seen = set()
        duplicate_keys = []
        
        for skill_key, skill_data in self.memory.memory_data["user_profile"]["skills"].items():
            skill_name = skill_data["skill_name"].lower().strip()
            if skill_name in skill_names_seen:
                duplicate_keys.append(skill_key)
                cleaned["duplicates_removed"] += 1
            else:
                skill_names_seen.add(skill_name)
        
        # Remove duplicates
        for key in duplicate_keys:
            del self.memory.memory_data["user_profile"]["skills"][key]
        
        # Clean up style preferences
        for category in self.memory.memory_data["style_preferences"]:
            prefs = self.memory.memory_data["style_preferences"][category]
            unique_prefs = []
            seen_rules = set()
            
            for pref in prefs:
                rule = pref["rule"]
                if rule not in seen_rules and len(rule) > 5:
                    seen_rules.add(rule)
                    unique_prefs.append(pref)
                else:
                    cleaned["duplicates_removed"] += 1
            
            self.memory.memory_data["style_preferences"][category] = unique_prefs
        
        self.memory.save_memory()
        return cleaned
    
    def auto_sync_files(self) -> Dict[str, any]:
        """Automatically sync file changes and clean memory"""
        results = {
            "changes_detected": False,
            "skillset_changes": {},
            "criteria_changes": {},
            "cleanup_results": {}
        }
        
        # Check for file changes
        changes = self.check_for_changes()
        results["changes_detected"] = changes["any_changes"]
        
        if changes["skillset_changed"]:
            results["skillset_changes"] = self.process_skillset_changes()
        
        if changes["criteria_changed"]:
            results["criteria_changes"] = self.process_criteria_changes()
        
        # Always clean memory pollution
        results["cleanup_results"] = self.clean_memory_pollution()
        
        return results
    
    def force_resync(self) -> Dict[str, any]:
        """Force a complete resync of all files"""
        # Remove existing checksums to force update
        if os.path.exists(self.checksums_file):
            os.remove(self.checksums_file)
        
        return self.auto_sync_files()