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
        
        result = {
            "developer": username,
            "analysis_type": "github",
            "data_source": "real_api",
            "time_range_months": time_range_months,
            "username": analysis_result.get("username"),
            "profile": analysis_result.get("profile", {}),
            "language_skills": analysis_result.get("language_skills", {}),
            "expertise_areas": analysis_result.get("expertise_areas", {}),
            "total_repositories": analysis_result.get("total_repositories", 0),
            "analysis_date": datetime.now().isoformat(),
            "_save_prompt": f"\n\n💾 Would you like to save this analysis to the database?\n\nUse: save_analysis_to_database(github_username='{username}')\n\nThis will store the analysis for version tracking and historical comparison."
        }
        
        # Log the prompt for the AI to see
        logger.info(f"Analysis complete for {username}. Prompting to save to database.")
        
        return result
        
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
            "analysis_date": datetime.now().isoformat(),
            "_save_prompt": f"\n\n💾 Would you like to save this profile to the database?\n\nUse: save_analysis_to_database(github_username='{github_username}')\n\nNote: This only saves basic profile. For full analysis, use analyze_github_developer first."
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
            },
            "_save_prompt": f"\n\n💾 Would you like to save both developer analyses to the database?\n\nDeveloper 1: save_analysis_to_database(github_username='{developer1_github}')\nDeveloper 2: save_analysis_to_database(github_username='{developer2_github}')\n\nSaving allows for historical tracking and future comparisons."
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


@mcp.tool()
async def export_developer_profile(
    username: str,
    output_path: Optional[str] = None,
    format: str = "json"
) -> Dict[str, Any]:
    """
    Export developer competence profile to a file for external analysis.
    
    This tool exports sanitized developer data (without sensitive personal information)
    to a JSON file that can be used for further analysis in external tools.
    
    Args:
        username: GitHub username to export profile for
        output_path: File path for export (default: ./exports/{username}_profile.json)
        format: Export format - currently only 'json' is supported
        
    Returns:
        Export status including file path and record count
    """
    import json
    import os
    from pathlib import Path
    
    try:
        # Analyze the developer first
        config = Config()
        github_service = GitHubService()
        analyzer = GitHubAnalyzer(github_service)
        
        logger.info(f"Exporting profile for user: {username}")
        
        # Get analysis (already sanitized by services)
        analysis_result = await analyzer.analyze_developer(username)
        
        # Prepare export data with metadata
        export_data = {
            "export_metadata": {
                "username": username,
                "export_date": datetime.now().isoformat(),
                "format": format,
                "data_sanitized": True,
                "contains_pii": False
            },
            "developer_profile": {
                "username": analysis_result.get("username"),
                "profile": analysis_result.get("profile", {}),
                "language_skills": analysis_result.get("language_skills", {}),
                "expertise_areas": analysis_result.get("expertise_areas", {}),
                "total_repositories": analysis_result.get("total_repositories", 0),
                "analysis_date": datetime.now().isoformat()
            }
        }
        
        # Determine output path
        if not output_path:
            exports_dir = Path("./exports")
            exports_dir.mkdir(exist_ok=True)
            output_path = str(exports_dir / f"{username}_profile.json")
        else:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(output_path)
        
        logger.info(f"Successfully exported profile to: {output_path}")
        
        return {
            "success": True,
            "file_path": str(Path(output_path).absolute()),
            "records_exported": 1,
            "file_size_bytes": file_size,
            "format": format,
            "timestamp": datetime.now().isoformat(),
            "data_sanitized": True
        }
        
    except Exception as e:
        logger.error(f"Error exporting profile for {username}: {str(e)}")
        return {
            "success": False,
            "file_path": output_path or "N/A",
            "records_exported": 0,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_all_employees(
    source: str = "github",
    include_metadata: bool = False
) -> Dict[str, Any]:
    """
    Discover all collaborators and team members from GitHub repositories.
    
    Args:
        source: Data source ("github" or "all")
        include_metadata: Include additional metadata (commit counts, last activity)
    
    Returns:
        Dictionary containing discovered collaborators with optional metadata
    """
    try:
        logger.info(f"Fetching all employees from source: {source}")
        
        config = Config()
        employees = {
            "github_employees": [],
            "total_count": 0,
            "source": source
        }
        
        if source in ["github", "all"] and config.github_token:
            try:
                github_service = GitHubService()
                analyzer = GitHubAnalyzer(github_service)
                
                # Get authenticated user's organizations
                from github import Github, Auth
                auth = Auth.Token(config.github_token)
                g = Github(auth=auth)
                user = g.get_user()
                
                discovered = []
                for org in user.get_orgs():
                    members = github_service.get_organization_members(org.login)
                    discovered.extend(members)
                
                # Deduplicate by username
                unique_employees = {emp['username']: emp for emp in discovered}.values()
                employees["github_employees"] = list(unique_employees)
                employees["total_count"] = len(unique_employees)
                
                logger.info(f"Discovered {len(unique_employees)} GitHub collaborators")
                
            except Exception as e:
                logger.error(f"Failed to discover GitHub collaborators: {e}")
                employees["github_employees"] = []
                employees["error"] = str(e)
        
        return employees
        
    except Exception as e:
        logger.error(f"Error in get_all_employees: {str(e)}")
        return {
            "error": f"Failed to get employees: {str(e)}",
            "source": source
        }


@mcp.tool()
async def add_competence_to_database(
    name: str,
    category: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Add a new competence/skill to the database.
    
    Args:
        name: Name of the competence (e.g., "React", "Python", "Leadership")
        category: Category (programming_languages, frameworks_tools, databases, soft_skills, domain_knowledge)
        description: Optional description of the competence
        
    Returns:
        Confirmation with competence ID
    """
    try:
        from db.repository import DatabaseRepository
        
        db_repo = DatabaseRepository()
        competence_id = db_repo.add_competence(name, category, description)
        
        return {
            "status": "success",
            "competence_id": competence_id,
            "name": name,
            "category": category,
            "message": f"Successfully added competence '{name}' to category '{category}'",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error adding competence: {e}")
        return {
            "status": "error",
            "error": str(e),
            "name": name,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_all_competences() -> Dict[str, Any]:
    """
    Retrieve all competences from the database.
    
    Returns the complete list of skills/competences organized by category.
    
    Returns:
        All competences with their categories and descriptions
    """
    try:
        from db.repository import DatabaseRepository
        
        db_repo = DatabaseRepository()
        competences = db_repo.get_all_competences()
        
        # Organize by category
        by_category = {}
        for comp in competences:
            category = comp['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append({
                'id': comp['id'],
                'name': comp['name'],
                'description': comp['description']
            })
        
        return {
            "status": "success",
            "total_competences": len(competences),
            "categories": len(by_category),
            "competences_by_category": by_category,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting competences: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_user_competence_overview(
    github_username: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a user's competence overview from the database.
    
    Args:
        github_username: GitHub username to lookup
        
    Returns:
        User's competence overview with ranks and percentages
    """
    try:
        from db.repository import DatabaseRepository
        
        db_repo = DatabaseRepository()
        
        # Get user ID
        user = db_repo.get_user_by_identifier(github_username, None)
        if not user:
            return {
                "status": "not_found",
                "message": "User not found in database",
                "github_username": github_username,
                "timestamp": datetime.now().isoformat()
            }
        
        user_id = user['id']
        overview = db_repo.get_user_competence_overview(user_id)
        
        return {
            "status": "success",
            "user_info": {
                "id": user['id'],
                "github_username": user['github_username'],
                "full_name": user.get('full_name'),
                "display_name": user.get('display_name')
            },
            "total_competences": len(overview),
            "competences": overview,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user competence overview: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def save_analysis_to_database(
    github_username: str,
    full_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a developer and save results to the database (normalized with versioning).
    
    Args:
        github_username: GitHub username for analysis
        full_name: Developer's full name (optional)
        
    Returns:
        Analysis results and database save confirmation
    """
    try:
        from db.repository import DatabaseRepository
        from analyzers.skill_processor import SkillProcessor
        
        # Perform GitHub analysis
        github_service = GitHubService()
        analyzer = GitHubAnalyzer(github_service)
        analysis_result = await analyzer.analyze_developer(github_username)
        
        # Initialize database and skill processor
        db_repo = DatabaseRepository()
        skill_processor = SkillProcessor(db_repo)
        
        # Create or get user
        user_id = db_repo.get_or_create_user(
            github_username=github_username,
            full_name=full_name or github_username
        )
        
        # Save metadata FIRST to get version number
        metadata = {
            "profile": analysis_result.get("profile", {}),
            "raw_language_data": analysis_result.get("language_skills", {}),
            "expertise_areas": analysis_result.get("expertise_areas", {}),
            "github_username": github_username
        }
        
        analysis_version = db_repo.save_analysis(
            user_id=user_id,
            metadata=metadata,
            total_repositories=analysis_result.get("total_repositories", 0),
            data_source="github"
        )
        
        # Process skills from analysis
        skill_assessment = skill_processor.process_github_data(analysis_result)
        
        # Extract and save ALL skills (technical, soft, domain) to BOTH current AND history
        skills_saved = 0
        skills_failed = []
        
        # Get all skill types
        all_skills = []
        all_skills.extend(skill_assessment.get("technical_skills", []))
        all_skills.extend(skill_assessment.get("soft_skills", []))
        all_skills.extend(skill_assessment.get("domain_skills", []))
        
        for skill in all_skills:
            try:
                # Get skill details
                competence_name = skill.get("name")
                if not competence_name:
                    continue
                
                # Determine category from skill data
                skill_category = skill.get("category", "programming_languages")
                
                # Ensure the competence exists in the database
                db_repo.add_competence(
                    name=competence_name,
                    category=skill_category,
                    description=f"{competence_name} skill from {skill_category}"
                )
                
                # Calculate percentage from skill level and confidence
                confidence = skill.get("confidence_score", 0.5)
                usage_freq = skill.get("usage_frequency", 0)
                
                # Get skill level - handle both string and enum formats
                level = skill.get("level", "intermediate")
                if hasattr(level, 'name'):  # It's an enum
                    level_str = level.name.lower()
                elif hasattr(level, 'value'):  # Pydantic model
                    level_str = level.value.lower()
                else:  # It's already a string
                    level_str = str(level).lower().replace("skilllevel.", "")
                
                # Convert skill level to percentage (0-100)
                level_map = {
                    "beginner": 20,
                    "intermediate": 50,
                    "advanced": 75,
                    "expert": 95
                }
                base_percent = level_map.get(level_str, 50)
                
                # Adjust based on confidence (±20%)
                adjusted_percent = min(max(base_percent + (confidence - 0.5) * 40, 0), 100)
                
                # Update user competence (BOTH current AND history with version)
                db_repo.update_user_competence(
                    user_id=user_id,
                    competence_name=competence_name,
                    procent=round(adjusted_percent, 2),
                    usage_frequency=usage_freq,
                    analysis_version=analysis_version  # NEW: Also save to history
                )
                
                skills_saved += 1
                logger.info(f"✓ Saved: {competence_name} ({skill_category}) = {adjusted_percent:.1f}% [usage: {usage_freq}] (v{analysis_version})")
                
            except Exception as skill_error:
                error_msg = f"{skill.get('name', 'Unknown')}: {str(skill_error)}"
                skills_failed.append(error_msg)
                logger.warning(f"✗ Failed to save skill: {error_msg}")
                continue
        
        result = {
            "status": "success",
            "user_id": user_id,
            "analysis_version": analysis_version,
            "skills_saved": skills_saved,
            "total_skills_found": len(all_skills),
            "github_username": github_username,
            "message": f"✓ Analysis saved: {skills_saved}/{len(all_skills)} skills stored (current + history v{analysis_version})",
            "timestamp": datetime.now().isoformat(),
            "architecture": "normalized_with_versioning"
        }
        
        if skills_failed:
            result["skills_failed"] = skills_failed
            result["warning"] = f"{len(skills_failed)} skills could not be saved"
        
        return result
        
    except Exception as e:
        logger.error(f"Error saving analysis to database: {e}")
        return {
            "status": "error",
            "error": str(e),
            "github_username": github_username,
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_previous_analysis(
    github_username: str
) -> Dict[str, Any]:
    """
    Retrieve previous analysis versions from the database (normalized structure).
    Returns metadata + competence history for each version.
    
    Args:
        github_username: GitHub username
        
    Returns:
        All stored analysis versions with competences for the user
    """
    try:
        from db.repository import DatabaseRepository
        
        db_repo = DatabaseRepository()
        
        # Get user
        user = db_repo.get_user_by_identifier(github_username, None)
        if not user:
            return {
                "status": "not_found",
                "message": "No previous analyses found for this user",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get all analysis metadata
        analyses_metadata = db_repo.get_all_analyses(user['id'])
        
        # For each version, get the competences
        analyses_with_competences = []
        for analysis in analyses_metadata:
            version = analysis['version_number']
            competences = db_repo.get_competences_for_version(user['id'], version)
            
            analyses_with_competences.append({
                "version": version,
                "analysis_date": analysis['analysis_date'],
                "total_repositories": analysis['total_repositories'],
                "data_source": analysis['data_source'],
                "metadata": analysis['metadata'],
                "competences": competences,
                "total_competences": len(competences)
            })
        
        return {
            "status": "success",
            "user_info": {
                "id": user['id'],
                "github_username": user['github_username']
            },
            "total_versions": len(analyses_with_competences),
            "analyses": analyses_with_competences,
            "message": f"Found {len(analyses_with_competences)} analysis version(s)",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving previous analysis: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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