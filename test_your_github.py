#!/usr/bin/env python3
"""
Test Your GitHub Analysis
Direct test of GitHub analysis features using your token
"""

import os
from dotenv import load_dotenv
from github import Github

# Load environment
load_dotenv()

def test_your_github():
    """Test analysis features on your GitHub account"""
    
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not token:
        print("❌ No GitHub token found in .env file")
        return
    
    try:
        g = Github(token)
        user = g.get_user()
        
        print(f"🚀 Testing GitHub Analysis for: {user.login}")
        print(f"📊 Public repos: {user.public_repos}")
        print(f"👥 Followers: {user.followers}")
        print(f"👤 Following: {user.following}")
        print("-" * 50)
        
        # Get your repositories
        print("\n📁 YOUR REPOSITORIES:")
        repos = list(user.get_repos(type='all'))[:10]  # Limit to 10
        
        for i, repo in enumerate(repos, 1):
            print(f"{i}. {repo.name} ⭐{repo.stargazers_count} 🍴{repo.forks_count}")
            
            # Get languages
            try:
                languages = repo.get_languages()
                if languages:
                    top_langs = list(languages.keys())[:3]
                    print(f"   Languages: {', '.join(top_langs)}")
            except:
                pass
            
            # Get collaborators (for repos you own)
            if repo.owner.login == user.login:
                try:
                    collaborators = list(repo.get_collaborators())
                    if len(collaborators) > 1:  # More than just you
                        collab_names = [c.login for c in collaborators if c.login != user.login]
                        if collab_names:
                            print(f"   👥 Collaborators: {', '.join(collab_names[:5])}")
                except:
                    pass
            
            print()
        
        # Test organization analysis if you're part of any
        print("\n🏢 YOUR ORGANIZATIONS:")
        try:
            orgs = list(user.get_orgs())
            if orgs:
                for org in orgs[:5]:
                    print(f"• {org.login}")
                    try:
                        org_repos = list(org.get_repos(type='public'))[:3]
                        for repo in org_repos:
                            print(f"  - {repo.name} ⭐{repo.stargazers_count}")
                    except:
                        pass
            else:
                print("No organizations found")
        except Exception as e:
            print(f"Could not fetch organizations: {e}")
        
        # Test specific repository analysis
        if repos:
            print(f"\n🔍 DETAILED ANALYSIS OF: {repos[0].name}")
            repo = repos[0]
            
            # Contributors
            try:
                contributors = list(repo.get_contributors())[:10]
                print(f"👥 Contributors ({len(contributors)}):")
                for contrib in contributors:
                    print(f"  • {contrib.login} - {contrib.contributions} contributions")
            except Exception as e:
                print(f"Could not get contributors: {e}")
            
            # Recent commits
            try:
                commits = list(repo.get_commits())[:5]
                print(f"\n📝 Recent commits:")
                for commit in commits:
                    author = commit.author.login if commit.author else "Unknown"
                    print(f"  • {author}: {commit.commit.message[:50]}...")
            except Exception as e:
                print(f"Could not get commits: {e}")
        
        print("\n✅ GitHub analysis test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_your_github()
