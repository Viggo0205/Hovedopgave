"""
Configuration Management for Developer Skill Analyzer MCP Server.

This module handles all configuration settings for the skill analysis system,
including API keys, rate limiting, caching, and operational parameters.

Configuration Sources:
1. Environment variables (.env file)
2. Default values for optional settings
3. Runtime configuration validation

Key Configuration Areas:
- API Authentication (GitHub, Jira, OpenAI, etc.)
- Rate Limiting and Request Management
- Caching Configuration
- Logging and Debugging
- Analysis Parameters (time ranges, limits)
- Mock Mode for Testing

Author: Developer Skill Analyzer Project
Version: Enhanced with comprehensive API management
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows configuration through environment variables or .env file
load_dotenv()


class Config:
    """
    Centralized Configuration Management for the Developer Skill Analyzer.
    
    This class manages all configuration settings including:
    - API credentials for external services
    - Rate limiting and performance settings
    - Analysis parameters and limits
    - Caching and logging configuration
    - Mock mode for testing without real API calls
    
    All settings are loaded from environment variables with sensible defaults.
    """
    
    def __init__(self):
        """
        Initialize configuration by loading all settings from environment variables.
        
        Environment Variables:
        - MOCK_MODE: Enable/disable mock data for testing (default: true)
        - GITHUB_ACCESS_TOKEN: GitHub API authentication token
        - JIRA_SERVER_URL, JIRA_EMAIL, JIRA_API_TOKEN: Jira API settings
        - API rate limiting and caching settings
        - Analysis parameters (time ranges, result limits)
        """
        # Mock Mode Configuration - allows testing without real API calls
        # When enabled, uses mock data instead of making actual API requests
        mock_mode_env = os.getenv("MOCK_MODE", "true").lower()
        self.mock_mode: bool = mock_mode_env == "true"
        
        # GitHub API Configuration
        self.github_token: Optional[str] = (
            os.getenv("GITHUB_ACCESS_TOKEN") or 
            os.getenv("GITHUB_TOKEN")
        )
        
        # Force real mode for Claude Desktop if we have a valid token
        if self.github_token and self.github_token.startswith("ghp_"):
            self.mock_mode = False
        
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
            # Use logging instead of print to avoid interfering with MCP JSON output
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Configuration issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
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