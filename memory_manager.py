#!/usr/bin/env python3
"""
Memory Manager - Standalone interface for Cover Letter GPT memory management
Run this to review, export, or manage learned preferences and memory data
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cover_letter_generator.memory_core import MemoryCore
from src.cover_letter_generator.memory_interface import MemoryInterface
from src.cover_letter_generator.visual_interface import VisualInterface

def main():
    """Main entry point for memory management"""
    ui = VisualInterface()
    
    # Display welcome banner
    ui.print_banner()
    ui.print_section_header("MEMORY & LEARNING MANAGER")
    ui.print_info("Welcome to the Cover Letter GPT Memory Management Interface")
    ui.print_info("Here you can review what the system has learned, export data, and manage preferences.")
    ui.print_section_footer()
    
    try:
        # Initialize memory system
        ui.start_loading("Loading memory system")
        memory = MemoryCore()
        memory_interface = MemoryInterface(memory)
        ui.stop_loading()
        
        # Display learning insights
        insights = memory_interface.get_learning_insights()
        if "Insufficient data" not in insights:
            ui.print_info("CURRENT LEARNING STATUS:")
            ui.print_data_preview(insights)
            print()
        
        # Run interactive memory manager
        memory_interface.run_interactive_memory_manager()
        
    except Exception as e:
        ui.stop_loading()
        ui.print_error(f"Error initializing memory system: {e}")
        return
    
    ui.print_goodbye()

if __name__ == "__main__":
    main()