"""
GitHub Repository and Profile Analyzer for Developer Skill Assessment.

This module provides comprehensive analysis of GitHub data for skill extraction,
including repository analysis, commit patterns, collaboration metrics, and
technology stack identification.

Key Capabilities:
1. Repository Analysis:
   - Programming language detection and usage statistics
   - Code complexity and quality metrics
   - Project structure and architectural patterns
   - Documentation and testing practices

2. User Profile Analysis:
   - Overall coding activity and consistency
   - Technology preferences and expertise areas
   - Open source contribution patterns
   - Leadership and mentoring indicators

3. Collaboration Analysis:
   - Team involvement and communication patterns
   - Code review participation
   - Issue resolution and project management
   - Knowledge sharing and documentation

4. Skill Extraction:
   - Programming languages with proficiency levels
   - Frameworks, libraries, and tools usage
   - Development methodologies and practices
   - Domain expertise identification

5. Technical Features:
   - GitHub API integration with rate limiting
   - Mock data support for testing
   - Caching for performance optimization
   - Error handling and fallback mechanisms

Author: Developer Skill Analyzer Project
Version: Enhanced with comprehensive skill analysis capabilities
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

from github import Github, GithubException, Auth
from github.Repository import Repository
from github.Commit import Commit
from github.PullRequest import PullRequest

from ..models.analysis import GitHubAnalysisResult, RepositoryAnalysis

logger = logging.getLogger(__name__)
logger.disabled = True  # Disable logging to prevent stdout interference


class GitHubAnalyzer:
    """Analyzes GitHub data to extract developer skills and metrics."""
    
    def __init__(self, access_token: str):
        """
        Initialize the GitHub analyzer.
        
        Args:
            access_token: GitHub personal access token
        """
        # Use new PyGithub authentication method to avoid deprecation warnings
        auth = Auth.Token(access_token)
        self.github = Github(auth=auth)
        self.rate_limit_buffer = 100  # Reserve some requests for safety
    
    async def analyze_developer(
        self,
        username: str,
        repositories: Optional[List[str]] = None,
        include_contributions: bool = True,
        time_range_months: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze a developer's GitHub activity.
        
        Args:
            username: GitHub username
            repositories: Specific repositories to analyze
            include_contributions: Include contributions to other repos
            time_range_months: Number of months to analyze
            
        Returns:
            Analysis results dictionary
        """
        try:
            user = self.github.get_user(username)
            since_date = datetime.now() - timedelta(days=time_range_months * 30)
            
            logger.info(f"Analyzing GitHub user: {username}")
            
            # Get profile data
            profile_data = self._extract_profile_data(user)
            
            # Get repositories to analyze
            repos_to_analyze = await self._get_repositories_to_analyze(
                user, repositories, include_contributions
            )
            
            # Analyze each repository
            repository_analyses = []
            for repo in repos_to_analyze:
                try:
                    repo_analysis = await self._analyze_repository(
                        repo, username, since_date
                    )
                    if repo_analysis:
                        repository_analyses.append(repo_analysis)
                except Exception as e:
                    logger.warning(f"Failed to analyze repository {repo.name}: {e}")
                    continue
            
            # Aggregate results
            result = self._aggregate_analysis_results(
                username, profile_data, repository_analyses, time_range_months
            )
            
            return result.dict()
            
        except GithubException as e:
            logger.error(f"GitHub API error for user {username}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing GitHub user {username}: {e}")
            raise
    
    def _extract_profile_data(self, user) -> Dict[str, Any]:
        """Extract basic profile information."""
        return {
            "login": user.login,
            "name": user.name,
            "company": user.company,
            "location": user.location,
            "email": user.email,
            "bio": user.bio,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    async def _get_repositories_to_analyze(
        self,
        user,
        specific_repos: Optional[List[str]],
        include_contributions: bool
    ) -> List[Repository]:
        """Get list of repositories to analyze."""
        repos = []
        
        if specific_repos:
            # Analyze specific repositories
            for repo_name in specific_repos:
                try:
                    if '/' in repo_name:
                        repo = self.github.get_repo(repo_name)
                    else:
                        repo = user.get_repo(repo_name)
                    repos.append(repo)
                except GithubException as e:
                    logger.warning(f"Could not access repository {repo_name}: {e}")
        else:
            # Get user's repositories
            try:
                user_repos = list(user.get_repos(type='all', sort='updated'))
                repos.extend(user_repos[:25])  # Limit to avoid rate limits
                
                if include_contributions:
                    # Get repositories with contributions (limited)
                    events = list(user.get_events()[:50])  # Recent events
                    contrib_repos = set()
                    
                    for event in events:
                        if hasattr(event, 'repo') and event.repo:
                            if event.repo.owner.login != user.login:  # Not own repo
                                contrib_repos.add(event.repo)
                    
                    repos.extend(list(contrib_repos)[:10])  # Limit contributions
                    
            except GithubException as e:
                logger.warning(f"Could not get repositories for user: {e}")
        
        return repos
    
    async def _analyze_repository(
        self,
        repo: Repository,
        username: str,
        since_date: datetime
    ) -> Optional[RepositoryAnalysis]:
        """Analyze a single repository for the developer's contributions."""
        try:
            # Check rate limits (simplified check)
            try:
                rate_limit = self.github.get_rate_limit()
                remaining = getattr(rate_limit, 'core', rate_limit).remaining
                if remaining < self.rate_limit_buffer:
                    logger.warning("Approaching GitHub rate limit, skipping detailed analysis")
                    return None
            except Exception as e:
                logger.warning(f"Could not check rate limit: {e}, continuing anyway")
            
            # Get basic repository info
            repo_analysis = RepositoryAnalysis(
                name=repo.name,
                url=repo.html_url,
                description=repo.description,
                primary_language=repo.language,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                size_kb=repo.size,
                topics=list(repo.get_topics()) if hasattr(repo, 'get_topics') else []
            )
            
            # Get languages
            try:
                languages = repo.get_languages()
                repo_analysis.languages = languages
            except GithubException:
                pass
            
            # Analyze commits by this user
            commits_data = await self._analyze_commits(repo, username, since_date)
            repo_analysis.commits_count = commits_data['count']
            repo_analysis.additions = commits_data['additions']
            repo_analysis.deletions = commits_data['deletions']
            repo_analysis.first_contribution = commits_data['first_commit']
            repo_analysis.last_contribution = commits_data['last_commit']
            
            # Analyze pull requests
            pr_data = await self._analyze_pull_requests(repo, username, since_date)
            repo_analysis.pull_requests = pr_data['count']
            
            # Analyze issues
            issues_data = await self._analyze_issues(repo, username, since_date)
            repo_analysis.issues_created = issues_data['created']
            repo_analysis.issues_resolved = issues_data['resolved']
            
            # Determine role in project
            repo_analysis.role_in_project = self._determine_project_role(
                repo, username, commits_data, pr_data, issues_data
            )
            
            # Calculate complexity score
            repo_analysis.complexity_score = self._calculate_repository_complexity(
                repo, repo_analysis
            )
            
            return repo_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo.name}: {e}")
            return None
    
    async def _analyze_commits(
        self, repo: Repository, username: str, since_date: datetime
    ) -> Dict[str, Any]:
        """Analyze commits by the user in the repository."""
        commits_data = {
            'count': 0,
            'additions': 0,
            'deletions': 0,
            'first_commit': None,
            'last_commit': None
        }
        
        try:
            # Get all commits in the time range, then filter by user
            # This handles cases where Git author name differs from GitHub username
            commits = repo.get_commits(since=since_date)
            commit_dates = []
            
            for commit in commits:
                # Check if this commit is by the target user
                # Check both GitHub user and repository ownership
                is_user_commit = False
                
                # Method 1: Check GitHub user association
                if commit.author and commit.author.login == username:
                    is_user_commit = True
                
                # Method 2: For repository owners, count all commits in their repos
                elif repo.owner.login == username:
                    is_user_commit = True
                
                if not is_user_commit:
                    continue
                commits_data['count'] += 1
                commit_dates.append(commit.commit.author.date)
                
                # Get detailed stats (limited to avoid rate limits)
                if commits_data['count'] <= 20:  # Analyze first 20 commits in detail
                    try:
                        files = commit.files
                        for file in files:
                            commits_data['additions'] += file.additions
                            commits_data['deletions'] += file.deletions
                    except GithubException:
                        pass  # Skip if can't get file details
                
                # Limit to avoid rate limits
                if commits_data['count'] >= 50:
                    break
            
            if commit_dates:
                commits_data['first_commit'] = min(commit_dates)
                commits_data['last_commit'] = max(commit_dates)
                
        except GithubException as e:
            logger.warning(f"Could not analyze commits for {repo.name}: {e}")
        
        return commits_data
    
    async def _analyze_pull_requests(
        self, repo: Repository, username: str, since_date: datetime
    ) -> Dict[str, Any]:
        """Analyze pull requests by the user."""
        pr_data = {'count': 0, 'merged': 0, 'review_comments': 0}
        
        try:
            prs = repo.get_pulls(state='all', sort='updated', direction='desc')
            
            for pr in prs:
                if pr.updated_at < since_date:
                    break
                
                if pr.user.login == username:
                    pr_data['count'] += 1
                    if pr.merged:
                        pr_data['merged'] += 1
                
                # Count review comments by this user
                try:
                    reviews = pr.get_reviews()
                    for review in reviews:
                        if review.user.login == username:
                            pr_data['review_comments'] += 1
                except GithubException:
                    pass
                
                # Limit to avoid rate limits
                if pr_data['count'] >= 20:
                    break
                    
        except GithubException as e:
            logger.warning(f"Could not analyze pull requests for {repo.name}: {e}")
        
        return pr_data
    
    async def _analyze_issues(
        self, repo: Repository, username: str, since_date: datetime
    ) -> Dict[str, Any]:
        """Analyze issues created and resolved by the user."""
        issues_data = {'created': 0, 'resolved': 0, 'commented': 0}
        
        try:
            issues = repo.get_issues(state='all', sort='updated', direction='desc')
            
            for issue in issues:
                if issue.updated_at < since_date:
                    break
                
                # Don't count pull requests as issues
                if issue.pull_request:
                    continue
                
                if issue.user.login == username:
                    issues_data['created'] += 1
                    if issue.state == 'closed':
                        issues_data['resolved'] += 1
                
                # Check if user commented
                try:
                    comments = issue.get_comments()
                    for comment in comments:
                        if comment.user.login == username:
                            issues_data['commented'] += 1
                            break
                except GithubException:
                    pass
                
                # Limit to avoid rate limits
                if issues_data['created'] + issues_data['commented'] >= 30:
                    break
                    
        except GithubException as e:
            logger.warning(f"Could not analyze issues for {repo.name}: {e}")
        
        return issues_data
    
    def _determine_project_role(
        self, repo: Repository, username: str, commits_data: Dict, 
        pr_data: Dict, issues_data: Dict
    ) -> str:
        """Determine the user's role in the project."""
        try:
            # Check if user is owner
            if repo.owner.login == username:
                return "owner"
            
            # Check if user is a collaborator
            try:
                if repo.has_in_collaborators(username):
                    return "maintainer"
            except GithubException:
                pass
            
            # Determine based on activity level
            total_activity = (
                commits_data['count'] + 
                pr_data['count'] + 
                issues_data['created']
            )
            
            if total_activity >= 20:
                return "active_contributor"
            elif total_activity >= 5:
                return "contributor"
            else:
                return "occasional_contributor"
                
        except Exception:
            return "contributor"
    
    def _calculate_repository_complexity(
        self, repo: Repository, repo_analysis: RepositoryAnalysis
    ) -> float:
        """Calculate a complexity score for the repository."""
        complexity_score = 0.0
        
        # Language diversity (more languages = higher complexity)
        language_count = len(repo_analysis.languages)
        complexity_score += min(language_count / 5.0, 1.0) * 0.3
        
        # Repository size
        size_score = min(repo.size / 10000, 1.0)  # Normalize by 10MB
        complexity_score += size_score * 0.2
        
        # Stars and forks (popularity indicator)
        popularity_score = min((repo.stargazers_count + repo.forks_count) / 100, 1.0)
        complexity_score += popularity_score * 0.2
        
        # Contribution level
        contribution_score = min(repo_analysis.commits_count / 50, 1.0)
        complexity_score += contribution_score * 0.3
        
        return min(complexity_score, 1.0)
    
    def _aggregate_analysis_results(
        self,
        username: str,
        profile_data: Dict[str, Any],
        repository_analyses: List[RepositoryAnalysis],
        time_range_months: int
    ) -> GitHubAnalysisResult:
        """Aggregate all analysis results into a single result object."""
        
        result = GitHubAnalysisResult(
            username=username,
            profile_data=profile_data,
            repositories=repository_analyses,
            time_range_analyzed=time_range_months
        )
        
        # Aggregate metrics
        result.total_repositories = len(repository_analyses)
        result.owned_repositories = len([r for r in repository_analyses if r.role_in_project == "owner"])
        result.contributed_repositories = result.total_repositories - result.owned_repositories
        
        # Sum up metrics
        for repo in repository_analyses:
            result.total_commits += repo.commits_count
            result.total_additions += repo.additions
            result.total_deletions += repo.deletions
            result.total_pull_requests += repo.pull_requests
            result.total_issues += repo.issues_created
            result.total_stars_earned += repo.stars
        
        # Language analysis
        language_totals = defaultdict(int)
        for repo in repository_analyses:
            for lang, lines in repo.languages.items():
                language_totals[lang] += lines
        
        if language_totals:
            total_lines = sum(language_totals.values())
            result.language_distribution = {
                lang: count / total_lines for lang, count in language_totals.items()
            }
            result.primary_languages = sorted(
                language_totals.keys(), 
                key=language_totals.get, 
                reverse=True
            )[:5]
        
        # Calculate additional metrics
        result.consistency_score = self._calculate_consistency_score(repository_analyses)
        result.documentation_score = self._calculate_documentation_score(repository_analyses)
        
        return result
    
    def _calculate_consistency_score(self, repositories: List[RepositoryAnalysis]) -> float:
        """Calculate consistency score based on regular activity."""
        if not repositories:
            return 0.0
        
        # Simple consistency based on number of repositories with recent activity
        active_repos = len([r for r in repositories if r.commits_count > 0])
        return min(active_repos / max(len(repositories), 1), 1.0)
    
    def _calculate_documentation_score(self, repositories: List[RepositoryAnalysis]) -> float:
        """Calculate documentation score based on repository descriptions and topics."""
        if not repositories:
            return 0.0
        
        documented_repos = len([
            r for r in repositories 
            if r.description and len(r.description.strip()) > 10
        ])
        
        return documented_repos / len(repositories)
    
    async def discover_collaborators(
        self, 
        include_metadata: bool = False,
        filter_active: bool = True,
        max_repositories: int = 20
    ) -> List[Any]:
        """
        Discover all collaborators across the authenticated user's repositories.
        
        This method searches through accessible repositories to find collaborators,
        contributors, and team members who have worked on projects.
        
        Args:
            include_metadata: Include additional metadata (commit counts, last activity, etc.)
            filter_active: Only include recently active collaborators
            max_repositories: Maximum number of repositories to analyze (prevents timeout)
        
        Returns:
            List of collaborators with optional metadata
        """
        try:
            logger.info("Starting collaborator discovery across repositories...")
            
            collaborators_data = {}
            current_user = self.github.get_user()
            
            # Get repositories but limit the number to prevent timeout
            repositories = list(current_user.get_repos(type='all'))
            
            # Prioritize more recent/active repositories
            repositories.sort(key=lambda r: r.updated_at, reverse=True)
            
            # Limit repositories to analyze
            if len(repositories) > max_repositories:
                repositories = repositories[:max_repositories]
                logger.info(f"Limited analysis to {max_repositories} most recent repositories")
            
            logger.info(f"Analyzing {len(repositories)} repositories for collaborators...")
            
            for i, repo in enumerate(repositories):
                logger.info(f"Processing repository {i+1}/{len(repositories)}: {repo.name}")
                try:
                    # Get collaborators for this repository
                    repo_collaborators = list(repo.get_collaborators())
                    
                    for collaborator in repo_collaborators:
                        username = collaborator.login
                        
                        if username not in collaborators_data:
                            collaborators_data[username] = {
                                'username': username,
                                'name': collaborator.name or username,
                                'repositories': [],
                                'total_repositories': 0,
                                'commit_count': 0,
                                'last_activity': None
                            }
                        
                        # Add this repository to the collaborator's data
                        collaborators_data[username]['repositories'].append({
                            'name': repo.name,
                            'url': repo.html_url,
                            'language': repo.language,
                            'stars': repo.stargazers_count
                        })
                        collaborators_data[username]['total_repositories'] += 1
                        
                        # If metadata is requested, get more detailed information (but limit API calls)
                        if include_metadata:
                            try:
                                # Get recent commits by this collaborator (limit to 5 to speed up)
                                commits = list(repo.get_commits(author=collaborator, since=datetime.now() - timedelta(days=90)))[:5]
                                collaborators_data[username]['commit_count'] += len(commits)
                                
                                if commits:
                                    latest_commit_date = commits[0].commit.author.date
                                    if (not collaborators_data[username]['last_activity'] or 
                                        latest_commit_date > collaborators_data[username]['last_activity']):
                                        collaborators_data[username]['last_activity'] = latest_commit_date.isoformat()
                                        
                            except Exception as e:
                                logger.debug(f"Could not get commit data for {username} in {repo.name}: {e}")
                                # Don't fail the entire process for individual commit failures
                                pass
                    
                except Exception as e:
                    logger.debug(f"Could not access collaborators for repository {repo.name}: {e}")
                    continue
            
            # Convert to list and apply filtering
            collaborators_list = list(collaborators_data.values())
            
            # Filter out inactive collaborators if requested
            if filter_active and include_metadata:
                cutoff_date = datetime.now() - timedelta(days=180)  # 6 months
                collaborators_list = [
                    c for c in collaborators_list 
                    if (c.get('last_activity') and 
                        datetime.fromisoformat(c['last_activity'].replace('Z', '+00:00')) > cutoff_date)
                ]
            
            # Sort by number of repositories (most active first)
            collaborators_list.sort(key=lambda x: x['total_repositories'], reverse=True)
            
            logger.info(f"Discovered {len(collaborators_list)} collaborators")
            
            # Return simple list of usernames if no metadata requested
            if not include_metadata:
                return [collab['username'] for collab in collaborators_list]
            
            return collaborators_list
            
        except Exception as e:
            logger.error(f"Error discovering collaborators: {e}")
            return []
    
    async def get_organization_tech_stack(self) -> Dict[str, Any]:
        """
        Analyze the technical stack across all accessible repositories.
        
        Returns comprehensive information about programming languages, frameworks,
        tools, and technologies used across the organization.
        
        Returns:
            Dictionary containing technology stack analysis
        """
        try:
            logger.info("Analyzing organization-wide technical stack...")
            
            tech_stack = {
                'programming_languages': defaultdict(int),
                'frameworks': defaultdict(int),
                'tools': defaultdict(int),
                'databases': defaultdict(int),
                'topics': defaultdict(int)
            }
            
            current_user = self.github.get_user()
            repositories = list(current_user.get_repos(type='all'))
            
            analyzed_repos = 0
            
            for repo in repositories:
                try:
                    analyzed_repos += 1
                    
                    # Get programming languages
                    languages = repo.get_languages()
                    for language, bytes_count in languages.items():
                        tech_stack['programming_languages'][language] += bytes_count
                    
                    # Get topics (tags)
                    topics = repo.get_topics()
                    for topic in topics:
                        tech_stack['topics'][topic] += 1
                    
                    # Analyze README for framework mentions
                    try:
                        readme = repo.get_readme()
                        readme_content = readme.decoded_content.decode('utf-8').lower()
                        
                        # Common frameworks to detect
                        frameworks = [
                            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
                            'laravel', 'rails', 'symfony', 'jquery', 'bootstrap', 'tailwind',
                            'nodejs', 'nextjs', 'nuxtjs', 'fastapi', 'gin', 'echo'
                        ]
                        
                        for framework in frameworks:
                            if framework in readme_content:
                                tech_stack['frameworks'][framework] += 1
                        
                        # Common tools and databases
                        tools = ['docker', 'kubernetes', 'jenkins', 'gitlab', 'travis', 'circleci']
                        databases = ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle']
                        
                        for tool in tools:
                            if tool in readme_content:
                                tech_stack['tools'][tool] += 1
                                
                        for db in databases:
                            if db in readme_content:
                                tech_stack['databases'][db] += 1
                                
                    except Exception as e:
                        logger.debug(f"Could not analyze README for {repo.name}: {e}")
                    
                except Exception as e:
                    logger.debug(f"Could not analyze repository {repo.name}: {e}")
                    continue
            
            # Convert defaultdicts to regular dicts and sort
            result = {
                'technologies': {
                    'programming_languages': dict(sorted(
                        tech_stack['programming_languages'].items(), 
                        key=lambda x: x[1], reverse=True
                    )),
                    'frameworks': dict(sorted(
                        tech_stack['frameworks'].items(),
                        key=lambda x: x[1], reverse=True
                    )),
                    'tools': dict(sorted(
                        tech_stack['tools'].items(),
                        key=lambda x: x[1], reverse=True
                    )),
                    'databases': dict(sorted(
                        tech_stack['databases'].items(),
                        key=lambda x: x[1], reverse=True
                    )),
                    'topics': dict(sorted(
                        tech_stack['topics'].items(),
                        key=lambda x: x[1], reverse=True
                    ))
                },
                'summary': {
                    'total_languages': len(tech_stack['programming_languages']),
                    'total_frameworks': len(tech_stack['frameworks']),
                    'total_tools': len(tech_stack['tools']),
                    'total_databases': len(tech_stack['databases']),
                    'total_topics': len(tech_stack['topics']),
                    'most_used_language': max(tech_stack['programming_languages'].items(), 
                                            key=lambda x: x[1])[0] if tech_stack['programming_languages'] else 'Unknown',
                    'repositories_analyzed': analyzed_repos
                },
                'repositories_count': analyzed_repos
            }
            
            logger.info(f"Technical stack analysis complete: {analyzed_repos} repositories analyzed")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing technical stack: {e}")
            return {
                'technologies': {},
                'summary': {},
                'repositories_count': 0
            }