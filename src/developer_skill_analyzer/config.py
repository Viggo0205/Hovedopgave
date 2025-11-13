"""
Configuration management for the Developer Skill Analyzer.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # GitHub API Configuration
        self.github_token: Optional[str] = os.getenv("GITHUB_ACCESS_TOKEN")
        
        # Jira API Configuration
        self.jira_server_url: Optional[str] = os.getenv("JIRA_SERVER_URL")
        self.jira_email: Optional[str] = os.getenv("JIRA_EMAIL")
        self.jira_api_token: Optional[str] = os.getenv("JIRA_API_TOKEN")
        
        # Rate Limiting Configuration
        self.api_rate_limit: int = int(os.getenv("API_RATE_LIMIT", "100"))
        self.github_rate_limit: int = int(os.getenv("GITHUB_RATE_LIMIT", "5000"))
        self.jira_rate_limit: int = int(os.getenv("JIRA_RATE_LIMIT", "200"))
        
        # Cache Configuration
        self.enable_cache: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
        
        # Logging Configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: Optional[str] = os.getenv("LOG_FILE")
        
        # Analysis Configuration
        self.default_time_range_months: int = int(os.getenv("DEFAULT_TIME_RANGE_MONTHS", "12"))
        self.max_repositories_analyzed: int = int(os.getenv("MAX_REPOSITORIES_ANALYZED", "50"))
        self.max_issues_analyzed: int = int(os.getenv("MAX_ISSUES_ANALYZED", "200"))
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        issues = []
        
        if not self.github_token:
            issues.append("GITHUB_ACCESS_TOKEN is required for GitHub analysis")
        
        if not self.jira_server_url:
            issues.append("JIRA_SERVER_URL is required for Jira analysis")
        
        if not self.jira_email:
            issues.append("JIRA_EMAIL is required for Jira analysis")
        
        if not self.jira_api_token:
            issues.append("JIRA_API_TOKEN is required for Jira analysis")
        
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        return True
    
    def get_github_configured(self) -> bool:
        """Check if GitHub configuration is complete."""
        return bool(self.github_token)
    
    def get_jira_configured(self) -> bool:
        """Check if Jira configuration is complete."""
        return all([
            self.jira_server_url,
            self.jira_email,
            self.jira_api_token
        ])