"""
Automatic Update Worker
Runs every 5 minutes to analyze and update all users in the database.
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
from db.connection import DatabaseConnection
from services.github_service import GitHubService
from services.jira_service import JiraService
from analyzers.github_analyzer import GitHubAnalyzer
from analyzers.jira_analyzer import JiraAnalyzer
from analyzers.skill_processor import SkillProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoUpdateWorker:
    """Worker that automatically updates user analyses."""
    
    def __init__(self, update_interval_minutes: int = 5):
        """
        Initialize the worker.
        
        Args:
            update_interval_minutes: How often to check for updates (default 5 minutes)
        """
        self.update_interval_minutes = update_interval_minutes
        self.db_repo = DatabaseRepository()
        self.skill_processor = SkillProcessor(self.db_repo)
        
        # Initialize services
        try:
            self.github_service = GitHubService()
            self.github_analyzer = GitHubAnalyzer(self.github_service)
            logger.info("✓ GitHub service initialized")
        except Exception as e:
            logger.warning(f"GitHub service not available: {e}")
            self.github_service = None
            self.github_analyzer = None
        
        try:
            self.jira_service = JiraService()
            self.jira_analyzer = JiraAnalyzer(self.jira_service)
            logger.info("✓ Jira service initialized")
        except Exception as e:
            logger.warning(f"Jira service not available: {e}")
            self.jira_service = None
            self.jira_analyzer = None
    
    def get_users_needing_update(self) -> List[Dict[str, Any]]:
        """Get list of users that need updating."""
        try:
            query = "SELECT * FROM get_users_for_update(%s)"
            results = self.db_repo.db.execute_query(
                query, 
                (self.update_interval_minutes,)
            )
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting users for update: {e}")
            return []
    
    async def analyze_and_save_github(self, user_id: int, github_username: str) -> bool:
        """
        Analyze GitHub account and save to database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.github_analyzer:
            logger.warning(f"GitHub analyzer not available for {github_username}")
            return False
        
        try:
            logger.info(f"Analyzing GitHub: {github_username}")
            
            # Perform analysis
            analysis_result = await self.github_analyzer.analyze_developer(github_username)
            
            # Extract skill assessment
            skill_assessment = {
                "language_skills": analysis_result.get("language_skills", {}),
                "expertise_areas": analysis_result.get("expertise_areas", {})
            }
            
            # Combine and process skills
            combined = self.skill_processor.combine_assessments({
                "github": skill_assessment
            })
            
            # Update competences
            for skill_name, skill_data in combined.get("skills", {}).items():
                proficiency = skill_data.get("proficiency_percent", 0)
                self.db_repo.update_user_competence(
                    user_id=user_id,
                    competence_name=skill_name,
                    procent=proficiency
                )
            
            # Save full analysis
            version = self.db_repo.save_analysis(
                user_id=user_id,
                analysis_data=analysis_result
            )
            
            skills_count = len(combined.get("skills", {}))
            logger.info(f"✓ {github_username}: v{version}, {skills_count} skills saved")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error analyzing {github_username}: {e}")
            return False
    
    async def analyze_and_save_jira(self, user_id: int, jira_email: str) -> bool:
        """
        Analyze Jira account and save to database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.jira_analyzer:
            logger.warning(f"Jira analyzer not available for {jira_email}")
            return False
        
        try:
            logger.info(f"Analyzing Jira: {jira_email}")
            
            # Perform analysis
            analysis_result = await self.jira_analyzer.analyze_developer(jira_email)
            
            # Extract skill assessment
            skill_assessment = {
                "language_skills": analysis_result.get("language_skills", {}),
                "expertise_areas": analysis_result.get("expertise_areas", {})
            }
            
            # Combine and process skills
            combined = self.skill_processor.combine_assessments({
                "jira": skill_assessment
            })
            
            # Update competences
            for skill_name, skill_data in combined.get("skills", {}).items():
                proficiency = skill_data.get("proficiency_percent", 0)
                self.db_repo.update_user_competence(
                    user_id=user_id,
                    competence_name=skill_name,
                    procent=proficiency
                )
            
            # Save full analysis
            version = self.db_repo.save_analysis(
                user_id=user_id,
                analysis_data=analysis_result
            )
            
            skills_count = len(combined.get("skills", {}))
            logger.info(f"✓ {jira_email}: v{version}, {skills_count} skills saved")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error analyzing {jira_email}: {e}")
            return False
    
    async def process_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single user (analyze GitHub and/or Jira).
        
        Args:
            user: User dictionary with id, github_username, jira_email
            
        Returns:
            Result dictionary
        """
        user_id = user['user_id']
        github_username = user.get('github_username')
        jira_email = user.get('jira_email')
        
        results = {
            'user_id': user_id,
            'github_username': github_username,
            'jira_email': jira_email,
            'github_success': False,
            'jira_success': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Analyze GitHub if available
        if github_username:
            results['github_success'] = await self.analyze_and_save_github(
                user_id, github_username
            )
        
        # Analyze Jira if available
        if jira_email:
            results['jira_success'] = await self.analyze_and_save_jira(
                user_id, jira_email
            )
        
        return results
    
    async def run_update_cycle(self):
        """Run one complete update cycle."""
        logger.info("=" * 60)
        logger.info(f"Starting update cycle at {datetime.now()}")
        logger.info("=" * 60)
        
        # Get users needing update
        users = self.get_users_needing_update()
        
        if not users:
            logger.info("No users need updating at this time")
            return
        
        logger.info(f"Found {len(users)} user(s) needing update")
        
        # Process each user
        results = []
        for user in users:
            result = await self.process_user(user)
            results.append(result)
            # Small delay between users to avoid rate limiting
            await asyncio.sleep(2)
        
        # Summary
        github_success = sum(1 for r in results if r['github_success'])
        jira_success = sum(1 for r in results if r['jira_success'])
        
        logger.info("=" * 60)
        logger.info(f"Update cycle complete:")
        logger.info(f"  - Users processed: {len(results)}")
        logger.info(f"  - GitHub updates: {github_success}")
        logger.info(f"  - Jira updates: {jira_success}")
        logger.info("=" * 60)
    
    async def run(self):
        """Run the worker continuously."""
        logger.info("🚀 Auto-update worker started")
        logger.info(f"Update interval: {self.update_interval_minutes} minutes")
        logger.info(f"GitHub available: {self.github_analyzer is not None}")
        logger.info(f"Jira available: {self.jira_analyzer is not None}")
        
        while True:
            try:
                await self.run_update_cycle()
            except Exception as e:
                logger.error(f"Error in update cycle: {e}")
            
            # Wait for next cycle
            wait_seconds = self.update_interval_minutes * 60
            logger.info(f"Waiting {self.update_interval_minutes} minutes until next cycle...")
            await asyncio.sleep(wait_seconds)


async def main():
    """Main entry point."""
    # You can change the interval here (in minutes)
    worker = AutoUpdateWorker(update_interval_minutes=5)
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
