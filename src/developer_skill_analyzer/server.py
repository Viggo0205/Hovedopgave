"""
FastMCP Server for Developer Skill Analysis - Main MCP Server Implementation.

This is the core MCP (Model Context Protocol) server that provides comprehensive
developer skill analysis capabilities through structured tool interfaces.

Server Architecture:
1. MCP Tool Registration: Exposes analysis functions as MCP tools
2. GitHub Integration: Repository analysis, commit patterns, language detection
3. Jira Integration: Issue analysis, project involvement, task complexity
4. Skill Processing: Advanced algorithms for skill extraction and proficiency assessment
5. Data Aggregation: Combines multiple data sources for comprehensive analysis

MCP Tools Provided:
- analyze_github_user: Complete GitHub profile and repository analysis
- analyze_repository: Detailed single repository analysis
- analyze_jira_user: Jira activity and issue resolution analysis
- assess_skills: Cross-platform skill assessment and gap analysis
- get_skill_recommendations: Personalized learning recommendations

Key Features:
- Real-time API data fetching from GitHub and Jira
- Intelligent skill extraction from code and project metadata
- Proficiency level assessment based on usage patterns
- Collaborative analysis and team skill mapping
- Performance metrics and productivity insights

Configuration:
- GitHub and Jira API integration
- Configurable rate limiting and caching
- Flexible analysis parameters
- Comprehensive logging and error handling

Author: Developer Skill Analyzer Project
Version: Enhanced MCP server with comprehensive analysis capabilities
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import redirect_stdout
from io import StringIO

from fastmcp import FastMCP
from pydantic import BaseModel

from .config import Config
from .models.developer import DeveloperProfile, SkillAssessment
from .analyzers.github_analyzer import GitHubAnalyzer
from .analyzers.jira_analyzer import JiraAnalyzer
from .analyzers.skill_processor import SkillProcessor

# Initialize logging - completely disable logging to prevent any stdout interference
logging.basicConfig(
    level=logging.CRITICAL,  # Only show critical errors
    handlers=[
        logging.NullHandler(),  # Discard all log messages completely
    ]
)
logger = logging.getLogger(__name__)
logger.disabled = True  # Completely disable this logger

# Initialize MCP server
mcp = FastMCP("Developer Skill Analyzer")

# Utility function to suppress stdout during tool execution
def suppress_stdout(func):
    """Decorator to suppress all stdout output during function execution."""
    async def wrapper(*args, **kwargs):
        # Redirect stdout to a StringIO buffer to discard it
        with redirect_stdout(StringIO()):
            return await func(*args, **kwargs)
    return wrapper


class GitHubAnalysisRequest(BaseModel):
    """Request model for GitHub analysis"""
    username: str
    repositories: Optional[List[str]] = None
    include_contributions: bool = True
    time_range_months: int = 12


class JiraAnalysisRequest(BaseModel):
    """Request model for Jira analysis"""
    email: str
    projects: Optional[List[str]] = None
    include_comments: bool = True
    time_range_months: int = 6


class DeveloperComparisonRequest(BaseModel):
    """Request model for developer comparison"""
    developer1_profile: str  # Profile ID or identifier
    developer2_profile: str  # Profile ID or identifier
    comparison_metrics: Optional[List[str]] = None


class EmployeeListRequest(BaseModel):
    """Request model for getting employee names"""
    source: str = "all"  # "github", "jira", or "all"
    include_metadata: bool = False
    filter_active: bool = True


class CapabilitiesRequest(BaseModel):
    """Request model for overall capabilities analysis"""
    team_name: Optional[str] = None
    skill_categories: Optional[List[str]] = None
    include_gaps: bool = True
    aggregation_level: str = "team"  # "individual", "team", "organization"


@mcp.tool()
async def analyze_github_developer(
    username: str,
    repositories: Optional[List[str]] = None,
    include_contributions: bool = True,
    time_range_months: int = 12
) -> Dict[str, Any]:
    """
    Analyze developer skills based on GitHub activity.
    
    Examines repositories, commits, pull requests, and contributions
    to assess programming skills, technologies used, and collaboration patterns.
    
    Args:
        username: GitHub username to analyze
        repositories: Specific repositories to analyze (if None, analyzes all public repos)
        include_contributions: Whether to include contributions to other repos
        time_range_months: Number of months of history to analyze
    
    Returns:
        Comprehensive skill analysis including:
        - Programming languages and proficiency levels
        - Frameworks and tools used
        - Collaboration metrics
        - Code quality indicators
        - Learning progression
    """
    try:
        config = Config()
        analyzer = GitHubAnalyzer(config.github_token)
        
        logger.info(f"Starting GitHub analysis for user: {username}")
        
        # Perform the analysis
        analysis_result = await analyzer.analyze_developer(
            username=username,
            repositories=repositories,
            include_contributions=include_contributions,
            time_range_months=time_range_months
        )
        
        # Process skills using the skill processor
        skill_processor = SkillProcessor()
        skill_assessment = skill_processor.process_github_data(analysis_result)
        
        return {
            "developer": username,
            "analysis_type": "github",
            "data_source": "real_api",
            "time_range_months": time_range_months,
            "skill_assessment": skill_assessment,
            "analysis_date": analysis_result.get("analysis_date"),
            "summary": skill_assessment.get("summary", {}),
            "detailed_skills": skill_assessment.get("skills", {}),
            "recommendations": skill_assessment.get("recommendations", [])
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
async def analyze_jira_developer(
    email: str,
    projects: Optional[List[str]] = None,
    include_comments: bool = True,
    time_range_months: int = 6
) -> Dict[str, Any]:
    """
    Analyze developer skills based on Jira activity.
    
    Examines issue assignments, comments, project participation,
    and task complexity to assess problem-solving skills and domain knowledge.
    
    Args:
        email: Developer's email address in Jira
        projects: Specific Jira projects to analyze
        include_comments: Whether to analyze comments for communication skills
        time_range_months: Number of months of history to analyze
    
    Returns:
        Skill analysis including:
        - Domain expertise areas
        - Problem-solving complexity
        - Communication and collaboration skills
        - Project management involvement
        - Issue resolution patterns
    """
    try:
        config = Config()
        analyzer = JiraAnalyzer(
            server_url=config.jira_server_url,
            email=config.jira_email,
            api_token=config.jira_api_token
        )
        
        logger.info(f"Starting Jira analysis for user: {email}")
        
        # Perform the analysis
        analysis_result = await analyzer.analyze_developer(
            email=email,
            projects=projects,
            include_comments=include_comments,
            time_range_months=time_range_months
        )
        
        # Process skills using the skill processor
        skill_processor = SkillProcessor()
        skill_assessment = skill_processor.process_jira_data(analysis_result)
        
        return {
            "developer": email,
            "analysis_type": "jira",
            "time_range_months": time_range_months,
            "projects_analyzed": projects or analysis_result.get("projects", []),
            "skill_assessment": skill_assessment,
            "analysis_date": analysis_result.get("analysis_date"),
            "summary": skill_assessment.get("summary", {}),
            "detailed_skills": skill_assessment.get("skills", {}),
            "collaboration_metrics": skill_assessment.get("collaboration", {}),
            "recommendations": skill_assessment.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Error analyzing Jira developer {email}: {str(e)}")
        return {
            "error": f"Failed to analyze Jira developer: {str(e)}",
            "developer": email,
            "analysis_type": "jira"
        }


@mcp.tool()
async def get_all_employees(
    source: str = "all",
    include_metadata: bool = False,
    filter_active: bool = True
) -> Dict[str, Any]:
    """
    Discover all collaborators and team members from GitHub repositories and/or Jira projects.
    
    This function searches across accessible repositories to find all collaborators,
    contributors, and team members who have worked on projects.
    
    Args:
        source: Data source ("github", "jira", or "all")
        include_metadata: Include additional metadata (commit counts, last activity, etc.)
        filter_active: Only include recently active collaborators
    
    Returns:
        Dictionary containing discovered collaborators and team members with optional metadata
    """
    try:
        logger.info(f"Fetching all employees from source: {source}")
        
        config = Config()
        employees = {
            "github_employees": [],
            "jira_employees": [],
            "total_count": 0,
            "source": source,
            "metadata": {}
        }
        
        # Discover collaborators from GitHub repositories
        if source in ["github", "all"] and config.github_token:
            try:
                logger.info("Starting GitHub collaborator discovery across repositories...")
                analyzer = GitHubAnalyzer(config.github_token)
                
                # Use asyncio.wait_for to add timeout (5 minutes max)
                github_employees = await asyncio.wait_for(
                    analyzer.discover_collaborators(
                        include_metadata=include_metadata,
                        filter_active=filter_active,
                        max_repositories=15  # Limit to 15 repositories for faster results
                    ),
                    timeout=300  # 5 minute timeout
                )
                employees["github_employees"] = github_employees
                logger.info(f"Successfully discovered {len(github_employees)} GitHub collaborators")
                
                if include_metadata and github_employees:
                    logger.info(f"Metadata included: commits, repositories, last activity")
                    
            except Exception as e:
                logger.error(f"Failed to discover GitHub collaborators: {e}")
                logger.error(f"This may be due to API rate limits or repository access permissions")
                employees["github_employees"] = []
        
        if source in ["jira", "all"] and config.jira_server_url:
            try:
                logger.info("Starting Jira user discovery across projects...")
                jira_analyzer = JiraAnalyzer(
                    server_url=config.jira_server_url,
                    email=config.jira_email,
                    api_token=config.jira_api_token
                )
                jira_employees = await jira_analyzer.discover_users(
                    include_metadata=include_metadata,
                    filter_active=filter_active
                )
                employees["jira_employees"] = jira_employees
                logger.info(f"Successfully discovered {len(jira_employees)} Jira team members")
            except Exception as e:
                logger.error(f"Failed to discover Jira users: {e}")
                logger.error(f"This may be due to Jira permissions or API configuration")
                employees["jira_employees"] = []
        
        # Calculate totals
        total_github = len(employees["github_employees"])
        total_jira = len(employees["jira_employees"])
        employees["total_count"] = total_github + total_jira
        
        # Add metadata
        employees["metadata"] = {
            "github_total": total_github,
            "jira_total": total_jira,
            "query_timestamp": datetime.now().isoformat(),
            "include_metadata": include_metadata,
            "filter_active": filter_active,
            "api_status": {
                "github_configured": bool(config.github_token),
                "jira_configured": bool(config.jira_server_url)
            }
        }
        
        logger.info(f"Retrieved {employees['total_count']} employees from {source}")
        return employees
        
    except Exception as e:
        logger.error(f"Error getting employee list: {str(e)}")
        return {
            "error": f"Failed to get employee list: {str(e)}",
            "source": source,
            "total_count": 0
        }


@mcp.tool()
async def get_skill_summary(
    github_username: Optional[str] = None,
    jira_email: Optional[str] = None,
    time_range_months: int = 12
) -> Dict[str, Any]:
    """
    Generate a comprehensive skill summary combining GitHub and Jira analysis.
    
    Args:
        github_username: GitHub username for analysis
        jira_email: Jira email for analysis  
        time_range_months: Analysis time range
    
    Returns:
        Combined skill assessment and recommendations
    """
    try:
        results = {}
        
        if github_username:
            github_result = await analyze_github_developer(
                username=github_username,
                time_range_months=time_range_months
            )
            results["github"] = github_result
            
        if jira_email:
            jira_result = await analyze_jira_developer(
                email=jira_email,
                time_range_months=time_range_months
            )
            results["jira"] = jira_result
            
        # Combine and process results
        skill_processor = SkillProcessor()
        combined_assessment = skill_processor.combine_assessments(results)
        
        return {
            "developer_identifiers": {
                "github_username": github_username,
                "jira_email": jira_email
            },
            "combined_skill_assessment": combined_assessment,
            "individual_assessments": results,
            "analysis_date": combined_assessment.get("analysis_date"),
            "overall_summary": combined_assessment.get("summary", {}),
            "top_skills": combined_assessment.get("top_skills", []),
            "improvement_areas": combined_assessment.get("improvement_areas", []),
            "career_recommendations": combined_assessment.get("career_recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Error generating skill summary: {str(e)}")
        return {
            "error": f"Failed to generate skill summary: {str(e)}",
            "developer_identifiers": {
                "github_username": github_username,
                "jira_email": jira_email
            }
        }


@mcp.tool()
async def compare_developers(
    developer1_github: str,
    developer2_github: str,
    comparison_metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        # Analyze both developers
        dev1_analysis = await analyze_github_developer(developer1_github)
        dev2_analysis = await analyze_github_developer(developer2_github)
        
        # Process comparison
        skill_processor = SkillProcessor()
        comparison_result = skill_processor.compare_developers(
            dev1_analysis, dev2_analysis, comparison_metrics
        )
        
        return {
            "comparison_type": "github_skills",
            "developers": {
                "developer1": developer1_github,
                "developer2": developer2_github
            },
            "comparison_metrics": comparison_metrics,
            "comparison_result": comparison_result,
            "individual_assessments": {
                "developer1": dev1_analysis,
                "developer2": dev2_analysis
            },
            "summary": comparison_result.get("summary", {}),
            "skill_gaps": comparison_result.get("skill_gaps", {}),
            "strengths_comparison": comparison_result.get("strengths_comparison", {}),
            "recommendations": comparison_result.get("recommendations", [])
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


# Resources
@mcp.resource("file://developer-profiles")
async def get_developer_profiles() -> str:
    """Get available developer profiles and cached analyses."""
    # This would typically read from a database or cache
    return "Available developer profiles and cached skill analyses"


@mcp.resource("file://skill-categories")
async def get_skill_categories() -> str:
    """Get the categorization system used for skill analysis."""
    skill_processor = SkillProcessor()
    categories = skill_processor.get_skill_categories()
    
    return f"""
# Skill Categories

## Programming Languages
{', '.join(categories.get('programming_languages', []))}

## Frameworks & Tools  
{', '.join(categories.get('frameworks_tools', []))}

## Soft Skills
{', '.join(categories.get('soft_skills', []))}

## Domain Knowledge
{', '.join(categories.get('domain_knowledge', []))}

## Analysis Metrics
- Code complexity analysis
- Collaboration patterns
- Learning progression tracking
- Problem-solving assessment
"""


# Prompts
@mcp.prompt("skill-assessment-report")
async def skill_assessment_prompt(developer_name: str) -> str:
    """Generate a prompt for creating a comprehensive skill assessment report."""
    return f"""
# Skill Assessment Report for {developer_name}

## Instructions
Please analyze the provided developer data and create a comprehensive skill assessment report. Focus on:

1. **Technical Skills Analysis**
   - Programming languages and proficiency levels
   - Frameworks, tools, and technologies
   - Code quality and best practices

2. **Collaboration & Communication**
   - Code review participation
   - Issue discussion quality
   - Mentoring and knowledge sharing

3. **Problem-Solving & Growth**
   - Complexity of tasks handled
   - Learning progression over time
   - Innovation and creative solutions

4. **Recommendations**
   - Areas for skill development
   - Career growth opportunities
   - Training suggestions

## Format
Structure your response with clear sections, specific examples, and actionable insights.
"""


@mcp.prompt("developer-comparison")
async def developer_comparison_prompt(dev1: str, dev2: str) -> str:
    """Generate a prompt for comparing two developers."""
    return f"""
# Developer Skill Comparison: {dev1} vs {dev2}

## Analysis Framework
Compare the two developers across these dimensions:

1. **Technical Expertise**
   - Programming language mastery
   - Technology stack breadth and depth
   - Code quality and architecture skills

2. **Productivity & Impact**
   - Code contribution volume and quality
   - Problem-solving efficiency
   - Feature delivery consistency

3. **Collaboration & Leadership**
   - Code review quality and frequency
   - Knowledge sharing and mentoring
   - Team contribution patterns

4. **Growth & Adaptability**
   - Learning curve on new technologies
   - Adaptation to changing requirements
   - Innovation and experimentation

## Deliverables
- Strengths and weaknesses comparison
- Skill gap analysis
- Role suitability assessment
- Development recommendations for each developer
"""


@mcp.tool()
async def get_technical_stack() -> Dict[str, Any]:
    """
    Get the technical stack and technologies used across the organization.
    
    Returns comprehensive information about programming languages, frameworks,
    tools, and their usage levels within the company.
    """
    try:
        config = Config()
        
        # Real analysis aggregating from all developers
        if config.github_token:
            analyzer = GitHubAnalyzer(config.github_token)
            stack_data = await analyzer.get_organization_tech_stack()
            
            return {
                "data_source": "real_api",
                "stack": stack_data.get("technologies", {}),
                "summary": stack_data.get("summary", {}),
                "analysis_date": datetime.now().isoformat(),
                "total_repositories_analyzed": stack_data.get("repositories_count", 0)
            }
        else:
            return {
                "error": "GitHub token not configured",
                "data_source": "error",
                "message": "Technical stack analysis requires GitHub API access"
            }
            
    except Exception as e:
        logger.error(f"Error getting technical stack: {str(e)}")
        return {
            "error": f"Failed to get technical stack: {str(e)}",
            "data_source": "error"
        }


async def test_tools_directly():
    """Direct testing mode - test MCP tools without MCP framework."""
    print("🧪 DIRECT TOOL TESTING MODE")
    print("=" * 50)
    
    while True:
        print("\nAvailable tools:")
        print("1. get_all_employees - Discover collaborators")
        print("2. analyze_github_developer - Analyze a developer")
        print("3. get_technical_stack - Organization tech stack")
        print("4. get_skill_summary - Combined skill assessment")
        print("5. compare_developers - Compare two developers")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-5): ").strip()
        
        if choice == "0":
            print("Exiting direct test mode...")
            break
        
        elif choice == "1":
            print("\n--- Testing get_all_employees ---")
            source = input("Source (github/jira/all) [github]: ").strip() or "github"
            metadata = input("Include metadata? (y/n) [n]: ").strip().lower() == 'y'
            active = input("Filter active only? (y/n) [y]: ").strip().lower() != 'n'
            
            result = await get_all_employees(source=source, include_metadata=True, filter_active=active)
            print(f"\nResult: {result}")
        
        elif choice == "2":
            print("\n--- Testing analyze_github_developer ---")
            username = input("GitHub username: ").strip()
            if username:
                months = input("Time range months [12]: ").strip() or "12"
                try:
                    months = int(months)
                    result = await analyze_github_developer(username=username, time_range_months=months)
                    print(f"\nResult: {result}")
                except ValueError:
                    print("Invalid number of months")
            else:
                print("Username required")
        
        elif choice == "3":
            print("\n--- Testing get_technical_stack ---")
            result = await get_technical_stack()
            print(f"\nResult: {result}")
        
        elif choice == "4":
            print("\n--- Testing get_skill_summary ---")
            github_user = input("GitHub username (optional): ").strip() or None
            jira_email = input("Jira email (optional): ").strip() or None
            
            if github_user or jira_email:
                result = await get_skill_summary(github_username=github_user, jira_email=jira_email)
                print(f"\nResult: {result}")
            else:
                print("At least one identifier required")
        
        elif choice == "5":
            print("\n--- Testing compare_developers ---")
            dev1 = input("First developer GitHub username: ").strip()
            dev2 = input("Second developer GitHub username: ").strip()
            
            if dev1 and dev2:
                result = await compare_developers(developer1_github=dev1, developer2_github=dev2)
                print(f"\nResult: {result}")
            else:
                print("Both usernames required")
        
        else:
            print("Invalid choice")


def main() -> None:
    """Main entry point for the MCP server."""
    # Check if running in direct test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Starting in direct test mode...")
        asyncio.run(test_tools_directly())
        return
    
    logger.info("Starting Developer Skill Analyzer MCP Server...")
    
    # Load configuration
    config = Config()
    
    # Ensure GitHub token is loaded from environment if not in config
    if not config.github_token:
        env_token = os.environ.get('GITHUB_TOKEN')
        if env_token:
            config.github_token = env_token
            logger.info("Loaded GitHub token from environment variables")
        else:
            logger.error("No GitHub token found in environment variables")
    
    # Debug: Log configuration state
    logger.info(f"=== MCP SERVER STARTUP DEBUG ===")
    logger.info(f"GitHub token configured: {'Yes' if config.github_token else 'No'}")
    if config.github_token:
        logger.info(f"GitHub token starts with: {config.github_token[:10]}...")
    logger.info(f"GITHUB_TOKEN env var: {'Set' if os.getenv('GITHUB_TOKEN') else 'Not set'}")
    
    # Validate required environment variables
    if not config.github_token:
        logger.warning("GitHub token not configured - GitHub analysis will be limited")
    
    if not all([config.jira_server_url, config.jira_email, config.jira_api_token]):
        logger.warning("Jira configuration incomplete - Jira analysis will be disabled")
    
    # Start the MCP server
    mcp.run()


if __name__ == "__main__":
    main()