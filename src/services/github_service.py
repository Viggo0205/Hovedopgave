"""GitHub service for raw data fetching from GitHub API."""

from typing import Dict, Any
from github import Github, Auth
from config import Config
from shared.data_sanitizer import sanitize_developer_profile, sanitize_list



class GitHubService:
    """Service for fetching raw data from GitHub API."""
    
    def __init__(self):
        self.config = Config()
        github_token = self.config.github_token
        auth = Auth.Token(github_token)
        self.github = Github(auth=auth)
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get raw user profile data from GitHub."""
        user = self.github.get_user(username)
        profile = {
            "username": user.login,
            "name": user.name,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        return sanitize_developer_profile(profile)
    
    def get_user_repositories(self, username: str, limit: int = 50) -> list:
        """Get raw repository data for a user."""
        user = self.github.get_user(username)
        repos = []
        
        for repo in list(user.get_repos(type='public'))[:limit]:
            repo_data = {
                "name": repo.name,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "size": repo.size,
                "languages": repo.get_languages()
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
    
    def get_user_languages(self, username: str) -> Dict[str, int]:
        """Get language data for a user - combines repository fetching and language extraction."""
        repositories = self.get_user_repositories(username)
        return self.get_language_data(repositories)
    
 # sprint 2
    def get_organization_members(self, org_name: str) -> list:
        """Get all public members of an organization."""
        try:
            org = self.github.get_organization(org_name)
            members = []
            
            for member in org.get_members():
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
        except Exception as e:
            print(f"Error fetching organization members: {e}")
            return []
    
    def get_organization_repositories(self, org_name: str, limit: int = 50) -> list:
        """Get repositories from an organization."""
        try:
            org = self.github.get_organization(org_name)
            repos = []
            
            for repo in list(org.get_repos())[:limit]:
                repo_data = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "size": repo.size,
                    "languages": repo.get_languages(),
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                }
                repos.append(repo_data)
            
            return repos
        except Exception as e:
            print(f"Error fetching organization repositories: {e}")
            return []
    
    def get_repository_contributors(self, repo_owner: str, repo_name: str) -> list:
        """Get contributors for a specific repository."""
        try:
            repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
            contributors = []
            
            for contributor in repo.get_contributors():
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
        except Exception as e:
            print(f"Error fetching repository contributors: {e}")
            return []