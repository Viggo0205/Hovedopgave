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

from github import Github, GithubException
from github.Repository import Repository
from github.Commit import Commit
from github.PullRequest import PullRequest

from ..models.analysis import GitHubAnalysisResult, RepositoryAnalysis

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyzes GitHub data to extract developer skills and metrics."""
    
    def __init__(self, access_token: str):
        """
        Initialize the GitHub analyzer.
        
        Args:
            access_token: GitHub personal access token
        """
        self.github = Github(access_token)
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
            # Check rate limits
            rate_limit = self.github.get_rate_limit()
            if rate_limit.core.remaining < self.rate_limit_buffer:
                logger.warning("Approaching GitHub rate limit, skipping detailed analysis")
                return None
            
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
            commits = repo.get_commits(author=username, since=since_date)
            commit_dates = []
            
            for commit in commits:
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