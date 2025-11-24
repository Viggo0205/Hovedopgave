#!/usr/bin/env python3
"""
Developer Skill Analyzer Console

Run this directly: python skill_console.py

A simple, working console for analyzing developer skills from GitHub and Jira.
"""

import os
import sys
from datetime import datetime

# Check for required packages and import what's available
try:
    from github import Github
    GITHUB_AVAILABLE = True
    print("✅ GitHub library available")
except ImportError:
    print("❌ PyGithub not installed. Install with: pip install PyGithub")
    GITHUB_AVAILABLE = False

try:
    from atlassian import Jira
    JIRA_AVAILABLE = True
    print("✅ Jira library available")
except ImportError:
    print("❌ Atlassian library not installed. Install with: pip install atlassian-python-api")
    JIRA_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment loaded")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")


class SkillConsole:
    def __init__(self):
        print("\n🔧 Setting up console...")
        
        # Get environment variables
        self.github_token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.jira_server = os.getenv("JIRA_SERVER_URL")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_token = os.getenv("JIRA_API_TOKEN")
        
        # Initialize GitHub if available
        self.github = None
        if GITHUB_AVAILABLE and self.github_token:
            try:
                self.github = Github(self.github_token)
                # Test connection
                user = self.github.get_user()
                print(f"✅ GitHub configured (connected as {user.login})")
            except Exception as e:
                print(f"❌ GitHub setup failed: {e}")
                self.github = None
        else:
            print("❌ GitHub not available (missing token or library)")
        
        # Initialize Jira if available
        self.jira = None
        if JIRA_AVAILABLE and all([self.jira_server, self.jira_email, self.jira_token]):
            try:
                self.jira = Jira(
                    url=self.jira_server,
                    username=self.jira_email,
                    password=self.jira_token,
                    cloud=True
                )
                # Test connection
                myself = self.jira.myself()
                print(f"✅ Jira configured (connected as {myself['displayName']})")
            except Exception as e:
                print(f"❌ Jira setup failed: {e}")
                self.jira = None
        else:
            print("❌ Jira not available (missing credentials or library)")

    def show_menu(self):
        print("\n" + "="*50)
        print("🎯 DEVELOPER SKILL ANALYZER")
        print("="*50)
        print("1. 👥 Get All Collaborators (GitHub)")
        print("2. 🧠 Get Developer Competencies (GitHub)")
        print("3. 📊 Analyze Developer Profile (GitHub)")
        print("4. 🎯 Get Jira Project Members")
        print("5. ⚙️ Check Configuration")
        print("0. ❌ Exit")
        print("-"*50)

    def get_collaborators(self):
        """Get all collaborators from GitHub repositories."""
        if not self.github:
            print("❌ GitHub not available. Check your setup with option 5.")
            return
        
        username = input("Enter GitHub username/organization: ").strip()
        if not username:
            print("❌ Username required")
            return
        
        print(f"\n🔄 Getting collaborators for {username}...")
        
        try:
            user = self.github.get_user(username)
            repos = list(user.get_repos())
            
            print(f"📁 Found {len(repos)} repositories")
            
            if len(repos) > 15:
                print(f"⚠️  Limiting analysis to first 15 repos (found {len(repos)})")
                repos = repos[:15]
            
            collaborators = {}
            
            for i, repo in enumerate(repos, 1):
                print(f"  [{i}/{len(repos)}] Analyzing: {repo.name}")
                
                try:
                    # Get contributors
                    contributors = list(repo.get_contributors())
                    
                    for contributor in contributors:
                        login = contributor.login
                        if login not in collaborators:
                            collaborators[login] = {
                                'name': contributor.name or login,
                                'repos': [],
                                'total_contributions': 0
                            }
                        
                        collaborators[login]['repos'].append(repo.name)
                        collaborators[login]['total_contributions'] += contributor.contributions
                
                except Exception as e:
                    print(f"    ⚠️  Could not analyze {repo.name}: {str(e)[:50]}...")
                    continue
            
            # Display results
            print(f"\n✅ Found {len(collaborators)} unique collaborators:")
            print("\n🏆 TOP COLLABORATORS:")
            
            # Sort by total contributions
            top_collaborators = sorted(
                collaborators.items(), 
                key=lambda x: x[1]['total_contributions'], 
                reverse=True
            )[:15]
            
            for login, data in top_collaborators:
                repo_count = len(data['repos'])
                total_contribs = data['total_contributions']
                print(f"   • {data['name']} (@{login})")
                print(f"     📊 {repo_count} repos, {total_contribs} contributions")
            
            if len(collaborators) > 15:
                print(f"\n   ... and {len(collaborators) - 15} more collaborators")
                        
        except Exception as e:
            print(f"❌ Failed to get collaborators: {e}")

    def get_competencies(self):
        """Analyze a developer's competencies from their GitHub activity."""
        if not self.github:
            print("❌ GitHub not available. Check your setup with option 5.")
            return
        
        username = input("Enter GitHub username to analyze: ").strip()
        if not username:
            print("❌ Username required")
            return
        
        print(f"\n🔄 Analyzing competencies for {username}...")
        
        try:
            user = self.github.get_user(username)
            repos = list(user.get_repos())
            
            print(f"📁 Analyzing {len(repos)} repositories...")
            
            if len(repos) > 30:
                print(f"⚠️  Limiting to 30 most recent repos (found {len(repos)})")
                repos = sorted(repos, key=lambda r: r.updated_at, reverse=True)[:30]
            
            # Collect language statistics
            languages = {}
            frameworks = set()
            tools = set()
            
            for i, repo in enumerate(repos, 1):
                if i % 5 == 0:
                    print(f"  Processed {i}/{len(repos)} repos...")
                
                try:
                    # Get programming languages
                    repo_languages = repo.get_languages()
                    for lang, bytes_count in repo_languages.items():
                        languages[lang] = languages.get(lang, 0) + bytes_count
                    
                    # Detect frameworks and tools from repo info
                    repo_text = f"{repo.name} {repo.description or ''}".lower()
                    
                    # Framework detection
                    if any(x in repo_text for x in ['react', 'jsx']): frameworks.add('React')
                    if any(x in repo_text for x in ['vue', 'vuejs']): frameworks.add('Vue.js')
                    if 'angular' in repo_text: frameworks.add('Angular')
                    if 'django' in repo_text: frameworks.add('Django')
                    if 'flask' in repo_text: frameworks.add('Flask')
                    if any(x in repo_text for x in ['spring', 'springboot']): frameworks.add('Spring')
                    if any(x in repo_text for x in ['express', 'expressjs']): frameworks.add('Express.js')
                    if any(x in repo_text for x in ['nextjs', 'next.js']): frameworks.add('Next.js')
                    if 'laravel' in repo_text: frameworks.add('Laravel')
                    
                    # Tool detection
                    if 'docker' in repo_text: tools.add('Docker')
                    if any(x in repo_text for x in ['kubernetes', 'k8s']): tools.add('Kubernetes')
                    if 'aws' in repo_text: tools.add('AWS')
                    if 'azure' in repo_text: tools.add('Azure')
                    if any(x in repo_text for x in ['mongodb', 'mongo']): tools.add('MongoDB')
                    if any(x in repo_text for x in ['postgresql', 'postgres']): tools.add('PostgreSQL')
                    if 'mysql' in repo_text: tools.add('MySQL')
                    if 'redis' in repo_text: tools.add('Redis')
                
                except Exception:
                    continue
            
            # Calculate and display results
            print(f"\n🧠 COMPETENCIES FOR {user.name or username}:")
            
            # Programming Languages
            if languages:
                total_bytes = sum(languages.values())
                print(f"\n💻 PROGRAMMING LANGUAGES:")
                
                sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
                for lang, bytes_count in sorted_languages[:10]:
                    percentage = (bytes_count / total_bytes * 100)
                    
                    # Determine skill level based on usage
                    if percentage > 25:
                        level = "🔥 Expert"
                    elif percentage > 10:
                        level = "⭐ Advanced"
                    elif percentage > 3:
                        level = "✅ Intermediate"
                    else:
                        level = "🌱 Beginner"
                    
                    print(f"   • {lang}: {percentage:.1f}% {level}")
            
            # Frameworks
            if frameworks:
                print(f"\n🛠️  FRAMEWORKS & LIBRARIES:")
                for framework in sorted(frameworks):
                    print(f"   • {framework}")
            
            # Tools & Platforms
            if tools:
                print(f"\n🔧 TOOLS & PLATFORMS:")
                for tool in sorted(tools):
                    print(f"   • {tool}")
            
            # Summary stats
            print(f"\n📊 SUMMARY:")
            print(f"   📁 Repositories analyzed: {len(repos)}")
            print(f"   💻 Programming languages: {len(languages)}")
            print(f"   🛠️  Frameworks detected: {len(frameworks)}")
            print(f"   🔧 Tools detected: {len(tools)}")
                        
        except Exception as e:
            print(f"❌ Failed to analyze competencies: {e}")

    def analyze_developer_profile(self):
        """Get comprehensive developer profile information."""
        if not self.github:
            print("❌ GitHub not available. Check your setup with option 5.")
            return
        
        username = input("Enter GitHub username to analyze: ").strip()
        if not username:
            print("❌ Username required")
            return
        
        print(f"\n🔄 Analyzing developer profile for {username}...")
        
        try:
            user = self.github.get_user(username)
            repos = list(user.get_repos())
            
            print(f"\n📊 DEVELOPER PROFILE: {user.name or username}")
            print("="*50)
            
            # Basic info
            print(f"👤 Username: {user.login}")
            if user.name: print(f"📛 Name: {user.name}")
            if user.company: print(f"🏢 Company: {user.company}")
            if user.location: print(f"📍 Location: {user.location}")
            if user.email: print(f"📧 Email: {user.email}")
            if user.blog: print(f"🌐 Website: {user.blog}")
            
            # Stats
            print(f"\n📈 STATISTICS:")
            print(f"   📁 Public repositories: {user.public_repos}")
            print(f"   👥 Followers: {user.followers}")
            print(f"   👤 Following: {user.following}")
            print(f"   📅 Joined: {user.created_at.strftime('%B %Y')}")
            
            # Recent activity
            recent_repos = [r for r in repos if r.updated_at and r.updated_at.year >= 2024]
            print(f"   🔄 Active repos (2024+): {len(recent_repos)}")
            
            # Popular repositories
            popular_repos = [r for r in repos if r.stargazers_count > 0]
            if popular_repos:
                popular_repos.sort(key=lambda r: r.stargazers_count, reverse=True)
                
                print(f"\n⭐ TOP REPOSITORIES:")
                for repo in popular_repos[:5]:
                    stars = repo.stargazers_count
                    language = repo.language or "Unknown"
                    print(f"   • {repo.name}: {stars} ⭐ ({language})")
            
            # Recent languages
            if repos:
                recent_languages = set()
                for repo in repos[:15]:  # Check recent repos
                    if repo.language:
                        recent_languages.add(repo.language)
                
                if recent_languages:
                    print(f"\n💻 RECENT LANGUAGES:")
                    print(f"   {', '.join(sorted(recent_languages))}")
            
        except Exception as e:
            print(f"❌ Failed to analyze developer profile: {e}")

    def get_jira_members(self):
        """Get project members from Jira."""
        if not self.jira:
            print("❌ Jira not available. Check your setup with option 5.")
            return
        
        project_key = input("Enter Jira project key: ").strip().upper()
        if not project_key:
            print("❌ Project key required")
            return
        
        print(f"\n🔄 Getting project members for {project_key}...")
        
        try:
            # Get project info
            project = self.jira.project(project_key)
            print(f"📂 Project: {project['name']}")
            
            # Get users from recent issues
            users = set()
            
            try:
                jql = f"project = {project_key} ORDER BY updated DESC"
                issues = self.jira.jql(jql, limit=50)['issues']
                
                print(f"📋 Analyzing {len(issues)} recent issues...")
                
                for issue in issues:
                    # Reporter
                    if 'reporter' in issue['fields'] and issue['fields']['reporter']:
                        reporter = issue['fields']['reporter']
                        users.add((
                            reporter['displayName'],
                            reporter.get('emailAddress', 'N/A')
                        ))
                    
                    # Assignee
                    if 'assignee' in issue['fields'] and issue['fields']['assignee']:
                        assignee = issue['fields']['assignee']
                        users.add((
                            assignee['displayName'],
                            assignee.get('emailAddress', 'N/A')
                        ))
                
                print(f"\n👥 PROJECT MEMBERS ({len(users)} found):")
                for name, email in sorted(users):
                    print(f"   • {name}")
                    if email != 'N/A':
                        print(f"     📧 {email}")
                    
            except Exception as e:
                print(f"❌ Could not get project members: {e}")
                
        except Exception as e:
            print(f"❌ Failed to access Jira project: {e}")

    def check_setup(self):
        """Check configuration and connections."""
        print(f"\n⚙️ CONFIGURATION STATUS:")
        print("="*40)
        
        # Environment variables
        print("📋 ENVIRONMENT VARIABLES:")
        print(f"   GitHub Token: {'✅ Set' if self.github_token else '❌ Missing'}")
        print(f"   Jira Server: {'✅ Set' if self.jira_server else '❌ Missing'}")
        print(f"   Jira Email: {'✅ Set' if self.jira_email else '❌ Missing'}")
        print(f"   Jira Token: {'✅ Set' if self.jira_token else '❌ Missing'}")
        
        # Library availability
        print(f"\n📚 LIBRARIES:")
        print(f"   PyGithub: {'✅ Available' if GITHUB_AVAILABLE else '❌ Missing'}")
        print(f"   Atlassian API: {'✅ Available' if JIRA_AVAILABLE else '❌ Missing'}")
        
        # Connection tests
        print(f"\n🔌 CONNECTIONS:")
        
        if self.github:
            try:
                user = self.github.get_user()
                rate_limit = self.github.get_rate_limit()
                remaining = rate_limit.core.remaining
                limit = rate_limit.core.limit
                print(f"   🐙 GitHub: ✅ Connected as {user.login} ({remaining}/{limit} requests)")
            except Exception as e:
                print(f"   🐙 GitHub: ❌ Connection failed: {e}")
        else:
            print(f"   🐙 GitHub: ❌ Not configured")
        
        if self.jira:
            try:
                myself = self.jira.myself()
                print(f"   🎯 Jira: ✅ Connected as {myself['displayName']}")
            except Exception as e:
                print(f"   🎯 Jira: ❌ Connection failed: {e}")
        else:
            print(f"   🎯 Jira: ❌ Not configured")
        
        # Installation help
        if not GITHUB_AVAILABLE or not JIRA_AVAILABLE:
            print(f"\n💡 INSTALLATION HELP:")
            if not GITHUB_AVAILABLE:
                print("   Install GitHub support: pip install PyGithub")
            if not JIRA_AVAILABLE:
                print("   Install Jira support: pip install atlassian-python-api")
            print("   Install environment support: pip install python-dotenv")

    def run(self):
        """Run the interactive console."""
        print("🚀 Developer Skill Analyzer Console")
        print("   Simple and focused on key features\n")
        
        if not GITHUB_AVAILABLE and not JIRA_AVAILABLE:
            print("❌ No API libraries available. Please install dependencies:")
            print("   pip install PyGithub atlassian-python-api python-dotenv")
            return
        
        while True:
            try:
                self.show_menu()
                choice = input("\nChoose option: ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    self.get_collaborators()
                elif choice == '2':
                    self.get_competencies()
                elif choice == '3':
                    self.analyze_developer_profile()
                elif choice == '4':
                    self.get_jira_members()
                elif choice == '5':
                    self.check_setup()
                else:
                    print("❌ Invalid option. Please try again.")
                
                input("\n⏸️ Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("\n⏸️ Press Enter to continue...")


if __name__ == "__main__":
    console = SkillConsole()
    console.run()
