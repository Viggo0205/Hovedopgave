#!/usr/bin/env python3
"""Simple GitHub Test"""

import os
print("Starting GitHub test...")

# Check environment
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("GITHUB_ACCESS_TOKEN")
print(f"Token loaded: {'Yes' if token else 'No'}")
if token:
    print(f"Token starts with: {token[:8]}...")

# Test GitHub
try:
    from github import Github
    print("GitHub library imported successfully")
    
    g = Github(token)
    user = g.get_user()
    print(f"Connected as: {user.login}")
    print(f"Your name: {user.name}")
    
    # Get your repos
    repos = list(user.get_repos(type='owner'))
    print(f"You have {len(repos)} repositories")
    
    if repos:
        repo = repos[0]
        print(f"First repo: {repo.name}")
        
        # Get collaborators
        try:
            collaborators = list(repo.get_collaborators())
            print(f"Collaborators in {repo.name}: {len(collaborators)}")
            for collab in collaborators:
                print(f"  - {collab.login}")
        except Exception as e:
            print(f"Could not get collaborators: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
