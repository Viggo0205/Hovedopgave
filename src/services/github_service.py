"""GitHub service for raw data fetching from GitHub API."""

import asyncio
import logging
import time
from typing import Dict, Any
from github import Github, Auth, RateLimitExceededException, GithubException
from asyncio_throttle import Throttler
from config import Config
from shared.data_sanitizer import sanitize_developer_profile, sanitize_list

logger = logging.getLogger(__name__)


class GitHubServiceDegradedException(Exception):
    """Raised when GitHub integration is in degraded state."""
    pass


class GitHubService:
    """Service for fetching raw data from GitHub API with rate limiting and retry logic."""
    
    # Class-level state tracking
    _degraded_state = False
    _degraded_until = 0  # Unix timestamp
    _failure_count = 0
    _max_failures_before_degraded = 3
    _degraded_duration_seconds = 300  # 5 minutes
    
    def __init__(self):
        self.config = Config()
        github_token = self.config.github_token
        auth = Auth.Token(github_token)
        self.github = Github(auth=auth)
        
        # Initialize rate limiter: max X requests per hour
        # GitHub free tier: 5000 requests/hour = ~83 requests/minute = 1.38 req/sec
        # We'll use conservative 60 requests/minute to stay safe
        requests_per_minute = 60
        self.throttler = Throttler(rate_limit=requests_per_minute, period=60.0)
        
        logger.info(f"GitHubService initialized with rate limit: {requests_per_minute} req/min")
    
    @classmethod
    def is_degraded(cls) -> bool:
        """Check if service is in degraded state."""
        if cls._degraded_state and time.time() < cls._degraded_until:
            return True
        elif cls._degraded_state and time.time() >= cls._degraded_until:
            # Recovery time passed, reset state
            cls._degraded_state = False
            cls._failure_count = 0
            logger.info("GitHub integration recovered from degraded state")
        return False
    
    @classmethod
    def mark_degraded(cls):
        """Mark the service as degraded after repeated failures."""
        cls._degraded_state = True
        cls._degraded_until = time.time() + cls._degraded_duration_seconds
        logger.error(
            f"GitHub integration marked as DEGRADED for {cls._degraded_duration_seconds}s "
            f"after {cls._failure_count} failures"
        )
    
    @classmethod
    def increment_failure(cls):
        """Increment failure count and mark degraded if threshold reached."""
        cls._failure_count += 1
        if cls._failure_count >= cls._max_failures_before_degraded:
            cls.mark_degraded()
    
    @classmethod
    def reset_failures(cls):
        """Reset failure count after successful request."""
        if cls._failure_count > 0:
            cls._failure_count = 0
            logger.debug("GitHub service failure count reset after successful request")
    
    async def _api_call_with_retry(self, func, *args, max_retries=3, **kwargs):
        """
        Execute API call with exponential backoff retry logic.
        
        Args:
            func: The API function to call
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result of the API call
            
        Raises:
            GitHubServiceDegradedException: If service is degraded
            Exception: If all retries exhausted
        """
        # Check degraded state first
        if self.is_degraded():
            raise GitHubServiceDegradedException(
                f"GitHub integration is degraded until {time.ctime(self._degraded_until)}"
            )
        
        # Apply rate limiting
        async with self.throttler:
            for attempt in range(max_retries):
                try:
                    # Execute the API call
                    result = func(*args, **kwargs)
                    
                    # Success - reset failure counter
                    self.reset_failures()
                    return result
                    
                except RateLimitExceededException as e:
                    # HTTP 429 - Rate limit exceeded
                    retry_after = getattr(e, 'retry_after', None)
                    wait_time = retry_after if retry_after else (2 ** attempt) * 5
                    
                    logger.warning(
                        f"Rate limit exceeded (attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {wait_time}s before retry..."
                    )
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                    else:
                        self.increment_failure()
                        raise
                        
                except GithubException as e:
                    # Other GitHub API errors
                    if e.status == 429:
                        # Alternative way 429 might be reported
                        wait_time = (2 ** attempt) * 5
                        logger.warning(
                            f"HTTP 429 detected (attempt {attempt + 1}/{max_retries}). "
                            f"Backing off for {wait_time}s..."
                        )
                        if attempt < max_retries - 1:
                            await asyncio.sleep(wait_time)
                        else:
                            self.increment_failure()
                            raise
                    else:
                        # Non-rate-limit error, don't retry
                        logger.error(f"GitHub API error: {e}")
                        self.increment_failure()
                        raise
                        
                except Exception as e:
                    # Unexpected errors
                    logger.error(f"Unexpected error in GitHub API call: {e}")
                    self.increment_failure()
                    raise
        
        # Should not reach here
        raise Exception("API call failed after all retries")
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get raw user profile data from GitHub with rate limiting."""
        user = await self._api_call_with_retry(self.github.get_user, username)
        profile = {
            "username": user.login,
            "name": user.name,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        return sanitize_developer_profile(profile)
    
    async def get_user_repositories(self, username: str, limit: int = 50) -> list:
        """Get raw repository data for a user with rate limiting."""
        user = await self._api_call_with_retry(self.github.get_user, username)
        repos = []
        
        # Get repos with rate limiting
        all_repos = await self._api_call_with_retry(lambda: list(user.get_repos(type='public'))[:limit])
        
        for repo in all_repos:
            # Each repo.get_languages() is an API call, so rate limit it too
            languages = await self._api_call_with_retry(repo.get_languages)
            repo_data = {
                "name": repo.name,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "size": repo.size,
                "languages": languages
            }
            repos.append(repo_data)
        
        return repos
    
    def get_language_data(self, repositories: list) -> Dict[str, int]:
        """Extract raw language data from repositories."""
        language_totals = {}
        for repo in repositories:
            if repo.get("languages"):
                for lang, lines in repo["languages"].items():
                    if lang in language_totals:
                        language_totals[lang] += lines
                    else:
                        language_totals[lang] = lines
        return language_totals
    
    async def get_user_languages(self, username: str) -> Dict[str, int]:
        """Get language data for a user - combines repository fetching and language extraction."""
        repositories = await self.get_user_repositories(username)
        return self.get_language_data(repositories)
    
 # sprint 2
    async def get_organization_members(self, org_name: str) -> list:
        """Get all public members of an organization with rate limiting."""
        try:
            org = await self._api_call_with_retry(self.github.get_organization, org_name)
            members = []
            
            all_members = await self._api_call_with_retry(lambda: list(org.get_members()))
            
            for member in all_members:
                member_data = {
                    "username": member.login,
                    "name": member.name,
                    "company": member.company,
                    "email": member.email,
                    "bio": member.bio,
                    "public_repos": member.public_repos,
                    "followers": member.followers,
                    "created_at": member.created_at.isoformat() if member.created_at else None
                }
                members.append(member_data)
            
            return sanitize_list(members)
        except GitHubServiceDegradedException:
            logger.error(f"Cannot fetch organization members - service degraded")
            raise
        except Exception as e:
            logger.error(f"Error fetching organization members: {e}")
            return []
    
    async def get_organization_repositories(self, org_name: str, limit: int = 50) -> list:
        """Get repositories from an organization with rate limiting."""
        try:
            org = await self._api_call_with_retry(self.github.get_organization, org_name)
            repos = []
            
            all_repos = await self._api_call_with_retry(lambda: list(org.get_repos())[:limit])
            
            for repo in all_repos:
                languages = await self._api_call_with_retry(repo.get_languages)
                repo_data = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "size": repo.size,
                    "languages": languages,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                }
                repos.append(repo_data)
            
            return repos
        except GitHubServiceDegradedException:
            logger.error(f"Cannot fetch organization repositories - service degraded")
            raise
        except Exception as e:
            logger.error(f"Error fetching organization repositories: {e}")
            return []
    
    async def get_repository_contributors(self, repo_owner: str, repo_name: str) -> list:
        """Get contributors for a specific repository with rate limiting."""
        try:
            repo = await self._api_call_with_retry(self.github.get_repo, f"{repo_owner}/{repo_name}")
            contributors = []
            
            all_contributors = await self._api_call_with_retry(lambda: list(repo.get_contributors()))
            
            for contributor in all_contributors:
                contributor_data = {
                    "username": contributor.login,
                    "name": contributor.name,
                    "contributions": contributor.contributions,
                    "company": contributor.company,
                    "email": contributor.email,
                    "public_repos": contributor.public_repos
                }
                contributors.append(contributor_data)
            
            return sanitize_list(contributors)
        except GitHubServiceDegradedException:
            logger.error(f"Cannot fetch repository contributors - service degraded")
            raise
        except Exception as e:
            logger.error(f"Error fetching repository contributors: {e}")
            return []