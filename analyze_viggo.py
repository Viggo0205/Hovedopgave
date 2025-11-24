#!/usr/bin/env python3
"""
Quick GitHub Analysis for Viggo0205
Direct analysis of your GitHub with detailed output
"""

import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

def analyze_viggo_github():
    """Analyze Viggo0205's GitHub account with detailed output"""
    
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not token:
        print("❌ No GitHub token found")
        return
    
    try:
        print("🔧 Connecting to GitHub...")
        g = Github(token)
        user = g.get_user()
        
        print(f"🚀 ANALYZING: {user.login}")
        print("=" * 50)
        
        # Basic info
        print(f"👤 Name: {user.name if user.name else 'Not set'}")
        print(f"📧 Email: {user.email if user.email else 'Not public'}")
        print(f"📍 Location: {user.location if user.location else 'Not set'}")
        print(f"🏢 Company: {user.company if user.company else 'Not set'}")
        print(f"📝 Bio: {user.bio if user.bio else 'Not set'}")
        print(f"📊 Public Repos: {user.public_repos}")
        print(f"👥 Followers: {user.followers}")
        print(f"👤 Following: {user.following}")
        
        print("\n📁 YOUR REPOSITORIES (Top 10):")
        print("-" * 50)
        
        # Get repos
        repos = list(user.get_repos(type='owner', sort='updated'))[:10]
        
        languages_total = {}
        total_stars = 0
        total_forks = 0
        all_collaborators = set()
        
        for i, repo in enumerate(repos, 1):
            print(f"\n{i:2d}. {repo.name}")
            print(f"    ⭐ Stars: {repo.stargazers_count}")
            print(f"    🍴 Forks: {repo.forks_count}")
            print(f"    📅 Updated: {repo.updated_at.strftime('%Y-%m-%d')}")
            
            total_stars += repo.stargazers_count
            total_forks += repo.forks_count
            
            if repo.description:
                desc = repo.description[:70] + "..." if len(repo.description) > 70 else repo.description
                print(f"    📝 {desc}")
            
            # Languages
            try:
                languages = repo.get_languages()
                if languages:
                    top_langs = list(languages.keys())[:3]
                    print(f"    💻 Languages: {', '.join(top_langs)}")
                    
                    # Add to total
                    for lang, bytes_count in languages.items():
                        languages_total[lang] = languages_total.get(lang, 0) + bytes_count
            except Exception as e:
                print(f"    ⚠️ Languages: Error - {e}")
            
            # Try to get collaborators
            try:
                collabs = list(repo.get_collaborators())
                if len(collabs) > 1:
                    collab_names = [c.login for c in collabs if c.login != user.login]
                    if collab_names:
                        print(f"    👥 Collaborators: {', '.join(collab_names[:3])}")
                        all_collaborators.update(collab_names)
            except Exception as e:
                print(f"    ⚠️ Collaborators: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📈 SUMMARY")
        print("=" * 50)
        print(f"🎯 Total Stars: {total_stars}")
        print(f"🎯 Total Forks: {total_forks}")
        
        if all_collaborators:
            print(f"👥 Unique Collaborators ({len(all_collaborators)}): {', '.join(sorted(all_collaborators)[:5])}")
        
        # Top languages
        if languages_total:
            print("\n💻 TOP PROGRAMMING LANGUAGES:")
            sorted_langs = sorted(languages_total.items(), key=lambda x: x[1], reverse=True)[:7]
            total_bytes = sum(languages_total.values())
            
            for lang, bytes_count in sorted_langs:
                percentage = (bytes_count / total_bytes) * 100
                bar_length = int(percentage / 5)  # Scale for display
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"   {lang:15} {percentage:5.1f}% {bar}")
        
        print("\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_viggo_github()
