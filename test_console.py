#!/usr/bin/env python3
"""
Test script to verify skill_console.py works
"""

print("🧪 Testing skill_console.py...")

try:
    import skill_console
    print("✅ Import successful")
    
    # Test initialization
    console = skill_console.SkillConsole()
    print("✅ Console creation successful")
    
    # Test if GitHub is configured
    if console.github and console.github.github:
        print("✅ GitHub configured and ready")
    else:
        print("❌ GitHub not configured")
    
    print("🎉 skill_console.py is working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
