#!/usr/bin/env python3
"""
Cover Letter Generator - Main Entry Point

This is the main entry point for the Cover Letter Generator application.
Run this file to start the application.

Usage:
    python run.py

Requirements:
    - OpenAI API key set in environment variable OPENAI_API_KEY
    - Required Python packages installed (see requirements.txt)
"""

import sys
import os

# Add src directory to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from cover_letter_generator.main import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)