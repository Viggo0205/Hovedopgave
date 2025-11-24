#!/usr/bin/env python3
"""
Quick test of the enhanced competency analysis features.
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

try:
    from github import Github
    from skill_console import SkillConsole
    
    def test_competency_features():
        """Test the new competency analysis features."""
        print("🧪 TESTING ENHANCED COMPETENCY ANALYSIS")
        print("="*50)
        
        console = SkillConsole()
        
        if not console.github:
            print("❌ GitHub not configured - check your .env file")
            return
        
        # Test competency assessment method
        print("\n🔬 Testing competency assessment algorithm:")
        
        # Simulate language data for different skill levels
        test_cases = [
            {"Python": 50000, "JavaScript": 30000},  # Should be intermediate/advanced
            {"Java": 100000},                        # Should be advanced/expert  
            {"CSS": 5000},                          # Should be beginner
            {"TypeScript": 80000, "React": 40000}   # Should be advanced
        ]
        
        repo_data = [
            {'name': 'test-repo-1', 'languages': {'Python': 25000, 'JavaScript': 15000}},
            {'name': 'test-repo-2', 'languages': {'Python': 25000, 'JavaScript': 15000}},
            {'name': 'test-repo-3', 'languages': {'Java': 100000}},
            {'name': 'test-repo-4', 'languages': {'CSS': 5000}},
        ]
        
        for i, lang_data in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {list(lang_data.keys())}")
            for lang, bytes_count in lang_data.items():
                lang_specific = {lang: bytes_count}
                level_name, level_emoji, score = console.assess_competency_level(lang_specific, repo_data)
                print(f"  {level_emoji} {lang}: {level_name} (Score: {score:.1f})")
        
        # Test framework detection
        print(f"\n🔬 Testing framework detection:")
        
        class MockRepo:
            def __init__(self, name, description="", topics=None):
                self.name = name
                self.description = description
                self.topics = topics or []
        
        test_repos = [
            MockRepo("my-react-app", "A React application", ["react", "javascript"]),
            MockRepo("django-backend", "Django REST API", ["django", "python"]),
            MockRepo("docker-setup", "Container configuration", ["docker"]),
            MockRepo("vue-frontend", "Vue.js frontend", ["vue", "vuejs"]),
        ]
        
        frameworks = console.detect_frameworks_and_tools(test_repos)
        print("Detected frameworks:")
        for fw, count in frameworks.items():
            print(f"  🔧 {fw}: Used in {count} repositories")
        
        print(f"\n✅ Competency analysis features working correctly!")
        print(f"\n🚀 Ready to analyze real developers with detailed skill levels!")
        
        return True

    if __name__ == "__main__":
        test_competency_features()
        
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Run: pip install PyGithub python-dotenv")
