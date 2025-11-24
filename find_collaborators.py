#!/usr/bin/env python3
"""
Quick Collaborator Finder for Viggo0205
Simple script to find collaborators using basic GitHub API
"""

import os
from dotenv import load_dotenv
from github import Github
from collections import defaultdict, Counter

load_dotenv()

def find_collaborators():
    """Find all collaborators from your repositories"""
    
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not token:
        print("❌ No GitHub token found")
        return
    
    try:
        print("🚀 FINDING YOUR COLLABORATORS")
        print("=" * 50)
        
        g = Github(token)
        user = g.get_user()  # This gets your own profile (Viggo0205)
        
        print(f"👤 Analyzing repositories for: {user.login}")
        
        # Get your repositories
        repos = list(user.get_repos(type='owner'))  # Only repos you own
        print(f"📁 Found {len(repos)} owned repositories")
        
        all_collaborators = {}
        repo_collaborations = defaultdict(list)
        
        for i, repo in enumerate(repos, 1):
            print(f"\n[{i:2d}/{len(repos)}] 📂 {repo.name}")
            
            collaborators_in_repo = []
            
            # Method 1: Direct collaborators
            try:
                collaborators = list(repo.get_collaborators())
                for collab in collaborators:
                    if collab.login != user.login:  # Not yourself
                        collaborators_in_repo.append(collab.login)
                        if collab.login not in all_collaborators:
                            all_collaborators[collab.login] = {
                                'name': collab.name,
                                'company': collab.company,
                                'location': collab.location,
                                'repos': collab.public_repos,
                                'followers': collab.followers,
                                'bio': collab.bio
                            }
                        repo_collaborations[collab.login].append(repo.name)
                
                if collaborators_in_repo:
                    print(f"    👥 Collaborators: {', '.join(collaborators_in_repo)}")
            
            except Exception as e:
                print(f"    ⚠️  Could not get collaborators: {e}")
            
            # Method 2: Contributors (people who committed)
            try:
                contributors = list(repo.get_contributors())
                contributor_names = []
                for contrib in contributors:
                    if contrib.login != user.login and contrib.login not in collaborators_in_repo:
                        contributor_names.append(contrib.login)
                        if contrib.login not in all_collaborators:
                            all_collaborators[contrib.login] = {
                                'name': contrib.name,
                                'company': contrib.company,
                                'location': contrib.location,
                                'repos': contrib.public_repos,
                                'followers': contrib.followers,
                                'bio': contrib.bio
                            }
                        repo_collaborations[contrib.login].append(repo.name)
                
                if contributor_names:
                    print(f"    🔧 Contributors: {', '.join(contributor_names[:5])}")
                    if len(contributor_names) > 5:
                        print(f"        ... and {len(contributor_names) - 5} more")
            
            except Exception as e:
                print(f"    ⚠️  Could not get contributors: {e}")
        
        # Summary
        print(f"\n🎯 SUMMARY")
        print("=" * 50)
        print(f"Total unique collaborators found: {len(all_collaborators)}")
        
        if all_collaborators:
            print(f"\n👥 YOUR COLLABORATORS:")
            print("-" * 50)
            
            for i, (username, info) in enumerate(sorted(all_collaborators.items()), 1):
                print(f"{i:2d}. {username}")
                if info['name']:
                    print(f"    📛 Name: {info['name']}")
                if info['company']:
                    print(f"    🏢 Company: {info['company']}")
                if info['location']:
                    print(f"    📍 Location: {info['location']}")
                print(f"    📊 Public repos: {info['repos']}")
                print(f"    👥 Followers: {info['followers']}")
                
                # Show which repos you collaborated on
                shared_repos = repo_collaborations[username]
                print(f"    🤝 Collaborated on: {', '.join(shared_repos[:3])}")
                if len(shared_repos) > 3:
                    print(f"        ... and {len(shared_repos) - 3} more repos")
                print()
            
            # Analytics
            print("📈 COLLABORATION ANALYTICS:")
            print("-" * 30)
            
            # Companies
            companies = Counter()
            locations = Counter()
            for info in all_collaborators.values():
                if info['company']:
                    companies[info['company']] += 1
                if info['location']:
                    locations[info['location']] += 1
            
            if companies:
                print("🏢 Companies your collaborators work for:")
                for company, count in companies.most_common(5):
                    print(f"   • {company} ({count} people)")
            
            if locations:
                print("\n📍 Locations of your collaborators:")
                for location, count in locations.most_common(5):
                    print(f"   • {location} ({count} people)")
            
            # Most collaborative repos
            repo_counts = Counter()
            for repos_list in repo_collaborations.values():
                for repo in repos_list:
                    repo_counts[repo] += 1
            
            if repo_counts:
                print(f"\n🤝 Your most collaborative repositories:")
                for repo, collab_count in repo_counts.most_common(5):
                    print(f"   • {repo} ({collab_count} collaborators)")
        
        else:
            print("No collaborators found in your repositories.")
            print("This might mean:")
            print("• Your repositories are mostly solo projects")
            print("• Collaborators are added through other means")
            print("• API limitations prevented finding all collaborators")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_collaborators()
