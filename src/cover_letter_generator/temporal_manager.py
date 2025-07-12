"""
Temporal Manager - Intelligent Time-Sensitive Information Management
Handles automatic updates, transitions, and context generation for temporal events
"""

import re
import calendar
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from .memory_core import MemoryCore, TemporalMemory

class TemporalManager:
    """Advanced temporal awareness and automatic updating system"""
    
    def __init__(self, memory_core: MemoryCore):
        self.memory = memory_core
        self.month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        self.season_to_months = {
            'spring': [3, 4, 5],
            'summer': [6, 7, 8], 
            'fall': [9, 10, 11],
            'autumn': [9, 10, 11],
            'winter': [12, 1, 2]
        }
    
    def _add_months(self, date_obj: datetime, months: int) -> datetime:
        """Add months to a datetime object using standard library"""
        month = date_obj.month + months
        year = date_obj.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(date_obj.day, calendar.monthrange(year, month)[1])
        return date_obj.replace(year=year, month=month, day=day)
    
    def parse_temporal_expression(self, text: str, reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime, str]:
        """Parse natural language temporal expressions into start/end dates and precision"""
        if reference_date is None:
            reference_date = datetime.now()
        
        text_lower = text.lower().strip()
        
        # Handle relative expressions
        if "next month" in text_lower:
            start_date = self._add_months(reference_date.replace(day=1), 1)
            end_date = self._add_months(start_date, 1) - timedelta(days=1)
            return start_date, end_date, "month"
        
        elif "this month" in text_lower:
            start_date = reference_date.replace(day=1)
            end_date = self._add_months(start_date, 1) - timedelta(days=1)
            return start_date, end_date, "month"
        
        elif "next year" in text_lower:
            start_date = reference_date.replace(month=1, day=1, year=reference_date.year + 1)
            end_date = start_date.replace(year=start_date.year + 1) - timedelta(days=1)
            return start_date, end_date, "year"
        
        # Handle seasonal expressions
        for season, months in self.season_to_months.items():
            pattern = rf"(?:this|next|in)\s+{season}"
            if re.search(pattern, text_lower):
                # Determine if it's this year or next year
                current_year = reference_date.year
                if "next" in text_lower or (reference_date.month > max(months)):
                    target_year = current_year + 1
                else:
                    target_year = current_year
                
                start_date = datetime(target_year, min(months), 1)
                end_month = max(months)
                if end_month == 12:
                    end_date = datetime(target_year, 12, 31)
                else:
                    end_date = datetime(target_year, end_month, calendar.monthrange(target_year, end_month)[1])
                    
                return start_date, end_date, "season"
        
        # Handle specific month expressions
        month_pattern = r"(?:in|this|next)\s+(\w+)\s*(?:(\d{4})|\b)"
        match = re.search(month_pattern, text_lower)
        if match:
            month_name = match.group(1)
            year_str = match.group(2)
            
            if month_name in self.month_names:
                month_num = self.month_names[month_name]
                
                if year_str:
                    target_year = int(year_str)
                elif "next" in text_lower or month_num <= reference_date.month:
                    target_year = reference_date.year + 1
                else:
                    target_year = reference_date.year
                
                start_date = datetime(target_year, month_num, 1)
                end_date = datetime(target_year, month_num, calendar.monthrange(target_year, month_num)[1])
                    
                return start_date, end_date, "month"
        
        # Default fallback
        return reference_date, reference_date + timedelta(days=30), "unknown"
    
    def update_all_temporal_events(self):
        """Comprehensive update of all temporal events with intelligent transitions"""
        current_date = datetime.now()
        updates_made = []
        
        for i, event in enumerate(self.memory.memory_data["temporal_events"]):
            original_status = event["status"]
            updated = False
            
            # Parse dates if they exist
            start_date = None
            end_date = None
            
            if event.get("start_date"):
                try:
                    start_date = datetime.fromisoformat(event["start_date"])
                except ValueError:
                    # Try to reparse from description if original parsing failed
                    parsed_start, parsed_end, precision = self.parse_temporal_expression(
                        event["description"], current_date
                    )
                    start_date = parsed_start
                    end_date = parsed_end
                    event["start_date"] = start_date.isoformat()
                    event["end_date"] = end_date.isoformat() if end_date else None
                    updated = True
            
            if event.get("end_date"):
                try:
                    end_date = datetime.fromisoformat(event["end_date"])
                except ValueError:
                    pass
            
            # Update status based on current date and event timing
            new_status = self._calculate_event_status(event, start_date, end_date, current_date)
            
            if new_status != event["status"]:
                event["status"] = new_status
                updated = True
                updates_made.append({
                    "event": event["description"],
                    "old_status": original_status,
                    "new_status": new_status,
                    "transition_date": current_date.isoformat()
                })
            
            # Update description if needed for natural language evolution
            updated_description = self._update_description_language(event, current_date)
            if updated_description != event["description"]:
                event["description"] = updated_description
                updated = True
        
        if updates_made:
            self.memory.save_memory()
            return updates_made
        
        return []
    
    def _calculate_event_status(self, event: Dict, start_date: Optional[datetime], 
                              end_date: Optional[datetime], current_date: datetime) -> str:
        """Calculate the appropriate status for an event based on timing"""
        
        if not start_date:
            return event["status"]  # Can't determine without start date
        
        # Buffer periods for transitions
        pre_start_buffer = timedelta(days=7)  # Consider "upcoming" one week before
        post_end_buffer = timedelta(days=30)   # Consider "completed" one month after end
        
        if current_date < start_date - pre_start_buffer:
            return "upcoming"
        elif current_date < start_date:
            return "starting_soon"  # New status for imminent events
        elif end_date and current_date > end_date + post_end_buffer:
            return "completed"
        elif end_date and current_date > end_date:
            return "recently_completed"  # New status for recently finished events
        else:
            return "current"
    
    def _update_description_language(self, event: Dict, current_date: datetime) -> str:
        """Update description language to reflect current temporal context"""
        description = event["description"]
        
        # Replace "next month" with more specific language based on current context
        if "next month" in description.lower():
            if event["status"] == "current":
                description = re.sub(r"next month", "currently", description, flags=re.IGNORECASE)
            elif event["status"] == "starting_soon":
                description = re.sub(r"next month", "very soon", description, flags=re.IGNORECASE)
        
        # Replace "will be attending" with "am attending" if current
        if event["status"] == "current":
            description = re.sub(r"will be (attending|starting|beginning)", r"am \1", description, flags=re.IGNORECASE)
            description = re.sub(r"I will (attend|start|begin)", r"I am \1ing", description, flags=re.IGNORECASE)
        
        # Replace "attending" with "attended" if completed
        if event["status"] in ["completed", "recently_completed"]:
            description = re.sub(r"am (attending|studying)", r"attended/studied", description, flags=re.IGNORECASE)
            description = re.sub(r"will (attend|start)", r"attended/completed", description, flags=re.IGNORECASE)
        
        return description
    
    def get_temporal_context_for_generation(self) -> str:
        """Generate temporal context string for AI cover letter generation"""
        context_parts = []
        current_events = self.memory.get_current_temporal_events()
        
        if not current_events:
            return ""
        
        # Group events by status
        status_groups = {}
        for event in current_events:
            status = event["status"]
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(event)
        
        # Generate context for each status group
        if "current" in status_groups:
            current_list = [event["description"] for event in status_groups["current"]]
            context_parts.append(f"CURRENTLY: {'; '.join(current_list)}")
        
        if "starting_soon" in status_groups:
            soon_list = [event["description"] for event in status_groups["starting_soon"]]
            context_parts.append(f"STARTING SOON: {'; '.join(soon_list)}")
        
        if "upcoming" in status_groups:
            upcoming_list = [event["description"] for event in status_groups["upcoming"]]
            context_parts.append(f"UPCOMING: {'; '.join(upcoming_list)}")
        
        if "recently_completed" in status_groups:
            recent_list = [event["description"] for event in status_groups["recently_completed"]]
            context_parts.append(f"RECENTLY COMPLETED: {'; '.join(recent_list)}")
        
        return "\n".join(context_parts)
    
    def add_smart_temporal_event(self, description: str, event_type: str = "education") -> TemporalMemory:
        """Add temporal event with intelligent parsing and auto-update rules"""
        
        # Parse the temporal expression from description
        start_date, end_date, precision = self.parse_temporal_expression(description)
        
        # Determine appropriate auto-update rules based on event type and precision
        auto_update_rules = {
            "update_frequency": "weekly" if precision == "month" else "monthly",
            "status_transitions": {
                "upcoming": "starting_soon",
                "starting_soon": "current",
                "current": "recently_completed",
                "recently_completed": "completed"
            },
            "description_updates": True,
            "precision": precision
        }
        
        # Determine initial status
        current_date = datetime.now()
        initial_status = self._calculate_event_status(
            {"status": "upcoming"}, start_date, end_date, current_date
        )
        
        temporal_memory = TemporalMemory(
            event_type=event_type,
            description=description,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat() if end_date else None,
            status=initial_status,
            auto_update_rules=auto_update_rules
        )
        
        self.memory.add_temporal_event(temporal_memory)
        return temporal_memory
    
    def get_temporal_summary(self) -> str:
        """Generate a summary of temporal awareness and recent updates"""
        updates = self.update_all_temporal_events()
        
        summary_parts = ["TEMPORAL AWARENESS SUMMARY:"]
        
        if updates:
            summary_parts.append(f"\nRecent Updates ({len(updates)} events):")
            for update in updates:
                summary_parts.append(f"- {update['event']}: {update['old_status']} → {update['new_status']}")
        
        current_events = self.memory.get_current_temporal_events()
        if current_events:
            summary_parts.append(f"\nActive Events ({len(current_events)}):")
            for event in current_events:
                summary_parts.append(f"- {event['description']} (Status: {event['status']})")
        
        context = self.get_temporal_context_for_generation()
        if context:
            summary_parts.append(f"\nGeneration Context:\n{context}")
        
        return "\n".join(summary_parts)