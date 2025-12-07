import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

from config import Config
from services.github_service import GitHubService
from analyzers.github_analyzer import GitHubAnalyzer

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Developer Skill Analyzer")

@mcp.tool()
async def analyze_github_developer(
    username: Optional[str] = None,
    repositories: Optional[List[str]] = None,
    include_contributions: bool = True,
    time_range_months: int = 12
) -> Dict[str, Any]:
    #  Python docstrings
    """
    Analyze developer skills based on GitHub activity.
    
    Fetches user repositories and analyzes programming languages used.
    Uses the configured GitHub username if none is provided.
    
    Args:
        username: GitHub username to analyze (optional, uses configured user if not provided)
        repositories: Not currently used
        include_contributions: Not currently used
        time_range_months: Not currently used
    
    Returns:
        Developer analysis including:
        - Programming languages and skill levels
        - Repository count and basic profile info
        - Language expertise categorization
    """
    try:
        config = Config()
        
        # Use configured username if none provided
        username = username or config.github_username
        if not username:
            return {
                "error": "No GitHub username provided and no default username configured in GITHUB_USERNAME environment variable"
            }
        
        # Initialize service and analyzer properly
        github_service = GitHubService()
        analyzer = GitHubAnalyzer(github_service)
        
        logger.info(f"Starting GitHub analysis for user: {username}")
        
        # Perform the analysis
        analysis_result = await analyzer.analyze_developer(username)
        
        return {
            "developer": username,
            "analysis_type": "github",
            "data_source": "real_api",
            "time_range_months": time_range_months,
            "username": analysis_result.get("username"),
            "profile": analysis_result.get("profile", {}),
            "language_skills": analysis_result.get("language_skills", {}),
            "expertise_areas": analysis_result.get("expertise_areas", {}),
            "total_repositories": analysis_result.get("total_repositories", 0),
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing GitHub developer {username}: {str(e)}")
        return {
            "error": f"Failed to analyze GitHub developer: {str(e)}",
            "developer": username,
            "analysis_type": "github",
            "data_source": "error"
        }



@mcp.tool()
async def get_github_profile(
    github_username: Optional[str] = None
) -> Dict[str, Any]:
    #  Python docstrings
    """
    Get basic GitHub profile information for a developer.
    Uses the configured GitHub username if none is provided.
    
    Args:
        github_username: GitHub username to analyze (optional, uses configured user if not provided)
    
    Returns:
        Basic profile information including repositories and languages
    """
    try:
        config = Config()
        
        # Use configured username if none provided
        github_username = github_username or config.github_username
        if not github_username:
            return {
                "error": "No GitHub username provided and no default username configured in GITHUB_USERNAME environment variable"
            }
        
        github_service = GitHubService()
        analyzer = GitHubAnalyzer(github_service)
        
        # Get basic profile info
        profile_result = await analyzer.get_basic_profile(github_username)
        
        return {
            "developer": github_username,
            "analysis_type": "github_profile",
            "profile_data": profile_result,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting GitHub profile for {github_username}: {str(e)}")
        return {
            "error": f"Failed to get GitHub profile: {str(e)}",
            "developer": github_username
        }


@mcp.tool()
async def compare_developers(
    developer1_github: str,
    developer2_github: str,
    comparison_metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    #  Python docstrings
    """
    Compare skill profiles between two developers.
    
    Args:
        developer1_github: First developer's GitHub username
        developer2_github: Second developer's GitHub username
        comparison_metrics: Specific metrics to compare
    
    Returns:
        Detailed comparison analysis
    """
    try:
        # Analyze both developers using proper service layer
        github_service = GitHubService()
        analyzer = GitHubAnalyzer(github_service)
        
        dev1_analysis = await analyzer.analyze_developer(developer1_github)
        dev2_analysis = await analyzer.analyze_developer(developer2_github)
        
        # Simple comparison - return both analyses
        return {
            "comparison_type": "github_raw_data",
            "developers": {
                "developer1": developer1_github,
                "developer2": developer2_github
            },
            "individual_assessments": {
                "developer1": dev1_analysis,
                "developer2": dev2_analysis
            },
            "analysis_date": datetime.now().isoformat(),
            "comparison_summary": {
                "dev1_languages": len(dev1_analysis.get("language_skills", {})),
                "dev2_languages": len(dev2_analysis.get("language_skills", {})),
                "dev1_repos": dev1_analysis.get("total_repositories", 0),
                "dev2_repos": dev2_analysis.get("total_repositories", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing developers: {str(e)}")
        return {
            "error": f"Failed to compare developers: {str(e)}",
            "developers": {
                "developer1": developer1_github,
                "developer2": developer2_github
            }
        }


@mcp.resource("github://available-languages")
async def get_available_languages() -> str:
    """List all programming languages we can analyze dynamically from constants."""
    from shared.language_categories import LANGUAGE_CATEGORIES
    language_categories = LANGUAGE_CATEGORIES
    
    result = "# Supported Programming Languages\n\n"
    for category, languages in language_categories.items():
        result += f"## {category}\n"
        result += f"- {', '.join(languages)}\n\n"
    
    result += "All languages are categorized into expertise areas and skill levels (Beginner → Expert)."
    return result


@mcp.prompt("analyze-developer-skills")
async def analyze_developer_prompt(username: str) -> str:
    """Generate a prompt for comprehensive developer analysis."""
    return f"""
Analyze the GitHub developer '{username}' and provide insights on:

1. **Programming Languages**: What languages they use and skill levels
2. **Expertise Areas**: Web development, mobile, data science, etc.  
3. **Activity Pattern**: Repository count and coding activity
4. **Strengths**: What they're best at based on code volume and diversity

Focus on practical insights that would be useful for:
- Technical interviews
- Team assignments  
- Skill development planning
- Project matching

Be specific about their technical capabilities and experience level.
"""


def main() -> None:
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()