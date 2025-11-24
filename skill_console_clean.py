#!/usr/bin/env python3
"""
Developer Skill Analyzer Console with Collaborator Analysis

Run this directly: python skill_console_clean.py
"""

import os
import sys
import asyncio
from datetime import datetime
from collections import defaultdict, Counter

# Check for required packages
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    print("❌ PyGithub not installed. Install with: pip install PyGithub python-dotenv")
    GITHUB_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class SkillConsole:
    def __init__(self):
        print("\n🔧 Setting up console...")
        
        # Get environment variables
        self.github_token = os.getenv("GITHUB_ACCESS_TOKEN")
        
        # Initialize GitHub if available
        self.github = None
        if GITHUB_AVAILABLE and self.github_token:
            try:
                self.github = Github(self.github_token)
                user = self.github.get_user()
                print(f"✅ GitHub: Connected as {user.login}")
            except Exception as e:
                print(f"❌ GitHub: {e}")
                self.github = None
        else:
            print("❌ GitHub: Not configured")

    def assess_competency_level(self, language_data, repos_analyzed):
        """
        Assess competency level based on usage patterns, repository count, and code volume.
        Returns: (level_name, level_emoji, score)
        """
        if not language_data:
            return "No Data", "❓", 0
        
        # Calculate metrics
        total_bytes = sum(language_data.values())
        repo_count = len([repo for repo in repos_analyzed if any(lang in language_data for lang in repo.get('languages', {}).keys())])
        
        # Scoring algorithm
        byte_score = min(total_bytes / 10000, 50)  # Max 50 points for code volume
        repo_score = min(repo_count * 10, 30)     # Max 30 points for repo diversity
        consistency_score = min(len(language_data), 20)  # Max 20 points for consistency
        
        total_score = byte_score + repo_score + consistency_score
        
        if total_score >= 80:
            return "Expert", "🏆", total_score
        elif total_score >= 60:
            return "Advanced", "🥇", total_score
        elif total_score >= 40:
            return "Intermediate", "🥈", total_score
        elif total_score >= 20:
            return "Beginner", "🥉", total_score
        else:
            return "Learning", "📚", total_score

    def detect_frameworks_and_tools(self, repos):
        """
        Detect frameworks and tools from repository analysis.
        Returns dict of detected technologies with usage indicators.
        """
        frameworks = {}
        
        for repo in repos:
            try:
                # Check repository topics/tags
                topics = getattr(repo, 'topics', []) or []
                
                # Check repository name and description for framework indicators
                repo_text = f"{repo.name} {repo.description or ''}".lower()
                
                # Framework detection patterns
                framework_patterns = {
                    'React': ['react', 'jsx', 'create-react-app'],
                    'Vue.js': ['vue', 'vuejs', 'nuxt'],
                    'Angular': ['angular', 'ng-', '@angular'],
                    'Node.js': ['node', 'nodejs', 'express', 'npm'],
                    'Django': ['django', 'python-web'],
                    'Flask': ['flask', 'python-flask'],
                    'Spring': ['spring', 'spring-boot', 'java-spring'],
                    'Laravel': ['laravel', 'php-laravel'],
                    '.NET': ['dotnet', '.net', 'csharp', 'asp.net'],
                    'Docker': ['docker', 'dockerfile', 'container'],
                    'Kubernetes': ['kubernetes', 'k8s', 'kubectl'],
                    'AWS': ['aws', 'amazon-web-services', 'lambda'],
                    'TensorFlow': ['tensorflow', 'tf', 'machine-learning'],
                    'PyTorch': ['pytorch', 'torch', 'deep-learning'],
                    'MongoDB': ['mongodb', 'mongo', 'nosql'],
                    'PostgreSQL': ['postgresql', 'postgres', 'sql'],
                    'Redis': ['redis', 'cache', 'key-value'],
                    'GraphQL': ['graphql', 'apollo', 'relay']
                }
                
                # Check patterns in topics and text
                for framework, patterns in framework_patterns.items():
                    if any(pattern in topics or pattern in repo_text for pattern in patterns):
                        frameworks[framework] = frameworks.get(framework, 0) + 1
                        
            except Exception:
                pass
                
        return frameworks

    def menu(self):
        print("\n" + "="*60)
        print("🎯 DEVELOPER SKILL ANALYZER")
        print("="*60)
        print("📋 QUICK LISTS:")
        print("1. 👥 Popular Tech Companies & Their Collaborators")
        print("2. 🧠 Top Developers & Their Skills")
        print("3. 🏆 Trending Repositories & Contributors")
        print("")
        print("🔍 PERSONAL ANALYSIS:")
        print("4. 🏠 Analyze YOUR GitHub Account")
        print("5. 🤝 Find ALL Your Collaborators & Their Skills")
        print("6. 📊 Analyze Specific Developer")
        print("7. ⚙️ Check Setup")
        print("0. Exit")
        print("-"*60)

    def get_popular_companies_collaborators(self):
        """Quick analysis of popular tech companies."""
        if not self.github:
            print("❌ GitHub not configured")
            return
        
        print("\n👥 POPULAR TECH COMPANIES ANALYSIS")
        print("="*50)
        
        companies = ["microsoft", "google", "facebook", "netflix", "github"]
        
        for company in companies:
            try:
                org = self.github.get_organization(company)
                print(f"\n🏢 {company.upper()}")
                print(f"   📊 Public repos: {org.public_repos}")
                print(f"   👥 Public members: {org.public_members}")
                
                # Get a few top repositories
                repos = list(org.get_repos(sort="stars"))[:3]
                for repo in repos:
                    print(f"   ⭐ {repo.name}: {repo.stargazers_count} stars")
                    
            except Exception as e:
                print(f"❌ Could not analyze {company}: {e}")

    def analyze_your_github(self):
        """Analyze your own GitHub account."""
        if not self.github:
            print("❌ GitHub not configured")
            return
        
        try:
            print("\n🏠 ANALYZING YOUR GITHUB ACCOUNT")
            print("="*50)
            
            user = self.github.get_user()
            print(f"👤 Account: {user.login}")
            print(f"📛 Name: {user.name if user.name else 'Not set'}")
            print(f"🏢 Company: {user.company if user.company else 'Not set'}")
            print(f"📍 Location: {user.location if user.location else 'Not set'}")
            print(f"📊 Public repos: {user.public_repos}")
            print(f"👥 Followers: {user.followers}")
            print(f"👤 Following: {user.following}")
            
            # Analyze repositories
            print(f"\n📁 YOUR TOP REPOSITORIES:")
            repos = list(user.get_repos(type='owner', sort='updated'))[:10]
            
            total_stars = 0
            languages_used = {}
            
            for i, repo in enumerate(repos, 1):
                print(f"{i:2d}. {repo.name}")
                print(f"    ⭐ Stars: {repo.stargazers_count}, 🍴 Forks: {repo.forks_count}")
                total_stars += repo.stargazers_count
                
                # Get languages
                try:
                    languages = repo.get_languages()
                    for lang, bytes_count in languages.items():
                        languages_used[lang] = languages_used.get(lang, 0) + bytes_count
                except:
                    pass
            
            print(f"\n📈 SUMMARY:")
            print(f"🎯 Total Stars Earned: {total_stars}")
            
            if languages_used:
                print(f"\n💻 YOUR PROGRAMMING LANGUAGES:")
                total_bytes = sum(languages_used.values())
                sorted_langs = sorted(languages_used.items(), key=lambda x: x[1], reverse=True)[:8]
                for lang, bytes_count in sorted_langs:
                    percentage = (bytes_count / total_bytes) * 100
                    print(f"   {lang:15}: {percentage:5.1f}%")
            
        except Exception as e:
            print(f"❌ Error analyzing your GitHub: {e}")

    def analyze_collaborators(self):
        """Find and analyze all your collaborators and their skills."""
        if not self.github:
            print("❌ GitHub not configured")
            return
        
        try:
            print("\n🤝 ANALYZING YOUR COLLABORATORS")
            print("="*60)
            
            user = self.github.get_user()
            your_username = user.login
            print(f"📊 Scanning repositories for: {your_username}")
            
            # Get your repositories
            repos = list(user.get_repos(type='all'))
            print(f"📁 Found {len(repos)} repositories to scan")
            
            all_collaborators = set()
            repo_collaborators = {}
            
            print(f"\n🔍 Scanning for collaborators...")
            for i, repo in enumerate(repos[:15], 1):  # Limit to avoid rate limits
                print(f"[{i:2d}] 📂 {repo.name}")
                
                try:
                    # Get direct collaborators
                    collaborators = list(repo.get_collaborators())
                    repo_collabs = [c.login for c in collaborators if c.login != your_username]
                    
                    # Get contributors (people who have committed)
                    try:
                        contributors = list(repo.get_contributors())
                        contrib_names = [c.login for c in contributors[:5] if c.login != your_username]
                        repo_collabs.extend(contrib_names)
                    except:
                        pass
                    
                    if repo_collabs:
                        unique_collabs = list(set(repo_collabs))
                        print(f"    👥 {len(unique_collabs)} collaborators: {', '.join(unique_collabs[:3])}")
                        if len(unique_collabs) > 3:
                            print(f"        ... and {len(unique_collabs) - 3} more")
                        all_collaborators.update(unique_collabs)
                        repo_collaborators[repo.name] = unique_collabs
                    else:
                        print(f"    📝 No external collaborators")
                        
                except Exception as e:
                    print(f"    ⚠️ Error: {e}")
            
            if not all_collaborators:
                print("❌ No collaborators found in your repositories")
                return
            
            print(f"\n🎯 FOUND {len(all_collaborators)} UNIQUE COLLABORATORS")
            print("="*60)
            
            # Analyze collaborators (limit to top 8 to avoid rate limits)
            top_collaborators = sorted(all_collaborators)[:8]
            print(f"📊 Analyzing top {len(top_collaborators)} collaborators...")
            
            collaborator_data = {}
            all_languages = Counter()
            companies = []
            locations = []
            
            for i, collaborator in enumerate(top_collaborators, 1):
                print(f"\n[{i:2d}/{len(top_collaborators)}] 👤 {collaborator}")
                print("-" * 35)
                
                try:
                    collab_user = self.github.get_user(collaborator)
                    
                    name = collab_user.name if collab_user.name else "Not set"
                    company = collab_user.company if collab_user.company else "Not set"
                    location = collab_user.location if collab_user.location else "Not set"
                    
                    print(f"📛 Name: {name}")
                    print(f"🏢 Company: {company}")
                    print(f"📍 Location: {location}")
                    print(f"📊 Public repos: {collab_user.public_repos}")
                    print(f"👥 Followers: {collab_user.followers}")
                    
                    if company != "Not set":
                        companies.append(company)
                    if location != "Not set":
                        locations.append(location)
                    
                    # Analyze their programming languages
                    try:
                        collab_repos = list(collab_user.get_repos(type='owner', sort='updated'))[:5]
                        collab_languages = {}
                        
                        for repo in collab_repos:
                            try:
                                repo_langs = repo.get_languages()
                                for lang, bytes_count in repo_langs.items():
                                    collab_languages[lang] = collab_languages.get(lang, 0) + bytes_count
                                    all_languages[lang] += 1  # Count how many collaborators use this language
                            except:
                                pass
                        
                        if collab_languages:
                            total_bytes = sum(collab_languages.values())
                            top_langs = sorted(collab_languages.items(), key=lambda x: x[1], reverse=True)[:4]
                            lang_percentages = [(lang, (bytes_count/total_bytes)*100) for lang, bytes_count in top_langs]
                            print(f"💻 Languages: {', '.join([f'{lang} ({perc:.0f}%)' for lang, perc in lang_percentages])}")
                        
                    except Exception as e:
                        print(f"⚠️ Could not analyze languages: {e}")
                    
                    # Show shared repositories
                    shared_repos = [repo for repo, collabs in repo_collaborators.items() if collaborator in collabs]
                    if shared_repos:
                        print(f"🤝 Collaborated on: {', '.join(shared_repos[:2])}")
                        if len(shared_repos) > 2:
                            print(f"    ... and {len(shared_repos) - 2} more repos")
                    
                except Exception as e:
                    print(f"❌ Error analyzing {collaborator}: {e}")
            
            # Generate summary report
            print("\n" + "="*60)
            print("📈 COLLABORATORS SUMMARY")
            print("="*60)
            
            # Most common languages among collaborators
            if all_languages:
                print(f"\n💻 MOST POPULAR LANGUAGES AMONG YOUR COLLABORATORS:")
                for lang, count in all_languages.most_common(8):
                    print(f"   {lang:15} - Used by {count} collaborator(s)")
            
            # Most common companies
            if companies:
                company_counts = Counter(companies)
                print(f"\n🏢 COLLABORATOR COMPANIES:")
                for company, count in company_counts.most_common(5):
                    print(f"   {company:25} - {count} collaborator(s)")
            
            # Most common locations  
            if locations:
                location_counts = Counter(locations)
                print(f"\n📍 COLLABORATOR LOCATIONS:")
                for location, count in location_counts.most_common(5):
                    print(f"   {location:25} - {count} collaborator(s)")
            
            # Most collaborative repositories
            repo_collab_count = {repo: len(collabs) for repo, collabs in repo_collaborators.items() if collabs}
            if repo_collab_count:
                print(f"\n🤝 YOUR MOST COLLABORATIVE REPOSITORIES:")
                sorted_repos = sorted(repo_collab_count.items(), key=lambda x: x[1], reverse=True)[:5]
                for repo, count in sorted_repos:
                    print(f"   {repo:30} - {count} collaborator(s)")
            
            print(f"\n✅ Analysis complete! Found {len(all_collaborators)} total collaborators.")
            print(f"🎯 Analyzed {len(top_collaborators)} collaborators in detail.")
            
        except Exception as e:
            print(f"❌ Error in collaborator analysis: {e}")

    def analyze_specific_developer(self):
        """Analyze a specific developer by username."""
        if not self.github:
            print("❌ GitHub not configured")
            return
        
        username = input("Enter GitHub username to analyze: ").strip()
        if not username:
            print("❌ No username provided")
            return
        
        try:
            print(f"\n📊 ANALYZING: {username}")
            print("="*40)
            
            user = self.github.get_user(username)
            print(f"👤 Username: {user.login}")
            print(f"📛 Name: {user.name if user.name else 'Not set'}")
            print(f"🏢 Company: {user.company if user.company else 'Not set'}")
            print(f"📍 Location: {user.location if user.location else 'Not set'}")
            print(f"📊 Public repos: {user.public_repos}")
            print(f"👥 Followers: {user.followers}")
            print(f"👤 Following: {user.following}")
            
            # Analyze their repositories
            repos = list(user.get_repos(type='owner', sort='updated'))[:8]
            if repos:
                print(f"\n📁 TOP REPOSITORIES:")
                for i, repo in enumerate(repos, 1):
                    print(f"{i}. {repo.name} (⭐{repo.stargazers_count})")
        
        except Exception as e:
            print(f"❌ Error analyzing {username}: {e}")

    def check_setup(self):
        """Check the current setup and configuration."""
        print("\n⚙️ SETUP STATUS")
        print("="*40)
        
        print(f"🐍 Python: Available")
        print(f"📦 PyGithub: {'✅ Available' if GITHUB_AVAILABLE else '❌ Missing'}")
        print(f"🔑 GitHub Token: {'✅ Configured' if self.github_token else '❌ Missing'}")
        print(f"🔗 GitHub Connection: {'✅ Connected' if self.github else '❌ Not connected'}")
        
        if self.github:
            try:
                rate_limit = self.github.get_rate_limit()
                print(f"📊 GitHub Rate Limit: {rate_limit.core.remaining}/{rate_limit.core.limit} requests remaining")
            except:
                print(f"📊 GitHub Rate Limit: Could not check")

    async def run(self):
        """Main console loop."""
        print("🚀 Developer Skill Analyzer Console")
        
        while True:
            try:
                self.menu()
                choice = input("Choose option: ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    self.get_popular_companies_collaborators()
                elif choice == '2':
                    print("🧠 Top Developers analysis coming soon...")
                elif choice == '3':
                    print("🏆 Trending Repositories analysis coming soon...")
                elif choice == '4':
                    self.analyze_your_github()
                elif choice == '5':
                    self.analyze_collaborators()
                elif choice == '6':
                    self.analyze_specific_developer()
                elif choice == '7':
                    self.check_setup()
                else:
                    print("❌ Invalid option")
                
                input("\n⏸️ Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\n⏸️ Press Enter to continue...")

async def main():
    """Main entry point."""
    console = SkillConsole()
    await console.run()

if __name__ == "__main__":
    asyncio.run(main())
