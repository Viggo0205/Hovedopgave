#!/usr/bin/env python3
"""
Test GitHub API access
"""

from dotenv import load_dotenv
import os
import requests
import json

def test_github_api():
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("🔍 Testing GitHub API access...")
    print(f"Token: {token[:10]}...")
    
    # Test user info
    try:
        user_response = requests.get('https://api.github.com/user', headers=headers)
        print(f"\n=== USER INFO ===")
        print(f"Status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"✅ Authentication successful!")
            print(f"Username: {user_data.get('login')}")
            print(f"Name: {user_data.get('name')}")
            print(f"Public repos: {user_data.get('public_repos')}")
            print(f"Followers: {user_data.get('followers')}")
            print(f"Company: {user_data.get('company')}")
            
            # Test repositories access
            repos_response = requests.get('https://api.github.com/user/repos?per_page=5', headers=headers)
            if repos_response.status_code == 200:
                repos = repos_response.json()
                print(f"\n=== RECENT REPOSITORIES ===")
                for repo in repos[:3]:
                    print(f"📁 {repo['name']} - {repo.get('language', 'No language')}")
            
        else:
            print(f"❌ Authentication failed: {user_response.status_code}")
            print(f"Response: {user_response.text}")
            return False
            
        print(f"\n=== RATE LIMITS ===")
        print(f"Remaining: {user_response.headers.get('X-RateLimit-Remaining')}/5000")
        print(f"Reset time: {user_response.headers.get('X-RateLimit-Reset')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing GitHub API: {e}")
        return False

if __name__ == "__main__":
    test_github_api()