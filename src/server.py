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
async def get_developer_languages(
    username: str
) -> Dict[str, Any]:
    """
    Get all programming languages from a developer's profile organized by categories.
    Shows language distribution across categories and identifies top programming languages.
    
    Args:
        username: GitHub username to get language information for
    
    Returns:
        Dictionary containing:
        - Categorized languages (Programming Languages, Web Frontend, Backend/Server, etc.)
        - Top 3 programming languages by usage (lines of code)
        - Total number of languages and repositories
    """
    try:
        config = Config()
        github_service = GitHubService()
        analyzer = GitHubAnalyzer(github_service)
        
        logger.info(f"Getting language information for user: {username}")
        
        # Call analyzer to get languages by category
        result = await analyzer.get_languages_by_category(username)
        
        # Add timestamp
        result["analysis_date"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting languages for {username}: {str(e)}")
        return {
            "error": f"Failed to get language information: {str(e)}",
            "username": username
        }


@mcp.tool()
async def get_all_employees(
    source: str = "github",
    include_metadata: bool = False
) -> Dict[str, Any]:
    """
    Get all employees from database with fallback to GitHub discovery.
    
    Priority:
    1. Get active users from database
    2. If empty, check if token user is in an org -> get org members
    3. If not in org -> get collaborators from user's repositories
    
    Args:
        source: Data source ("github" or "all")
        include_metadata: Include additional metadata (commit counts, last activity)
    
    Returns:
        Dictionary containing employees with optional metadata
    """
    try:
        logger.info(f"Fetching all employees from source: {source}")
        
        from db.repository import DatabaseRepository
        db_repo = DatabaseRepository()
        
        # Try to get employees from database first
        db_users = db_repo.get_all_active_users()
        
        if db_users:
            logger.info(f"Found {len(db_users)} active users in database")
            return {
                "github_employees": db_users,
                "total_count": len(db_users),
                "source": "database"
            }
        
        # Fallback: Database is empty, discover from GitHub
        logger.info("Database is empty, discovering employees from GitHub")
        
        config = Config()
        employees = {
            "github_employees": [],
            "total_count": 0,
            "source": source
        }
        
        if source in ["github", "all"] and config.github_token:
            try:
                github_service = GitHubService()
                
                from github import Github, Auth
                auth = Auth.Token(config.github_token)
                g = Github(auth=auth)
                user = g.get_user()
                
                discovered = []
                orgs = list(user.get_orgs())
                
                if orgs:
                    # User is in organizations - get org members
                    logger.info(f"User belongs to {len(orgs)} organizations, fetching members")
                    for org in orgs:
                        members = github_service.get_organization_members(org.login)
                        discovered.extend(members)
                else:
                    # User not in org - get collaborators from repos
                    logger.info("User not in any organization, fetching collaborators from repositories")
                    repos = await github_service.get_user_repositories(user.login, limit=50)
                    collaborators_set = set()
                    
                    for repo in repos:
                        try:
                            repo_obj = g.get_repo(f"{user.login}/{repo['name']}")
                            for collab in repo_obj.get_collaborators():
                                collaborators_set.add(collab.login)
                        except Exception as e:
                            logger.warning(f"Could not get collaborators for {repo['name']}: {e}")
                            continue
                    
                    discovered = [{"username": username} for username in collaborators_set]
                
                # Deduplicate by username
                unique_employees = {emp['username']: emp for emp in discovered}.values()
                employees["github_employees"] = list(unique_employees)
                employees["total_count"] = len(unique_employees)
                
                logger.info(f"Discovered {len(unique_employees)} GitHub employees")
                
            except Exception as e:
                logger.error(f"Failed to discover GitHub employees: {e}")
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
        
        db_repo = DatabaseRepository()
        
        # Check if user exists and is active
        existing_user = db_repo.get_user_by_identifier(github_username, None, include_inactive=True)
        if existing_user and not existing_user.get('is_active', True):
            return {
                "status": "error",
                "error": f"Developer '{github_username}' is deactivated and cannot be analyzed",
                "message": "Use reactivate_developer tool first if you want to analyze this developer",
                "github_username": github_username,
                "timestamp": datetime.now().isoformat()
            }
        
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


@mcp.tool()
async def remove_developer(
    github_username: Optional[str] = None,
    jira_email: Optional[str] = None,
    performed_by: Optional[str] = None,
    admin_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove (deactivate) a developer who no longer works at the company.
    This is a soft delete - the user's data is retained but they won't appear in searches.
    
    🔒 ADMIN ONLY: This action requires admin password to write to audit log.
    
    Args:
        github_username: GitHub username of the developer to remove
        jira_email: Jira email of the developer to remove
        performed_by: GitHub username or email of the administrator performing this action
        admin_password: Admin database password (required for this operation)
        
    Returns:
        Confirmation of removal with developer details
    """
    try:
        from db.repository import DatabaseRepository
        
        # Check if admin password was provided
        if not admin_password:
            return {
                "status": "error",
                "error": "Admin password required to remove developer",
                "message": "Please provide admin_password parameter to perform this operation",
                "timestamp": datetime.now().isoformat()
            }
        
        # Use admin connection to write audit log
        db_repo = DatabaseRepository(admin_password=admin_password)
        result = db_repo.remove_developer(github_username, jira_email, performed_by)
        result["timestamp"] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"Error removing developer: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def reactivate_developer(
    github_username: Optional[str] = None,
    jira_email: Optional[str] = None,
    performed_by: Optional[str] = None,
    admin_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reactivate a previously removed developer.
    
    🔒 ADMIN ONLY: This action requires admin password to write to audit log.
    
    Args:
        github_username: GitHub username of the developer to reactivate
        jira_email: Jira email of the developer to reactivate
        performed_by: GitHub username or email of the administrator performing this action
        admin_password: Admin database password (required for this operation)
        
    Returns:
        Confirmation of reactivation
    """
    try:
        from db.repository import DatabaseRepository
        
        # Check if admin password was provided
        if not admin_password:
            return {
                "status": "error",
                "error": "Admin password required to reactivate developer",
                "message": "Please provide admin_password parameter to perform this operation",
                "timestamp": datetime.now().isoformat()
            }
        
        # Use admin connection to write audit log
        db_repo = DatabaseRepository(admin_password=admin_password)
        result = db_repo.reactivate_developer(github_username, jira_email, performed_by)
        result["timestamp"] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"Error reactivating developer: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_admin_audit_log(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 50,
    admin_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get audit log of administrative actions (deactivations, reactivations, deletions).
    
    🔒 ADMIN ONLY: This action requires admin password to view sensitive audit logs.
    
    Args:
        user_id: Optional filter by user ID
        action: Optional filter by action type ('deactivate', 'reactivate', 'delete_permanently')
        limit: Maximum number of entries to return (default 50)
        admin_password: Admin database password (required for this operation)
        
    Returns:
        List of audit log entries with timestamps and admin identifiers
    """
    try:
        from db.repository import DatabaseRepository
        
        # Check if admin password was provided
        if not admin_password:
            return {
                "status": "error",
                "error": "Admin password required to view audit log",
                "message": "Please provide admin_password parameter to perform this operation",
                "timestamp": datetime.now().isoformat()
            }
        
        # Use admin connection to read audit log
        db_repo = DatabaseRepository(admin_password=admin_password)
        result = db_repo.get_audit_log(user_id, action, limit)
        result["timestamp"] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def list_removed_developers() -> Dict[str, Any]:
    """
    List all developers who have been removed (deactivated).
    
    Returns:
        List of inactive developers with their details and deactivation dates
    """
    try:
        from db.repository import DatabaseRepository
        
        db_repo = DatabaseRepository()
        inactive_users = db_repo.get_inactive_users()
        
        return {
            "status": "success",
            "total_removed": len(inactive_users),
            "developers": [{
                "github_username": user.get('github_username'),
                "jira_email": user.get('jira_email'),
                "full_name": user.get('full_name'),
                "display_name": user.get('display_name'),
                "company": user.get('company'),
                "deactivated_at": user.get('deactivated_at').isoformat() if user.get('deactivated_at') else None,
                "created_at": user.get('created_at').isoformat() if user.get('created_at') else None
            } for user in inactive_users],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing removed developers: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def get_employees_by_skill(
    skill_name: str,
    min_level: Optional[str] = None,
    include_inactive: bool = False,
    use_github_fallback: bool = True,
    github_search_scope: str = "collaborators"
) -> Dict[str, Any]:
    """
    Find all employees/developers who have a specific skill or competence.
    
    Searches database first. If no results found, optionally falls back to analyzing 
    GitHub users directly.
    
    Args:
        skill_name: Name of the skill/competence to search for (e.g., "Python", "JavaScript", "React")
        min_level: Minimum proficiency level filter - one of: "Beginner", "Intermediate", "Advanced", "Expert"
        include_inactive: If True, also include deactivated/removed users in results
        use_github_fallback: If True, fetch and analyze GitHub users when database has no results
        github_search_scope: What to search on GitHub - "collaborators" (default), "organizations", or "followers"
        
    Returns:
        List of employees with the specified skill, including their proficiency details
    """
    try:
        from db.repository import DatabaseRepository
        
        logger.info(f"Searching for employees with skill: {skill_name} (min_level: {min_level})")
        
        db_repo = DatabaseRepository()
        users = db_repo.get_users_by_competence(
            competence_name=skill_name,
            min_level=min_level,
            include_inactive=include_inactive
        )
        
        # Database has results - return them
        if users:
            rank_summary = {}
            for user in users:
                rank = user['competence']['rank']
                rank_summary[rank] = rank_summary.get(rank, 0) + 1
            
            return {
                "status": "success",
                "data_source": "database",
                "skill_name": skill_name,
                "min_level": min_level,
                "include_inactive": include_inactive,
                "total_count": len(users),
                "rank_distribution": rank_summary,
                "employees": users,
                "timestamp": datetime.now().isoformat()
            }
        
        # No database results - try GitHub fallback if enabled
        if use_github_fallback:
            logger.info(f"No database results for {skill_name}, attempting GitHub fallback (scope: {github_search_scope})...")
            
            try:
                # Get GitHub users based on scope
                config = Config()
                if not config.github_token:
                    return {
                        "status": "success",
                        "data_source": "database",
                        "message": "No employees found in database and GitHub fallback unavailable (no token)",
                        "skill_name": skill_name,
                        "min_level": min_level,
                        "employees": [],
                        "total_count": 0,
                        "timestamp": datetime.now().isoformat()
                    }
                
                github_service = GitHubService()
                analyzer = GitHubAnalyzer(github_service)
                
                from github import Github, Auth
                auth = Auth.Token(config.github_token)
                g = Github(auth=auth)
                user = g.get_user()
                
                discovered = []
                
                # Get users based on search scope
                if github_search_scope == "organizations":
                    # Get org members
                    for org in user.get_orgs():
                        members = github_service.get_organization_members(org.login)
                        discovered.extend(members)
                
                elif github_search_scope == "followers":
                    # Get followers
                    for follower in user.get_followers():
                        discovered.append({
                            "username": follower.login,
                            "name": follower.name,
                            "company": follower.company
                        })
                
                else:  # collaborators (default)
                    # Get contributors from user's repositories (including the repo owner)
                    collaborators_set = set()
                    # Add the authenticated user
                    collaborators_set.add(user.login)
                    
                    for repo in user.get_repos(type='public'):
                        try:
                            # Get contributors for each repo
                            for contributor in repo.get_contributors():
                                collaborators_set.add(contributor.login)
                        except Exception as repo_error:
                            logger.debug(f"Could not get contributors for {repo.name}: {repo_error}")
                            continue
                    
                    # Convert set to list of user dicts
                    for collab_username in collaborators_set:
                        try:
                            collab_user = g.get_user(collab_username)
                            discovered.append({
                                "username": collab_user.login,
                                "name": collab_user.name,
                                "company": collab_user.company
                            })
                        except Exception as e:
                            logger.debug(f"Could not fetch user {collab_username}: {e}")
                            continue
                
                # Deduplicate by username
                unique_members = {emp['username']: emp for emp in discovered}.values()
                
                logger.info(f"Found {len(unique_members)} GitHub users (scope: {github_search_scope}), analyzing for {skill_name}...")
                
                # Analyze each member for the requested skill
                matching_employees = []
                for member in unique_members:
                    try:
                        username = member['username']
                        analysis = await analyzer.analyze_developer(username)
                        
                        # Check if they have the skill
                        language_skills = analysis.get('language_skills', {})
                        
                        # Check if skill_name matches any language (case-insensitive)
                        for lang_name, lang_data in language_skills.items():
                            if lang_name.lower() == skill_name.lower():
                                level = lang_data.get('level', 'Beginner')
                                
                                # Apply min_level filter if specified
                                if min_level:
                                    level_order = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
                                    if level_order.get(level, 0) < level_order.get(min_level, 0):
                                        continue
                                
                                matching_employees.append({
                                    'user_id': None,
                                    'github_username': username,
                                    'full_name': member.get('name'),
                                    'display_name': username,
                                    'company': member.get('company'),
                                    'location': None,
                                    'role': None,
                                    'competence': {
                                        'name': lang_name,
                                        'category': 'programming_languages',
                                        'proficiency_percent': None,
                                        'rank': level,
                                        'total_lines': lang_data.get('total_lines'),
                                        'repositories': lang_data.get('repositories'),
                                        'usage_frequency': None,
                                        'last_updated': None
                                    }
                                })
                                break
                    
                    except Exception as member_error:
                        logger.warning(f"Failed to analyze member {member.get('username')}: {member_error}")
                        continue
                
                # Group by rank for summary
                rank_summary = {}
                for emp in matching_employees:
                    rank = emp['competence']['rank']
                    rank_summary[rank] = rank_summary.get(rank, 0) + 1
                
                return {
                    "status": "success",
                    "data_source": f"github_fallback_{github_search_scope}",
                    "message": f"No database results found. Analyzed {len(unique_members)} GitHub users from {github_search_scope}.",
                    "skill_name": skill_name,
                    "min_level": min_level,
                    "total_count": len(matching_employees),
                    "rank_distribution": rank_summary,
                    "employees": matching_employees,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as fallback_error:
                logger.error(f"GitHub fallback failed: {fallback_error}")
                return {
                    "status": "success",
                    "data_source": "database",
                    "message": f"No employees found in database. GitHub fallback failed: {str(fallback_error)}",
                    "skill_name": skill_name,
                    "min_level": min_level,
                    "employees": [],
                    "total_count": 0,
                    "timestamp": datetime.now().isoformat()
                }
        
        # No results and fallback disabled
        return {
            "status": "success",
            "data_source": "database",
            "message": f"No employees found with skill: {skill_name}" + 
                      (f" at {min_level} level or above" if min_level else ""),
            "skill_name": skill_name,
            "min_level": min_level,
            "employees": [],
            "total_count": 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting employees by skill: {e}")
        return {
            "status": "error",
            "error": str(e),
            "skill_name": skill_name,
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
async def permanently_delete_developer(
    github_username: Optional[str] = None,
    jira_email: Optional[str] = None,
    confirm: bool = False,
    admin_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    PERMANENTLY DELETE a developer and ALL their data (GDPR "right to be forgotten").
    This is irreversible! All analyses, competences, and history will be removed.
    
    🔒 ADMIN ONLY: This operation requires admin database password.
    
    WARNING: This is a hard delete. Data cannot be recovered!
    
    Args:
        github_username: GitHub username of the developer to delete
        jira_email: Jira email of the developer to delete
        confirm: Must be True to proceed (safety check)
        admin_password: Admin database password (required for this operation)
        
    Returns:
        Confirmation of permanent deletion
    """
    try:
        from db.repository import DatabaseRepository
        
        # Check if admin password was provided
        if not admin_password:
            return {
                "status": "error",
                "error": "Admin password required for permanent deletion",
                "message": "Please provide admin_password parameter to perform this operation",
                "timestamp": datetime.now().isoformat()
            }
        
        # Use admin connection for this operation
        db_repo = DatabaseRepository(admin_password=admin_password)
        result = db_repo.delete_user_permanently(github_username, jira_email, confirm)
        result["timestamp"] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"Error permanently deleting developer: {e}")
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