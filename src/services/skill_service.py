import logging
from typing import Any, Dict, List
from config import Config
from analyzers.skill_processor import SkillProcessor

logger = logging.getLogger(__name__)

class SkillService:
    """Service for skill processing and analysis operations."""
    
    def __init__(self):
        self.config = Config()
        self.processor = SkillProcessor()
    
    async def get_all_employees(self) -> List[Dict[str, Any]]:
        """
        Get a list of all employees/developers in the system.
        
        Returns:
            List of dictionaries containing employee information
        """
        try:
            logger.info("Retrieving all employees")
            
            # Real API analysis only - query from skill processor
            employees = await self.processor.get_all_employees()
            
            logger.info(f"Retrieved {len(employees)} employees")
            return employees
            
        except Exception as e:
            logger.error(f"Error retrieving employees: {str(e)}")
            raise
    
    async def combine_analysis_results(
        self,
        github_results: Dict[str, Any],
        jira_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine analysis results from multiple platforms.
        
        Args:
            github_results: Results from GitHub analysis
            jira_results: Results from Jira analysis
        
        Returns:
            Combined analysis results
        """
        try:
            logger.info("Combining analysis results from multiple platforms")
            
            combined_results = await self.processor.combine_results(
                github_results, jira_results
            )
            
            logger.info("Analysis results combined successfully")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error combining analysis results: {str(e)}")
            raise