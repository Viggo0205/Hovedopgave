#!/usr/bin/env python3
"""
Simple GitHub connection test - fresh start
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_github():
    """Test basic GitHub connection."""
    try:
        print("🧪 Basic GitHub Connection Test")
        print("=" * 40)
        
        # Test 1: Check token
        print("1️⃣ Checking environment...")
        github_token = os.environ.get('GITHUB_TOKEN')
        
        if not github_token:
            print("❌ GITHUB_TOKEN not found in environment")
            return False
        else:
            print(f"✅ GitHub token found (preview: {github_token[:8]}...)")
        
        # Test 2: Import our config
        print("\n2️⃣ Testing imports...")
        try:
            from developer_skill_analyzer.config import Config
            config = Config()
            print(f"✅ Config loaded, token configured: {bool(config.github_token)}")
        except Exception as e:
            print(f"❌ Config import failed: {e}")
            return False
        
        # Test 3: Test GitHub analyzer
        print("\n3️⃣ Testing GitHub analyzer...")
        try:
            from developer_skill_analyzer.analyzers.github_analyzer import GitHubAnalyzer
            analyzer = GitHubAnalyzer(config.github_token)
            
            # Get current user
            user = analyzer.github.get_user()
            print(f"✅ GitHub API works! User: {user.login}")
            print(f"   Public repos: {user.public_repos}")
            
        except Exception as e:
            print(f"❌ GitHub analyzer failed: {e}")
            return False
        
        print("\n🎉 Basic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_github()
    if success:
        print("\n✅ GitHub connection is working!")
    else:
        print("\n❌ Fix the issues above")