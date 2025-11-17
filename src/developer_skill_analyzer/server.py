"""
MCP Server for Developer Skill Analysis

This server provides tools and resources for analyzing developer skills
based on their GitHub and Jira activity history.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .config import Config
from .models.developer import DeveloperProfile, SkillAssessment
from .analyzers.github_analyzer import GitHubAnalyzer
from .analyzers.jira_analyzer import JiraAnalyzer
from .analyzers.skill_processor import SkillProcessor
from .mock_data import (
    get_mock_github_data, 
    get_mock_jira_data, 
    MOCK_EMPLOYEES, 
    MOCK_TECHNICAL_STACK
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Developer Skill Analyzer")


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
        
        # Check if mock mode is enabled
        if config.mock_mode:
            logger.info(f"Using mock data for GitHub analysis: {username}")
            
            # Get mock GitHub data
            mock_data = get_mock_github_data(username)
            
            # Create a realistic analysis result using mock data
            analysis_result = {
                "developer": username,
                "analysis_type": "github_mock",
                "data_source": "mock",
                "time_range_months": time_range_months,
                "github_profile": {
                    "username": mock_data["username"],
                    "name": mock_data["name"],
                    "email": mock_data["email"]
                },
                "repositories_analyzed": len(mock_data["repositories"]),
                "languages": mock_data["languages"],
                "commit_stats": mock_data["commit_history"],
                "skill_assessment": {
                    "technical_skills": [],
                    "collaboration_metrics": {
                        "total_repositories": len(mock_data["repositories"]),
                        "contribution_frequency": "High",
                        "code_quality_indicators": "Good"
                    }
                },
                "summary": {
                    "primary_language": max(mock_data["languages"].items(), key=lambda x: x[1])[0],
                    "total_commits": mock_data["commit_history"]["total_commits"],
                    "activity_level": "Active" if mock_data["commit_history"]["commits_last_month"] > 20 else "Moderate"
                },
                "analysis_date": datetime.now().isoformat(),
                "recommendations": [
                    f"Strong in {max(mock_data['languages'].items(), key=lambda x: x[1])[0]}",
                    "Active contributor with consistent commit history",
                    "Consider expanding to additional languages"
                ]
            }
            
            # Add technical skills based on languages
            for lang, percentage in mock_data["languages"].items():
                if percentage > 0.1:  # Only include languages with >10% usage
                    confidence = min(95, int(percentage * 100 + 20))
                    level = "Expert" if percentage > 0.5 else "Advanced" if percentage > 0.3 else "Intermediate"
                    
                    analysis_result["skill_assessment"]["technical_skills"].append({
                        "skill": lang,
                        "level": level,
                        "confidence": confidence,
                        "evidence": f"{percentage:.0%} of code base",
                        "commits": int(mock_data["commit_history"]["total_commits"] * percentage)
                    })
            
            return analysis_result
        
        else:
            # Real API mode
            analyzer = GitHubAnalyzer(config.github_token)
            
            logger.info(f"Starting real GitHub analysis for user: {username}")
            
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
    Get a list of all employee names from GitHub and/or Jira.
    
    Args:
        source: Data source ("github", "jira", or "all")
        include_metadata: Include additional metadata about employees
        filter_active: Only include active employees
    
    Returns:
        Dictionary containing employee names and optional metadata
    """
    try:
        logger.info(f"Fetching all employees from source: {source}")
        
        employees = {
            "github_employees": [],
            "jira_employees": [],
            "total_count": 0,
            "source": source,
            "metadata": {}
        }
        
        # Mock employee data for demonstration
        # In a real implementation, this would query GitHub/Jira APIs
        mock_github_employees = [
            {
                "username": "alice_dev",
                "display_name": "Alice Johnson",
                "role": "Senior Full-Stack Developer",
                "team": "Frontend Team",
                "last_activity": "2025-11-15",
                "repositories": 24,
                "total_commits": 1456
            },
            {
                "username": "bob_backend",
                "display_name": "Bob Smith",
                "role": "Backend Developer",
                "team": "API Team",
                "last_activity": "2025-11-16",
                "repositories": 18,
                "total_commits": 892
            },
            {
                "username": "carol_lead",
                "display_name": "Carol Davis",
                "role": "Technical Lead",
                "team": "Architecture Team",
                "last_activity": "2025-11-17",
                "repositories": 35,
                "total_commits": 2341
            },
            {
                "username": "david_ml",
                "display_name": "David Chen",
                "role": "ML Engineer",
                "team": "Data Science Team",
                "last_activity": "2025-11-14",
                "repositories": 12,
                "total_commits": 567
            },
            {
                "username": "eve_devops",
                "display_name": "Eve Wilson",
                "role": "DevOps Engineer",
                "team": "Infrastructure Team",
                "last_activity": "2025-11-17",
                "repositories": 8,
                "total_commits": 423
            }
        ]
        
        mock_jira_employees = [
            {
                "email": "alice.johnson@company.com",
                "display_name": "Alice Johnson",
                "role": "Senior Developer",
                "team": "Frontend Team",
                "last_activity": "2025-11-16",
                "issues_resolved": 145,
                "avg_resolution_time": 2.3
            },
            {
                "email": "bob.smith@company.com",
                "display_name": "Bob Smith",
                "role": "Backend Developer",
                "team": "API Team",
                "last_activity": "2025-11-15",
                "issues_resolved": 98,
                "avg_resolution_time": 1.8
            },
            {
                "email": "carol.davis@company.com",
                "display_name": "Carol Davis",
                "role": "Technical Lead",
                "team": "Architecture Team",
                "last_activity": "2025-11-17",
                "issues_resolved": 67,
                "avg_resolution_time": 3.1
            }
        ]
        
        # Filter and process based on source
        if source in ["github", "all"]:
            github_list = []
            for emp in mock_github_employees:
                if include_metadata:
                    github_list.append(emp)
                else:
                    github_list.append({
                        "username": emp["username"],
                        "display_name": emp["display_name"],
                        "team": emp["team"]
                    })
            employees["github_employees"] = github_list
        
        if source in ["jira", "all"]:
            jira_list = []
            for emp in mock_jira_employees:
                if include_metadata:
                    jira_list.append(emp)
                else:
                    jira_list.append({
                        "email": emp["email"],
                        "display_name": emp["display_name"],
                        "team": emp["team"]
                    })
            employees["jira_employees"] = jira_list
        
        # Calculate totals
        total_github = len(employees["github_employees"])
        total_jira = len(employees["jira_employees"])
        employees["total_count"] = total_github + total_jira
        
        # Add metadata
        employees["metadata"] = {
            "github_total": total_github,
            "jira_total": total_jira,
            "teams": list(set([emp.get("team", "Unknown") for emp in mock_github_employees + mock_jira_employees])),
            "roles": list(set([emp.get("role", "Unknown") for emp in mock_github_employees + mock_jira_employees])),
            "query_timestamp": "2025-11-17T10:30:00Z",
            "include_metadata": include_metadata,
            "filter_active": filter_active
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
        
        if config.mock_mode:
            logger.info("Returning mock technical stack data")
            return {
                "data_source": "mock",
                "stack": MOCK_TECHNICAL_STACK,
                "summary": {
                    "total_technologies": sum(len(category) for category in MOCK_TECHNICAL_STACK.values()),
                    "categories": list(MOCK_TECHNICAL_STACK.keys()),
                    "most_used_language": "JavaScript",
                    "most_used_framework": "React",
                    "most_used_tool": "Git"
                },
                "analysis_date": datetime.now().isoformat()
            }
        else:
            # Real analysis would aggregate from all developers
            return {
                "data_source": "aggregated",
                "message": "Real technical stack analysis requires API credentials",
                "mock_available": True
            }
            
    except Exception as e:
        logger.error(f"Error getting technical stack: {str(e)}")
        return {
            "error": f"Failed to get technical stack: {str(e)}",
            "data_source": "error"
        }


def main() -> None:
    """Main entry point for the MCP server."""
    logger.info("Starting Developer Skill Analyzer MCP Server...")
    
    # Load configuration
    config = Config()
    
    # Validate required environment variables
    if not config.github_token:
        logger.warning("GitHub token not configured - GitHub analysis will be limited")
    
    if not all([config.jira_server_url, config.jira_email, config.jira_api_token]):
        logger.warning("Jira configuration incomplete - Jira analysis will be disabled")
    
    # Start the MCP server
    mcp.run()


if __name__ == "__main__":
    main()