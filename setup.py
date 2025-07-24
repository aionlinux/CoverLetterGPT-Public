#!/usr/bin/env python3
"""
Setup Script for Cover Letter GPT - Ultra-Fine-Tuned System
===========================================================

Quick setup script for getting started with the Cover Letter GPT system.
Validates environment, installs dependencies, and provides setup guidance.

Purpose: Streamlined setup for public GitHub showcase
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("🚀 Cover Letter GPT - Ultra-Fine-Tuned Setup")
    print("⚡ Ultra-Fine-Tuned by Claude AI (Anthropic) ⚡")
    print("=" * 50)
    print()

def check_python_version():
    """Check if Python version is supported"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def check_openai_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API Key not found")
        print("   Please set your API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print()
        return False
    
    print("✅ OpenAI API Key found")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Install main dependencies
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Main dependencies installed")
        
        # Check if user wants development dependencies
        install_dev = input("Install development dependencies? (y/N): ").strip().lower()
        if install_dev in ['y', 'yes']:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-test.txt'], 
                          check=True, capture_output=True)
            print("✅ Development dependencies installed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("   Try running manually: pip install -r requirements.txt")
        return False
    
    return True

def validate_structure():
    """Validate project structure"""
    required_dirs = [
        "src/cover_letter_generator",
        "data/profile", 
        "data/input",
        "output",
        "tests",
        "docs"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Missing directories: {', '.join(missing)}")
        return False
    
    print("✅ Project structure validated")
    return True

def create_demo_files():
    """Ensure demo files exist"""
    demo_files = [
        "data/profile/TechProfessionalResume.pdf",
        "data/profile/criteria.txt",
        "data/profile/skillset.csv",
        "data/input/job_listing.txt"
    ]
    
    missing = []
    for file_path in demo_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"⚠️  Missing demo files: {', '.join(missing)}")
        print("   Demo files are included in the repository")
        return False
    
    print("✅ Demo files found")
    return True

def show_next_steps(has_api_key):
    """Show next steps for user"""
    print()
    print("🎯 Setup Complete! Next Steps:")
    print()
    
    if not has_api_key:
        print("1. Set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    print("2. Run the system:")
    print("   python run.py")
    print()
    
    print("3. Try demo mode:")
    print("   make demo")
    print()
    
    print("4. Run tests:")
    print("   make test")
    print()
    
    print("5. Explore features:")
    print("   python memory_navigator.py    # Memory navigation")
    print("   python memory_manager.py      # Analytics")
    print("   make benchmark               # Performance tests")
    print()
    
    print("📚 Documentation:")
    print("   docs/ARCHITECTURE.md  - System architecture")
    print("   docs/TESTING.md       - Testing guide")
    print("   GITHUB_README.md      - Complete usage guide")
    print()

def main():
    """Main setup process"""
    print_header()
    
    # Validation steps
    check_python_version()
    has_api_key = check_openai_key()
    
    if not validate_structure():
        print("❌ Setup failed: Invalid project structure")
        sys.exit(1)
    
    if not create_demo_files():
        print("⚠️  Some demo files are missing")
    
    # Installation
    if not install_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    # Success
    print()
    print("🎉 Setup completed successfully!")
    show_next_steps(has_api_key)

if __name__ == "__main__":
    main()
