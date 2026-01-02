"""
One-time Auto Update Script
Runs once, updates all users, then exits.
Perfect for scheduling with pgAgent or Windows Task Scheduler.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from db.repository import DatabaseRepository
from services.github_service import GitHubService
from services.jira_service import JiraService
from analyzers.github_analyzer import GitHubAnalyzer
from analyzers.jira_analyzer import JiraAnalyzer
from analyzers.skill_processor import SkillProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduled_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def analyze_and_save_github(db_repo, skill_processor, github_analyzer, user_id: int, github_username: str) -> bool:
    """Analyze GitHub and save to database."""
    try:
        logger.info(f"Analyzing GitHub: {github_username}")
        
        analysis_result = await github_analyzer.analyze_developer(github_username)
        
        skill_assessment = {
            "language_skills": analysis_result.get("language_skills", {}),
            "expertise_areas": analysis_result.get("expertise_areas", {})
        }
        
        combined = skill_processor.combine_assessments({"github": skill_assessment})
        
        for skill_name, skill_data in combined.get("skills", {}).items():
            proficiency = skill_data.get("proficiency_percent", 0)
            db_repo.update_user_competence(
                user_id=user_id,
                competence_name=skill_name,
                procent=proficiency
            )
        
        version = db_repo.save_analysis(user_id=user_id, analysis_data=analysis_result)
        skills_count = len(combined.get("skills", {}))
        logger.info(f"✓ {github_username}: v{version}, {skills_count} skills")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error analyzing {github_username}: {e}")
        return False


async def analyze_and_save_jira(db_repo, skill_processor, jira_analyzer, user_id: int, jira_email: str) -> bool:
    """Analyze Jira and save to database."""
    try:
        logger.info(f"Analyzing Jira: {jira_email}")
        
        analysis_result = await jira_analyzer.analyze_developer(jira_email)
        
        skill_assessment = {
            "language_skills": analysis_result.get("language_skills", {}),
            "expertise_areas": analysis_result.get("expertise_areas", {})
        }
        
        combined = skill_processor.combine_assessments({"jira": skill_assessment})
        
        for skill_name, skill_data in combined.get("skills", {}).items():
            proficiency = skill_data.get("proficiency_percent", 0)
            db_repo.update_user_competence(
                user_id=user_id,
                competence_name=skill_name,
                procent=proficiency
            )
        
        version = db_repo.save_analysis(user_id=user_id, analysis_data=analysis_result)
        skills_count = len(combined.get("skills", {}))
        logger.info(f"✓ {jira_email}: v{version}, {skills_count} skills")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error analyzing {jira_email}: {e}")
        return False


async def main():
    """Main execution - run once and exit."""
    logger.info("="*60)
    logger.info(f"Scheduled update started: {datetime.now()}")
    logger.info("="*60)
    
    # Initialize
    db_repo = DatabaseRepository()
    skill_processor = SkillProcessor(db_repo)
    
    # Initialize services
    github_analyzer = None
    jira_analyzer = None
    
    try:
        github_service = GitHubService()
        github_analyzer = GitHubAnalyzer(github_service)
        logger.info("✓ GitHub service ready")
    except Exception as e:
        logger.warning(f"GitHub not available: {e}")
    
    try:
        jira_service = JiraService()
        jira_analyzer = JiraAnalyzer(jira_service)
        logger.info("✓ Jira service ready")
    except Exception as e:
        logger.warning(f"Jira not available: {e}")
    
    # Get users needing update
    try:
        query = "SELECT * FROM get_users_for_update(5)"
        users = db_repo.db.execute_query(query, (5,))
        users = [dict(row) for row in users]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return
    
    if not users:
        logger.info("No users need updating")
        return
    
    logger.info(f"Found {len(users)} user(s) to update")
    
    # Process each user
    github_success = 0
    jira_success = 0
    
    for user in users:
        user_id = user['user_id']
        github_username = user.get('github_username')
        jira_email = user.get('jira_email')
        
        if github_username and github_analyzer:
            if await analyze_and_save_github(db_repo, skill_processor, github_analyzer, user_id, github_username):
                github_success += 1
        
        if jira_email and jira_analyzer:
            if await analyze_and_save_jira(db_repo, skill_processor, jira_analyzer, user_id, jira_email):
                jira_success += 1
        
        await asyncio.sleep(2)  # Rate limiting
    
    # Summary
    logger.info("="*60)
    logger.info(f"Update complete:")
    logger.info(f"  Users processed: {len(users)}")
    logger.info(f"  GitHub updates: {github_success}")
    logger.info(f"  Jira updates: {jira_success}")
    logger.info(f"Finished: {datetime.now()}")
    logger.info("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
        sys.exit(0)  # Success
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)  # Failure
