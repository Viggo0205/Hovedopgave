#!/usr/bin/env python3
"""
Simple Developer Skill Analyzer Console

Run this directly: python skill_console.py
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Check for required packages
try:
    import github
    from dotenv import load_dotenv
    GITHUB_AVAILABLE = True
except ImportError:
    print("⚠️  PyGithub not installed. Install with: pip install PyGithub python-dotenv")
    GITHUB_AVAILABLE = False

try:
    import atlassian
    JIRA_AVAILABLE = True
except ImportError:
    print("⚠️  Jira not installed. Install with: pip install atlassian-python-api")
    JIRA_AVAILABLE = False

# Load environment
try:
    if 'load_dotenv' in locals():
        load_dotenv()
except:
    pass

# Simple config class
class SimpleConfig:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.jira_server_url = os.getenv("JIRA_SERVER_URL")
        self.jira_email = os.getenv("JIRA_EMAIL") 
        self.jira_api_token = os.getenv("JIRA_API_TOKEN")

# Simple GitHub analyzer
class SimpleGitHub:
    def __init__(self, token):
        if GITHUB_AVAILABLE:
            self.github = github.Github(token)
        else:
            self.github = None


class SkillConsole:
    def __init__(self):
        print("🔧 Initializing...")
        try:
            # Use the simple config class we defined
            self.config = SimpleConfig()
            
            # Initialize GitHub if available
            if GITHUB_AVAILABLE and self.config.github_token:
                self.github = SimpleGitHub(self.config.github_token)
                print(f"✅ GitHub: Ready")
            else:
                self.github = None
                print(f"❌ GitHub: Not configured")
            
            # For now, skip Jira initialization to get basic functionality working
            self.jira = None
            print(f"⚠️ Jira: Skipped for now")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            self.github = None
            self.jira = None

    def menu(self):
        print("\n" + "="*50)
        print("🎯 DEVELOPER SKILL ANALYZER")
        print("="*50)
        print("📋 QUICK LISTS:")
        print("1. 👥 Popular Tech Companies & Their Collaborators")
        print("2. 🧠 Top Developers & Their Skills")
        print("3. 🏆 Trending Repositories & Contributors")
        print("")
        print("🔍 PERSONAL ANALYSIS:")
        print("4. 🏠 Analyze YOUR GitHub Account")
        print("5. 🤝 Find ALL Your Collaborators & Their Skills")
        print("6. 📊 Analyze Specific Developer")
        print("7. 🔍 Search Organization")
        print("8. ⚙️ Check Setup")
        print("0. Exit")
        print("-"*50)

    def get_popular_companies_collaborators(self):
        """Get collaborators from popular tech companies."""
        if not self.github or not self.github.github:
            print("❌ GitHub not configured")
            return
        
        print("\n👥 POPULAR TECH COMPANIES & COLLABORATORS")
        print("="*50)
        
        # Pre-defined list of popular companies/orgs
        companies = [
            {"name": "Microsoft", "github": "microsoft"},
            {"name": "Google", "github": "google"},
            {"name": "Facebook/Meta", "github": "facebook"},
            {"name": "Netflix", "github": "netflix"},
            {"name": "Airbnb", "github": "airbnb"},
            {"name": "Uber", "github": "uber"},
            {"name": "GitHub", "github": "github"},
            {"name": "Docker", "github": "docker"}
        ]
        
        choice = input("Choose company (1-8) or press Enter to analyze all: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 8:
            # Analyze single company
            company = companies[int(choice) - 1]
            print(f"\n🔄 Analyzing {company['name']} ({company['github']})...")
            self._analyze_organization(company['github'], company['name'])
        else:
            # Analyze multiple companies (limited)
            print("\n🔄 Quick analysis of top companies...")
            for i, company in enumerate(companies[:4], 1):  # Limit to avoid rate limits
                print(f"\n[{i}/4] 🏢 {company['name']}:")
                self._analyze_organization(company['github'], company['name'], quick=True)

    def get_top_developers_skills(self):
        """Get skills from popular developers."""
        if not self.github or not self.github.github:
            print("❌ GitHub not configured")
            return
        
        print("\n🧠 TOP DEVELOPERS & THEIR SKILLS")
        print("="*50)
        
        # Pre-defined list of notable developers
        developers = [
            {"name": "Linus Torvalds", "github": "torvalds", "known_for": "Linux, Git"},
            {"name": "Dan Abramov", "github": "gaearon", "known_for": "React, Redux"},
            {"name": "Evan You", "github": "yyx990803", "known_for": "Vue.js"},
            {"name": "TJ Holowaychuk", "github": "tj", "known_for": "Express.js, Koa"},
            {"name": "Sindre Sorhus", "github": "sindresorhus", "known_for": "Open Source"},
            {"name": "Addy Osmani", "github": "addyosmani", "known_for": "Chrome DevTools"},
        ]
        
        choice = input("Choose developer (1-6) or press Enter to analyze all: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            # Analyze single developer
            dev = developers[int(choice) - 1]
            print(f"\n🔄 Analyzing {dev['name']} (@{dev['github']})...")
            print(f"   Known for: {dev['known_for']}")
            self._analyze_developer_skills(dev['github'], dev['name'])
        else:
            # Analyze multiple developers
            print("\n🔄 Quick skills analysis...")
            for i, dev in enumerate(developers[:4], 1):  # Limit to avoid rate limits
                print(f"\n[{i}/4] 👤 {dev['name']} (@{dev['github']}):")
                print(f"   Known for: {dev['known_for']}")
                self._analyze_developer_skills(dev['github'], dev['name'], quick=True)

    def get_trending_repositories(self):
        """Get trending repositories and their contributors."""
        if not self.github or not self.github.github:
            print("❌ GitHub not configured")
            return
        
        print("\n🏆 TRENDING REPOSITORIES & CONTRIBUTORS")
        print("="*50)
        
        # Pre-defined list of popular/trending repositories
        repos = [
            {"owner": "microsoft", "name": "vscode", "description": "Visual Studio Code"},
            {"owner": "facebook", "name": "react", "description": "React Library"},
            {"owner": "vuejs", "name": "vue", "description": "Vue.js Framework"},
            {"owner": "angular", "name": "angular", "description": "Angular Framework"},
            {"owner": "nodejs", "name": "node", "description": "Node.js Runtime"},
            {"owner": "docker", "name": "docker-ce", "description": "Docker Engine"},
        ]
        
        choice = input("Choose repository (1-6) or press Enter to analyze all: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            # Analyze single repository
            repo = repos[int(choice) - 1]
            print(f"\n🔄 Analyzing {repo['description']}...")
            self._analyze_repository(repo['owner'], repo['name'])
        else:
            # Analyze multiple repositories
            print("\n🔄 Quick repository analysis...")
            for i, repo in enumerate(repos[:4], 1):  # Limit to avoid rate limits
                print(f"\n[{i}/4] 📁 {repo['description']}:")
                self._analyze_repository(repo['owner'], repo['name'], quick=True)

    def _analyze_organization(self, org_name, display_name, quick=False):
        """Helper method to analyze an organization."""
        try:
            org = self.github.github.get_organization(org_name)
            repos = list(org.get_repos())[:5 if quick else 10]
            
            collaborators = {}
            
            for repo in repos:
                try:
                    contributors = list(repo.get_contributors())[:10]
                    for contributor in contributors:
                        login = contributor.login
                        if login not in collaborators:
                            collaborators[login] = {
                                'name': contributor.name or login,
                                'total_contributions': 0,
                                'repos': []
                            }
                        collaborators[login]['total_contributions'] += contributor.contributions
                        collaborators[login]['repos'].append(repo.name)
                except:
                    continue
              # Show results
            if quick:
                top_contributors = sorted(collaborators.items(), key=lambda x: x[1]['total_contributions'], reverse=True)[:3]
                contributor_list = [f"{data['name']} ({data['total_contributions']})" for login, data in top_contributors]
                print(f"   Top contributors: {', '.join(contributor_list)}")
            else:
                print(f"\n✅ Found {len(collaborators)} contributors in {display_name}:")
                top_contributors = sorted(collaborators.items(), key=lambda x: x[1]['total_contributions'], reverse=True)[:10]
                for login, data in top_contributors:
                    print(f"   • {data['name']} (@{login}): {data['total_contributions']} contributions across {len(data['repos'])} repos")
                    
        except Exception as e:
            print(f"   ❌ Could not analyze {display_name}: {str(e)[:50]}...")

    def _analyze_developer_skills(self, username, display_name, quick=False):
        """Helper method to analyze developer skills."""
        try:
            user = self.github.github.get_user(username)
            repos = list(user.get_repos())[:5 if quick else 15]
            
            languages = {}
            for repo in repos:
                try:
                    repo_langs = repo.get_languages()
                    for lang, bytes_count in repo_langs.items():
                        languages[lang] = languages.get(lang, 0) + bytes_count
                except:
                    continue
            
            if languages:
                total_bytes = sum(languages.values())
                top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5 if quick else 8]
                
                if quick:
                    lang_list = [f"{lang} ({(bytes_count/total_bytes*100):.1f}%)" for lang, bytes_count in top_languages[:3]]
                    print(f"   Top languages: {', '.join(lang_list)}")
                else:
                    print(f"\n💻 Programming Languages for {display_name}:")
                    for lang, bytes_count in top_languages:
                        percentage = (bytes_count / total_bytes * 100)
                        level = "🔥 Expert" if percentage > 30 else "⭐ Advanced" if percentage > 15 else "✅ Intermediate" if percentage > 5 else "🌱 Beginner"
                        print(f"   • {lang}: {percentage:.1f}% {level}")
            else:
                print(f"   ❌ No language data available for {display_name}")
                
        except Exception as e:
            print(f"   ❌ Could not analyze {display_name}: {str(e)[:50]}...")

    def _analyze_repository(self, owner, repo_name, quick=False):
        """Helper method to analyze a repository."""
        try:
            repo = self.github.github.get_repo(f"{owner}/{repo_name}")
            contributors = list(repo.get_contributors())[:5 if quick else 10]
            
            if quick:
                top_3 = contributors[:3]
                contrib_list = [f"{c.login} ({c.contributions})" for c in top_3]
                print(f"   Top contributors: {', '.join(contrib_list)}")
                print(f"   Language: {repo.language}, Stars: {repo.stargazers_count}")
            else:
                print(f"\n📁 Repository: {repo.full_name}")
                print(f"   ⭐ Stars: {repo.stargazers_count}")
                print(f"   🍴 Forks: {repo.forks_count}")
                print(f"   💻 Language: {repo.language}")
                print(f"   📝 Description: {repo.description}")
                print(f"\n👥 Top Contributors:")
                for contributor in contributors:
                    print(f"   • {contributor.name or contributor.login} (@{contributor.login}): {contributor.contributions} contributions")
                    
        except Exception as e:
            print(f"   ❌ Could not analyze repository: {str(e)[:50]}...")

    def get_collaborators(self):
        if not self.github or not self.github.github:
            print("❌ GitHub not configured")
            return
            
        user = input("GitHub username/org: ").strip()
        if not user:
            return
            
        print(f"🔄 Getting collaborators for {user}...")
        
        try:
            gh_user = self.github.github.get_user(user)
            repos = list(gh_user.get_repos())[:10]  # Limit for demo
            
            collaborators = {}
            
            for repo in repos:
                print(f"  📁 {repo.name}")
                try:
                    for contributor in repo.get_contributors():
                        if contributor.login not in collaborators:
                            collaborators[contributor.login] = {
                                'name': contributor.name or contributor.login,
                                'repos': [],
                                'contributions': contributor.contributions
                            }
                        collaborators[contributor.login]['repos'].append(repo.name)
                except:
                    continue
            
            print(f"\n✅ Found {len(collaborators)} collaborators:")
            for login, data in list(collaborators.items())[:15]:
                print(f"   • {data['name']} - {len(data['repos'])} repos, {data['contributions']} contributions")
                
        except Exception as e:
            print(f"❌ Error: {e}")

    def get_competencies(self):
        user = input("GitHub username: ").strip()
        if not user:
            return
            
        print(f"🔄 Analyzing competencies for {user}...")
        
        skills = {}
        
        # GitHub analysis
        if self.github:
            try:
                gh_user = self.github.github.get_user(user)
                repos = list(gh_user.get_repos())[:20]
                
                languages = {}
                frameworks = set()
                tools = set()
                
                for repo in repos:
                    # Get languages
                    try:
                        repo_langs = repo.get_languages()
                        for lang, bytes_count in repo_langs.items():
                            languages[lang] = languages.get(lang, 0) + bytes_count
                    except:
                        continue
                    
                    # Detect frameworks from repo names/descriptions
                    repo_text = f"{repo.name} {repo.description or ''}".lower()
                    if 'react' in repo_text: frameworks.add('React')
                    if 'vue' in repo_text: frameworks.add('Vue.js')
                    if 'angular' in repo_text: frameworks.add('Angular')
                    if 'django' in repo_text: frameworks.add('Django')
                    if 'flask' in repo_text: frameworks.add('Flask')
                    if 'spring' in repo_text: frameworks.add('Spring')
                    if 'express' in repo_text: frameworks.add('Express.js')
                    if 'docker' in repo_text: tools.add('Docker')
                    if 'kubernetes' in repo_text: tools.add('Kubernetes')
                    if 'aws' in repo_text: tools.add('AWS')
                
                # Calculate skill levels based on usage
                total_bytes = sum(languages.values())
                
                print(f"\n🧠 Competencies for {user}:")
                print("\n💻 PROGRAMMING LANGUAGES:")
                for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]:
                    percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                    level = "🔥 Expert" if percentage > 30 else "⭐ Advanced" if percentage > 15 else "✅ Intermediate" if percentage > 5 else "🌱 Beginner"
                    print(f"   • {lang}: {percentage:.1f}% {level}")
                
                if frameworks:
                    print(f"\n🛠️ FRAMEWORKS:")
                    for fw in sorted(frameworks):
                        print(f"   • {fw}")
                
                if tools:
                    print(f"\n🔧 TOOLS & PLATFORMS:")
                    for tool in sorted(tools):
                        print(f"   • {tool}")
                        
            except Exception as e:
                print(f"❌ GitHub analysis failed: {e}")

    def analyze_developer(self):
        user = input("GitHub username: ").strip()
        if not user:
            return
            
        print(f"🔄 Full analysis for {user}...")
        
        if self.github:
            try:
                gh_user = self.github.github.get_user(user)
                repos = list(gh_user.get_repos())
                
                print(f"\n📊 DEVELOPER PROFILE: {gh_user.name or user}")
                print(f"   👤 Public repos: {gh_user.public_repos}")
                print(f"   👥 Followers: {gh_user.followers}")
                print(f"   📍 Location: {gh_user.location or 'Not specified'}")
                print(f"   🏢 Company: {gh_user.company or 'Not specified'}")
                
                # Recent activity
                recent_repos = [r for r in repos if r.updated_at > datetime(2024, 1, 1)]
                print(f"   🔄 Active repos (2024+): {len(recent_repos)}")
                
                # Top repositories by stars
                top_repos = sorted(repos, key=lambda r: r.stargazers_count, reverse=True)[:5]
                if top_repos and top_repos[0].stargazers_count > 0:
                    print(f"\n⭐ TOP REPOSITORIES:")
                    for repo in top_repos:
                        if repo.stargazers_count > 0:
                            print(f"   • {repo.name}: {repo.stargazers_count} stars")
                            
            except Exception as e:
                print(f"❌ Analysis failed: {e}")

    def analyze_your_github(self):
        """Analyze your own GitHub account - repositories, collaborators, and skills."""
        if not self.github or not self.github.github:
            print("❌ GitHub not configured")
            return
        
        try:
            print("\n🏠 ANALYZING YOUR GITHUB ACCOUNT")
            print("="*50)
            
            user = self.github.github.get_user()
            print(f"👤 Account: {user.login}")
            if user.name:
                print(f"📛 Name: {user.name}")
            if user.bio:
                print(f"📝 Bio: {user.bio}")
            if user.location:
                print(f"📍 Location: {user.location}")
            if user.company:
                print(f"🏢 Company: {user.company}")
            
            print(f"📊 Stats: {user.public_repos} repos, {user.followers} followers, {user.following} following")
            
            # Get your repositories
            print(f"\n📁 YOUR REPOSITORIES:")
            repos = list(user.get_repos(type='owner', sort='updated'))[:15]
            
            all_languages = {}
            total_stars = 0
            total_forks = 0
            all_collaborators = set()
            
            for i, repo in enumerate(repos, 1):
                print(f"{i:2d}. {repo.name}")
                print(f"    ⭐ {repo.stargazers_count} stars, 🍴 {repo.forks_count} forks")
                total_stars += repo.stargazers_count
                total_forks += repo.forks_count
                
                if repo.description:
                    print(f"    📝 {repo.description[:60]}{'...' if len(repo.description) > 60 else ''}")
                
                # Languages
                try:
                    languages = repo.get_languages()
                    if languages:
                        repo_langs = list(languages.keys())[:3]
                        print(f"    💻 Languages: {', '.join(repo_langs)}")
                        
                        # Accumulate language stats
                        for lang, bytes_count in languages.items():
                            all_languages[lang] = all_languages.get(lang, 0) + bytes_count
                except Exception as e:
                    print(f"    ⚠️  Could not get languages: {e}")
                
                # Collaborators
                try:
                    collaborators = list(repo.get_collaborators())
                    if len(collaborators) > 1:  # More than just you
                        collab_names = [c.login for c in collaborators if c.login != user.login]
                        if collab_names:
                            print(f"    👥 Collaborators: {', '.join(collab_names[:5])}")
                            all_collaborators.update(collab_names)
                except Exception as e:
                    print(f"    ⚠️  Could not get collaborators: {e}")
                
                print()
            
            # Summary
            print("=" * 50)
            print("📈 SUMMARY")
            print("=" * 50)
            print(f"🎯 Total Stars: {total_stars}")
            print(f"🎯 Total Forks: {total_forks}")
            print(f"🎯 Total Collaborators: {len(all_collaborators)}")
            
            if all_collaborators:
                print(f"👥 All Collaborators: {', '.join(sorted(all_collaborators)[:10])}{'...' if len(all_collaborators) > 10 else ''}")
            
            # Top languages
            if all_languages:
                sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:10]
                print(f"\n💻 YOUR TOP PROGRAMMING LANGUAGES:")
                for lang, bytes_count in sorted_langs:
                    percentage = (bytes_count / sum(all_languages.values())) * 100
                    print(f"   {lang}: {percentage:.1f}%")
            
            # Organizations
            print(f"\n🏢 YOUR ORGANIZATIONS:")
            try:
                orgs = list(user.get_orgs())
                if orgs:
                    for org in orgs:
                        print(f"   • {org.login}")
                        try:
                            org_repos = list(org.get_repos(type='public'))
                            print(f"     📁 {len(org_repos)} public repositories")
                        except:
                            pass
                else:
                    print("   No organizations found")
            except Exception as e:
                print(f"   ⚠️  Could not fetch organizations: {e}")
            
        except Exception as e:
            print(f"❌ Error analyzing your GitHub: {e}")
            import traceback
            traceback.print_exc()

    def check_setup(self):
        print(f"\n⚙️ CONFIGURATION:")
        print(f"   GitHub Token: {'✅ Set' if self.config.github_token else '❌ Missing'}")
        print(f"   Jira Server: {'✅ Set' if self.config.jira_server_url else '❌ Missing'}")
        
        if self.github:
            try:
                user = self.github.github.get_user()
                rate_limit = self.github.github.get_rate_limit()
                print(f"   🐙 GitHub: ✅ Connected as {user.login} ({rate_limit.core.remaining} requests left)")
            except Exception as e:
                print(f"   🐙 GitHub: ❌ {e}")
                
        if self.jira:
            try:
                myself = self.jira.jira.myself()
                print(f"   🎯 Jira: ✅ Connected as {myself.get('emailAddress')}")
            except Exception as e:
                print(f"   🎯 Jira: ❌ {e}")

    async def analyze_collaborators(self):
        """Find and analyze all your collaborators and their skills."""
        if not self.github or not self.github.github:
            print("❌ GitHub not configured")
            return
        
        try:
            print("\n🤝 ANALYZING YOUR COLLABORATORS")
            print("="*60)
            
            # Get your GitHub username
            user = self.github.github.get_user()
            your_username = user.login
            print(f"📊 Scanning repositories for: {your_username}")
            
            # Get all your repositories
            repos = list(user.get_repos(type='all'))
            print(f"📁 Found {len(repos)} repositories to analyze")
            
            all_collaborators = set()
            repo_collaborators = {}
            
            # Scan repositories for collaborators
            print("\n🔍 Scanning for collaborators...")
            for i, repo in enumerate(repos[:20], 1):  # Limit to first 20 repos to avoid rate limits
                print(f"[{i:2d}] 📂 {repo.name}")
                
                try:
                    # Get direct collaborators
                    collaborators = list(repo.get_collaborators())
                    repo_collabs = [c.login for c in collaborators if c.login != your_username]
                    
                    # Get contributors
                    try:
                        contributors = list(repo.get_contributors())
                        contrib_names = [c.login for c in contributors[:5] if c.login != your_username]
                        repo_collabs.extend(contrib_names)
                    except:
                        pass
                    
                    if repo_collabs:
                        unique_collabs = list(set(repo_collabs))
                        print(f"    👥 {len(unique_collabs)} collaborators: {', '.join(unique_collabs[:3])}")
                        all_collaborators.update(unique_collabs)
                        repo_collaborators[repo.name] = unique_collabs
                    
                except Exception as e:
                    print(f"    ⚠️ Error: {e}")
            
            if not all_collaborators:
                print("❌ No collaborators found in your repositories")
                return
            
            print(f"\n🎯 FOUND {len(all_collaborators)} UNIQUE COLLABORATORS")
            print("="*60)
            
            # Analyze top collaborators (limit to avoid rate limits)
            top_collaborators = sorted(all_collaborators)[:10]
            print(f"📊 Analyzing skills of top {len(top_collaborators)} collaborators...")
            
            # Use the existing GitHub analyzer from src
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
                from developer_skill_analyzer.analyzers.github_analyzer import GitHubAnalyzer
                
                analyzer = GitHubAnalyzer(self.config.github_token)
                
                collaborator_data = {}
                languages_summary = {}
                
                for i, collaborator in enumerate(top_collaborators, 1):
                    print(f"\n[{i:2d}/{len(top_collaborators)}] 👤 {collaborator}")
                    print("-" * 30)
                    
                    try:
                        # Get basic profile info
                        collab_user = self.github.github.get_user(collaborator)
                        
                        print(f"📛 Name: {collab_user.name if collab_user.name else 'Not set'}")
                        print(f"🏢 Company: {collab_user.company if collab_user.company else 'Not set'}")
                        print(f"📍 Location: {collab_user.location if collab_user.location else 'Not set'}")
                        print(f"📊 Public repos: {collab_user.public_repos}")
                        print(f"👥 Followers: {collab_user.followers}")
                        
                        # Get their recent repositories to analyze languages
                        try:
                            collab_repos = list(collab_user.get_repos(type='owner', sort='updated'))[:5]
                            collab_languages = {}
                            
                            for repo in collab_repos:
                                try:
                                    repo_langs = repo.get_languages()
                                    for lang, bytes_count in repo_langs.items():
                                        collab_languages[lang] = collab_languages.get(lang, 0) + bytes_count
                                        languages_summary[lang] = languages_summary.get(lang, 0) + 1
                                except:
                                    pass
                            
                            if collab_languages:
                                total_bytes = sum(collab_languages.values())
                                top_langs = sorted(collab_languages.items(), key=lambda x: x[1], reverse=True)[:5]
                                lang_percentages = [(lang, (bytes_count/total_bytes)*100) for lang, bytes_count in top_langs]
                                print(f"💻 Languages: {', '.join([f'{lang} ({perc:.1f}%)' for lang, perc in lang_percentages])}")
                        
                        except Exception as e:
                            print(f"⚠️ Could not analyze languages: {e}")
                        
                        # Show which repos they collaborated on with you
                        shared_repos = [repo for repo, collabs in repo_collaborators.items() if collaborator in collabs]
                        if shared_repos:
                            print(f"🤝 Collaborated on: {', '.join(shared_repos[:2])}")
                            if len(shared_repos) > 2:
                                print(f"    ... and {len(shared_repos) - 2} more repositories")
                        
                        collaborator_data[collaborator] = {
                            'name': collab_user.name,
                            'company': collab_user.company,
                            'location': collab_user.location,
                            'repos': collab_user.public_repos,
                            'followers': collab_user.followers,
                            'languages': collab_languages if 'collab_languages' in locals() else {},
                            'shared_repos': shared_repos
                        }
                        
                    except Exception as e:
                        print(f"❌ Error analyzing {collaborator}: {e}")
                
                # Generate summary
                print("\n" + "="*60)
                print("📈 COLLABORATORS SUMMARY")
                print("="*60)
                
                if languages_summary:
                    print("\n💻 MOST COMMON LANGUAGES AMONG COLLABORATORS:")
                    sorted_langs = sorted(languages_summary.items(), key=lambda x: x[1], reverse=True)[:8]
                    for lang, count in sorted_langs:
                        print(f"   {lang:15} - Used by {count} collaborator(s)")
                
                # Most collaborative repositories
                repo_collab_count = {repo: len(collabs) for repo, collabs in repo_collaborators.items()}
                if repo_collab_count:
                    print(f"\n🤝 YOUR MOST COLLABORATIVE REPOSITORIES:")
                    sorted_repos = sorted(repo_collab_count.items(), key=lambda x: x[1], reverse=True)[:5]
                    for repo, count in sorted_repos:
                        print(f"   {repo:25} - {count} collaborator(s)")
                
                # Companies and locations
                companies = [data['company'] for data in collaborator_data.values() if data['company']]
                locations = [data['location'] for data in collaborator_data.values() if data['location']]
                
                if companies:
                    from collections import Counter
                    company_counts = Counter(companies)
                    print(f"\n🏢 COLLABORATOR COMPANIES:")
                    for company, count in company_counts.most_common(5):
                        print(f"   {company:25} - {count} collaborator(s)")
                
                if locations:
                    location_counts = Counter(locations)
                    print(f"\n📍 COLLABORATOR LOCATIONS:")
                    for location, count in location_counts.most_common(5):
                        print(f"   {location:25} - {count} collaborator(s)")
                
                print(f"\n✅ Analysis complete! Analyzed {len(collaborator_data)} collaborators from {len(all_collaborators)} total found.")
                
            except ImportError as e:
                print(f"❌ Could not import GitHub analyzer: {e}")
                print("Falling back to basic analysis...")
                
                # Basic fallback analysis
                for collaborator in top_collaborators[:5]:
                    try:
                        collab_user = self.github.github.get_user(collaborator)
                        print(f"\n👤 {collaborator}")
                        print(f"   📛 {collab_user.name if collab_user.name else 'Name not set'}")
                        print(f"   🏢 {collab_user.company if collab_user.company else 'Company not set'}")
                        print(f"   📊 {collab_user.public_repos} public repos")
                    except Exception as e:
                        print(f"❌ Could not analyze {collaborator}: {e}")
              except Exception as e:
            print(f"❌ Error in collaborator analysis: {e}")
            import traceback
            traceback.print_exc()

    async def run(self):
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
                    self.get_top_developers_skills()
                elif choice == '3':
                    self.get_trending_repositories()
                elif choice == '4':
                    self.analyze_your_github()
                elif choice == '5':
                    await self.analyze_collaborators()
                elif choice == '6':
                    self.analyze_developer()
                elif choice == '7':
                    self.get_collaborators()
                elif choice == '8':
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


if __name__ == "__main__":
    console = SkillConsole()
    asyncio.run(console.run())
