#!/usr/bin/env python3
"""
Collaborator Analysis for Viggo0205
Find all collaborators you've worked with and analyze their skills
"""

import os
import sys
import asyncio
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from developer_skill_analyzer.analyzers.github_analyzer import GitHubAnalyzer

load_dotenv()

class CollaboratorAnalyzer:
    def __init__(self):
        self.token = os.getenv("GITHUB_ACCESS_TOKEN")
        if not self.token:
            raise Exception("No GitHub token found in .env")
        
        self.analyzer = GitHubAnalyzer(self.token)
        self.collaborators_found = {}
        self.collaborator_skills = {}
    
    async def analyze_your_collaborators(self):
        """Find and analyze all your collaborators and their skills"""
        
        print("🚀 ANALYZING YOUR COLLABORATORS")
        print("=" * 60)
        
        # First, get your own profile and repositories
        your_username = "Viggo0205"  # Your GitHub username
        print(f"📊 Analyzing repositories for: {your_username}")
        
        try:
            user = self.analyzer.github.get_user(your_username)
            
            # Get all your repositories
            print("🔍 Scanning your repositories for collaborators...")
            repos = list(user.get_repos(type='all'))
            print(f"📁 Found {len(repos)} repositories to analyze")
            
            all_collaborators = set()
            repo_collaborators = defaultdict(list)
            
            # Analyze each repository for collaborators
            for i, repo in enumerate(repos, 1):
                print(f"[{i:2d}/{len(repos)}] 📂 {repo.name}")
                
                try:
                    # Get direct collaborators
                    collaborators = list(repo.get_collaborators())
                    repo_collabs = [c.login for c in collaborators if c.login != your_username]
                    
                    if repo_collabs:
                        print(f"    👥 Direct collaborators: {', '.join(repo_collabs)}")
                        all_collaborators.update(repo_collabs)
                        repo_collaborators[repo.name] = repo_collabs
                    
                    # Get contributors (people who have committed)
                    try:
                        contributors = list(repo.get_contributors())
                        contrib_names = [c.login for c in contributors[:10] if c.login != your_username]
                        
                        if contrib_names:
                            print(f"    🔧 Contributors: {', '.join(contrib_names[:5])}")
                            all_collaborators.update(contrib_names)
                            repo_collaborators[repo.name].extend(contrib_names)
                    except Exception as e:
                        print(f"    ⚠️  Could not get contributors: {e}")
                    
                    # Check recent commits for co-authors
                    try:
                        commits = list(repo.get_commits())[:20]  # Recent commits
                        for commit in commits:
                            if commit.author and commit.author.login != your_username:
                                all_collaborators.add(commit.author.login)
                    except Exception as e:
                        pass
                        
                except Exception as e:
                    print(f"    ❌ Error analyzing {repo.name}: {e}")
                    continue
            
            print(f"\n🎯 FOUND {len(all_collaborators)} UNIQUE COLLABORATORS")
            print("=" * 60)
            
            if not all_collaborators:
                print("No collaborators found.")
                return
            
            # Now analyze each collaborator's skills
            print("🧠 ANALYZING COLLABORATOR SKILLS...")
            print("=" * 60)
            
            collaborator_analyses = {}
            
            for i, collaborator in enumerate(sorted(all_collaborators), 1):
                print(f"\n[{i:2d}/{len(all_collaborators)}] 👤 {collaborator}")
                print("-" * 40)
                
                try:
                    # Analyze the collaborator's GitHub profile
                    analysis = await self.analyzer.analyze_developer(
                        collaborator,
                        time_range_months=12,
                        include_contributions=False  # Focus on their own repos
                    )
                    
                    collaborator_analyses[collaborator] = analysis
                    
                    # Extract key skills and info
                    profile = analysis.get('profile_data', {})
                    languages = analysis.get('language_distribution', {})
                    repos_count = analysis.get('total_repositories', 0)
                    
                    print(f"📛 Name: {profile.get('name', 'Not set')}")
                    print(f"🏢 Company: {profile.get('company', 'Not set')}")
                    print(f"📍 Location: {profile.get('location', 'Not set')}")
                    print(f"📊 Public repos: {repos_count}")
                    print(f"⭐ Total stars: {analysis.get('total_stars_earned', 0)}")
                    
                    if languages:
                        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
                        print(f"💻 Top languages: {', '.join([f'{lang} ({perc:.1%})' for lang, perc in top_languages])}")
                    
                    # Show which repos you collaborated on
                    shared_repos = []
                    for repo_name, collabs in repo_collaborators.items():
                        if collaborator in collabs:
                            shared_repos.append(repo_name)
                    
                    if shared_repos:
                        print(f"🤝 Collaborated on: {', '.join(shared_repos[:3])}")
                        if len(shared_repos) > 3:
                            print(f"    ... and {len(shared_repos) - 3} more")
                    
                except Exception as e:
                    print(f"❌ Could not analyze {collaborator}: {e}")
                    continue
            
            # Generate summary report
            await self._generate_summary_report(collaborator_analyses, repo_collaborators)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    async def _generate_summary_report(self, analyses, repo_collaborators):
        """Generate a summary report of all collaborators and their skills"""
        
        print("\n" + "=" * 60)
        print("📈 COLLABORATOR SKILLS SUMMARY")
        print("=" * 60)
        
        # Aggregate language skills
        all_languages = Counter()
        companies = Counter()
        locations = Counter()
        
        for username, analysis in analyses.items():
            languages = analysis.get('language_distribution', {})
            for lang, percentage in languages.items():
                all_languages[lang] += percentage
            
            profile = analysis.get('profile_data', {})
            if profile.get('company'):
                companies[profile['company']] += 1
            if profile.get('location'):
                locations[profile['location']] += 1
        
        # Top languages across all collaborators
        if all_languages:
            print("\n💻 TOP LANGUAGES AMONG YOUR COLLABORATORS:")
            for lang, total_skill in all_languages.most_common(10):
                print(f"   {lang:15} - Used by collaborators (total skill: {total_skill:.2f})")
        
        # Most common companies
        if companies:
            print(f"\n🏢 COMPANIES YOUR COLLABORATORS WORK FOR:")
            for company, count in companies.most_common(5):
                print(f"   {company:30} - {count} collaborator(s)")
        
        # Most common locations
        if locations:
            print(f"\n📍 COLLABORATOR LOCATIONS:")
            for location, count in locations.most_common(5):
                print(f"   {location:30} - {count} collaborator(s)")
        
        # Most active repositories for collaboration
        repo_collab_count = {repo: len(collabs) for repo, collabs in repo_collaborators.items() if collabs}
        if repo_collab_count:
            print(f"\n🤝 YOUR MOST COLLABORATIVE REPOSITORIES:")
            sorted_repos = sorted(repo_collab_count.items(), key=lambda x: x[1], reverse=True)
            for repo, count in sorted_repos[:5]:
                print(f"   {repo:30} - {count} collaborator(s)")
        
        # Skill recommendations
        print(f"\n🎯 SKILL INSIGHTS:")
        if all_languages:
            top_collab_languages = [lang for lang, _ in all_languages.most_common(3)]
            print(f"   • Your collaborators are strongest in: {', '.join(top_collab_languages)}")
            print(f"   • Consider deepening skills in these languages for better collaboration")
        
        print(f"\n✅ Analysis complete! Found {len(analyses)} collaborators across your repositories.")

async def main():
    """Main function to run the collaborator analysis"""
    try:
        analyzer = CollaboratorAnalyzer()
        await analyzer.analyze_your_collaborators()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
