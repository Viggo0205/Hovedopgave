#!/usr/bin/env python3
"""
Direct Collaborator Analysis Test
"""

import os
from dotenv import load_dotenv
from github import Github
from collections import Counter

load_dotenv()

def test_collaborator_analysis():
    """Direct test of collaborator analysis"""
    
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not token:
        print("❌ No GitHub token found")
        return
    
    try:
        print("🔧 Connecting to GitHub...")
        github = Github(token)
        user = github.get_user()
        
        print(f"🚀 ANALYZING COLLABORATORS FOR: {user.login}")
        print("="*60)
        
        # Get your repositories
        repos = list(user.get_repos(type='all'))
        print(f"📁 Found {len(repos)} repositories to scan")
        
        all_collaborators = set()
        repo_collaborators = {}
        
        print(f"\n🔍 Scanning for collaborators...")
        for i, repo in enumerate(repos[:10], 1):  # Limit to first 10 repos
            print(f"[{i:2d}] 📂 {repo.name}")
            
            try:
                # Get direct collaborators
                collaborators = list(repo.get_collaborators())
                repo_collabs = [c.login for c in collaborators if c.login != user.login]
                
                # Get contributors
                try:
                    contributors = list(repo.get_contributors())
                    contrib_names = [c.login for c in contributors[:3] if c.login != user.login]
                    repo_collabs.extend(contrib_names)
                except:
                    pass
                
                if repo_collabs:
                    unique_collabs = list(set(repo_collabs))
                    print(f"    👥 {len(unique_collabs)} collaborators: {', '.join(unique_collabs[:3])}")
                    all_collaborators.update(unique_collabs)
                    repo_collaborators[repo.name] = unique_collabs
                else:
                    print(f"    📝 No external collaborators")
                    
            except Exception as e:
                print(f"    ⚠️ Error: {e}")
        
        if not all_collaborators:
            print("❌ No collaborators found")
            return
        
        print(f"\n🎯 FOUND {len(all_collaborators)} UNIQUE COLLABORATORS:")
        print("-" * 60)
        
        # List all collaborators
        for i, collaborator in enumerate(sorted(all_collaborators), 1):
            print(f"{i:2d}. {collaborator}")
        
        # Analyze top 5 collaborators
        print(f"\n📊 ANALYZING TOP 5 COLLABORATORS:")
        print("="*60)
        
        top_collaborators = sorted(all_collaborators)[:5]
        
        for i, collaborator in enumerate(top_collaborators, 1):
            print(f"\n[{i}] 👤 {collaborator}")
            print("-" * 30)
            
            try:
                collab_user = github.get_user(collaborator)
                
                print(f"📛 Name: {collab_user.name if collab_user.name else 'Not set'}")
                print(f"🏢 Company: {collab_user.company if collab_user.company else 'Not set'}")
                print(f"📍 Location: {collab_user.location if collab_user.location else 'Not set'}")
                print(f"📊 Public repos: {collab_user.public_repos}")
                print(f"👥 Followers: {collab_user.followers}")
                
                # Show which repos they collaborated on with you
                shared_repos = [repo for repo, collabs in repo_collaborators.items() if collaborator in collabs]
                if shared_repos:
                    print(f"🤝 Collaborated on: {', '.join(shared_repos[:2])}")
                    if len(shared_repos) > 2:
                        print(f"    ... and {len(shared_repos) - 2} more repos")
                
            except Exception as e:
                print(f"❌ Error analyzing {collaborator}: {e}")
        
        print(f"\n✅ Analysis complete!")
        print(f"Found {len(all_collaborators)} total collaborators across {len(repo_collaborators)} repositories.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_collaborator_analysis()
