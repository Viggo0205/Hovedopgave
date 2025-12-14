"""
Database repository for managing developer skills data.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .connection import DatabaseConnection

logger = logging.getLogger(__name__)


def _serialize_datetime(obj: Any) -> Any:
    """
    Recursively convert datetime objects to ISO format strings.
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serialized object with datetime converted to strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _serialize_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_datetime(item) for item in obj]
    else:
        return obj


class DatabaseRepository:
    """Repository for database operations."""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        Initialize the repository.
        
        Args:
            db_connection: Database connection instance
        """
        self.db = db_connection or DatabaseConnection()
    
    def get_competence_categories(self) -> Dict[str, List[str]]:
        """
        Get all competence categories from the database.
        
        Returns:
            Dictionary mapping category names to lists of competences
        """
        try:
            query = "SELECT category, competences FROM competence_categories"
            results = self.db.execute_query(query)
            
            categories = {}
            for row in results:
                categories[row['category']] = row['competences']
            
            logger.info(f"Loaded {len(categories)} competence categories from database")
            return categories
            
        except Exception as e:
            logger.error(f"Error loading competence categories: {e}")
            # Return empty dict if database not available
            return {}
    
    def add_competence(self, name: str, category: str, description: Optional[str] = None) -> int:
        """
        Add a new competence to the database.
        
        Args:
            name: Competence name
            category: Category name
            description: Optional description
            
        Returns:
            Competence ID
        """
        try:
            query = "SELECT add_competence(%s, %s, %s)"
            result = self.db.execute_query(query, (name, category, description))
            competence_id = result[0]['add_competence']
            
            logger.info(f"Added competence: {name} (category: {category}, id: {competence_id})")
            return competence_id
            
        except Exception as e:
            logger.error(f"Error adding competence: {e}")
            raise
    
    def get_or_create_user(
        self,
        github_username: Optional[str] = None,
        jira_email: Optional[str] = None,
        full_name: Optional[str] = None,
        display_name: Optional[str] = None,
        company: Optional[str] = None,
        location: Optional[str] = None
    ) -> int:
        """
        Get existing user or create new one.
        
        Args:
            github_username: GitHub username
            jira_email: Jira email
            full_name: Full name
            display_name: Display name
            company: Company name
            location: Location
            
        Returns:
            User ID
        """
        try:
            query = "SELECT get_or_create_user(%s, %s, %s, %s, %s, %s)"
            result = self.db.execute_query(
                query,
                (github_username, jira_email, full_name, display_name, company, location)
            )
            user_id = result[0]['get_or_create_user']
            
            logger.info(f"User ID: {user_id} (GitHub: {github_username}, Jira: {jira_email})")
            return user_id
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            raise
    
    def update_user_competence(
        self,
        user_id: int,
        competence_name: str,
        procent: float,
        usage_frequency: int = 0
    ) -> None:
        """
        Update user's competence level.
        
        Args:
            user_id: User ID
            competence_name: Name of the competence
            procent: Competence percentage (0-100)
            usage_frequency: Usage frequency count
        """
        try:
            # Get competence ID
            query = "SELECT id FROM competence WHERE name = %s"
            result = self.db.execute_query(query, (competence_name,))
            
            if not result:
                logger.warning(f"Competence not found: {competence_name}")
                return
            
            competence_id = result[0]['id']
            
            # Update user competence
            query = "SELECT update_user_competence(%s, %s, %s, %s)"
            self.db.execute_query(query, (user_id, competence_id, procent, usage_frequency), fetch=False)
            
            logger.debug(f"Updated competence for user {user_id}: {competence_name} = {procent}%")
            
        except Exception as e:
            logger.error(f"Error updating user competence: {e}")
            raise
    
    def save_analysis(self, user_id: int, analysis_data: Dict[str, Any]) -> int:
        """
        Save analysis data with version management (keeps max 2 versions).
        
        Args:
            user_id: User ID
            analysis_data: Analysis data to save
            
        Returns:
            Version number of saved analysis
        """
        try:
            # Serialize datetime objects to ISO format strings
            serialized_data = _serialize_datetime(analysis_data)
            
            query = "SELECT save_analysis(%s, %s)"
            result = self.db.execute_query(
                query,
                (user_id, json.dumps(serialized_data))
            )
            version = result[0]['save_analysis']
            
            logger.info(f"Saved analysis for user {user_id} as version {version}")
            return version
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
    
    def get_latest_analysis(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the latest analysis for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Analysis data or None if not found
        """
        try:
            query = "SELECT * FROM get_latest_analysis(%s)"
            results = self.db.execute_query(query, (user_id,))
            
            if not results:
                return None
            
            result = results[0]
            return {
                'id': result['id'],
                'analysis_data': result['analysis_data'],
                'analysis_date': result['analysis_date'].isoformat() if result['analysis_date'] else None,
                'version_number': result['version_number']
            }
            
        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None
    
    def get_all_analyses(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all analyses for a user (max 2).
        
        Args:
            user_id: User ID
            
        Returns:
            List of analyses
        """
        try:
            query = """
                SELECT id, analysis_data, analysis_date, version_number
                FROM analysis_archive
                WHERE user_id = %s
                ORDER BY version_number DESC
            """
            results = self.db.execute_query(query, (user_id,))
            
            analyses = []
            for row in results:
                analyses.append({
                    'id': row['id'],
                    'analysis_data': row['analysis_data'],
                    'analysis_date': row['analysis_date'].isoformat() if row['analysis_date'] else None,
                    'version_number': row['version_number']
                })
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error getting all analyses: {e}")
            return []
    
    def get_user_competence_overview(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get user competence overview.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of user competences with details
        """
        try:
            if user_id:
                query = "SELECT * FROM user_competence_overview WHERE user_id = %s"
                results = self.db.execute_query(query, (user_id,))
            else:
                query = "SELECT * FROM user_competence_overview"
                results = self.db.execute_query(query)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting user competence overview: {e}")
            return []
    
    def get_all_competences(self) -> List[Dict[str, Any]]:
        """
        Get all competences from the database.
        
        Returns:
            List of all competences
        """
        try:
            query = "SELECT id, name, category, description FROM competence ORDER BY category, name"
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting all competences: {e}")
            return []
    
    def get_user_by_identifier(
        self,
        github_username: Optional[str] = None,
        jira_email: Optional[str] = None,
        include_inactive: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get user by GitHub username or Jira email.
        
        Args:
            github_username: GitHub username
            jira_email: Jira email
            include_inactive: If True, include deactivated users in search
            
        Returns:
            User data or None if not found
        """
        try:
            # Build query dynamically based on what's provided
            conditions = []
            params = []
            
            
            if github_username is not None:
                conditions.append("github_username = %s")
                params.append(github_username)
            
            if jira_email is not None:
                conditions.append("jira_email = %s")
                params.append(jira_email)
            
            if not conditions:
                return None
            
            # Add active filter unless explicitly including inactive users
            if not include_inactive:
                conditions.append("is_active = TRUE")
            
            query = f"SELECT * FROM users WHERE {' AND '.join(conditions)} LIMIT 1"
            results = self.db.execute_query(query, tuple(params))
            
            if results:
                return dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by identifier: {e}")
            return None
    
    def deactivate_user(
        self,
        github_username: Optional[str] = None,
        jira_email: Optional[str] = None
    ) -> bool:
        """
        Deactivate a user (soft delete).
        
        Args:
            github_username: GitHub username
            jira_email: Jira email address
            
        Returns:
            True if user was deactivated, False otherwise
        """
        try:
            conditions = []
            params = []
            
            if github_username is not None:
                conditions.append("github_username = %s")
                params.append(github_username)
            
            if jira_email is not None:
                conditions.append("jira_email = %s")
                params.append(jira_email)
            
            if not conditions:
                return False
            
            query = f"""
                UPDATE users 
                SET is_active = FALSE, 
                    deactivated_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE {' OR '.join(conditions)}
                AND is_active = TRUE
                RETURNING id, github_username, full_name
            """
            results = self.db.execute_query(query, tuple(params))
            
            if results:
                user = results[0]
                logger.info(f"Deactivated user: {user['github_username']} (ID: {user['id']})")
                return True
            
            logger.warning(f"No active user found to deactivate with given identifiers")
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            raise
    
    def reactivate_user(
        self,
        github_username: Optional[str] = None,
        jira_email: Optional[str] = None
    ) -> bool:
        """
        Reactivate a previously deactivated user.
        
        Args:
            github_username: GitHub username
            jira_email: Jira email address
            
        Returns:
            True if user was reactivated, False otherwise
        """
        try:
            conditions = []
            params = []
            
            if github_username is not None:
                conditions.append("github_username = %s")
                params.append(github_username)
            
            if jira_email is not None:
                conditions.append("jira_email = %s")
                params.append(jira_email)
            
            if not conditions:
                return False
            
            query = f"""
                UPDATE users 
                SET is_active = TRUE, 
                    deactivated_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE {' OR '.join(conditions)}
                AND is_active = FALSE
                RETURNING id, github_username, full_name
            """
            results = self.db.execute_query(query, tuple(params))
            
            if results:
                user = results[0]
                logger.info(f"Reactivated user: {user['github_username']} (ID: {user['id']})")
                return True
            
            logger.warning(f"No inactive user found to reactivate with given identifiers")
            return False
            
        except Exception as e:
            logger.error(f"Error reactivating user: {e}")
            raise
    
    def get_inactive_users(self) -> List[Dict[str, Any]]:
        """
        Get all inactive (deactivated) users.
        
        Returns:
            List of inactive users with their details
        """
        try:
            query = """
                SELECT 
                    id,
                    github_username,
                    jira_email,
                    full_name,
                    display_name,
                    company,
                    deactivated_at,
                    created_at
                FROM users
                WHERE is_active = FALSE
                ORDER BY deactivated_at DESC
            """
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting inactive users: {e}")
            raise

