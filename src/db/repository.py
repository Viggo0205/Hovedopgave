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
        usage_frequency: int = 0,
        analysis_version: Optional[int] = None
    ) -> None:
        """
        Update user's competence level (current + optional history).
        
        Args:
            user_id: User ID
            competence_name: Name of the competence
            procent: Competence percentage (0-100)
            usage_frequency: Usage frequency count
            analysis_version: Optional version number to also save in history table (1 or 2)
        """
        try:
            # Get competence ID
            query = "SELECT id FROM competence WHERE name = %s"
            result = self.db.execute_query(query, (competence_name,))
            
            if not result:
                logger.warning(f"Competence not found: {competence_name}")
                return
            
            competence_id = result[0]['id']
            
            # Update user competence (and history if version specified)
            query = "SELECT update_user_competence(%s, %s, %s, %s, %s)"
            self.db.execute_query(query, (user_id, competence_id, procent, usage_frequency, analysis_version), fetch=False)
            
            logger.debug(f"Updated competence for user {user_id}: {competence_name} = {procent}% (version: {analysis_version})")
            
        except Exception as e:
            logger.error(f"Error updating user competence: {e}")
            raise
    
    def save_analysis(
        self, 
        user_id: int, 
        metadata: Dict[str, Any],
        total_repositories: int = 0,
        data_source: str = 'github'
    ) -> int:
        """
        Save analysis metadata with version management (keeps max 2 versions).
        NOTE: Competences are stored in user_competence_history, not here.
        
        Args:
            user_id: User ID
            metadata: Analysis metadata (profile, repos, raw data - NOT processed competences)
            total_repositories: Total repository count
            data_source: Source of analysis ('github' or 'jira')
            
        Returns:
            Version number of saved analysis
        """
        try:
            # Serialize datetime objects to ISO format strings
            serialized_metadata = _serialize_datetime(metadata)
            
            query = "SELECT save_analysis(%s, %s, %s, %s)"
            result = self.db.execute_query(
                query,
                (user_id, json.dumps(serialized_metadata), total_repositories, data_source)
            )
            version = result[0]['save_analysis']
            
            logger.info(f"Saved analysis metadata for user {user_id} as version {version}")
            return version
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
    
    def get_latest_analysis(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the latest analysis metadata for a user.
        NOTE: This returns only metadata. Use get_competences_for_version() to get competences.
        
        Args:
            user_id: User ID
            
        Returns:
            Analysis metadata or None if not found
        """
        try:
            query = "SELECT * FROM get_latest_analysis(%s)"
            results = self.db.execute_query(query, (user_id,))
            
            if not results:
                return None
            
            result = results[0]
            return {
                'id': result['id'],
                'metadata': result['metadata'],
                'analysis_date': result['analysis_date'].isoformat() if result['analysis_date'] else None,
                'version_number': result['version_number'],
                'total_repositories': result['total_repositories']
            }
            
        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None
    
    def get_all_analyses(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all analysis metadata for a user (max 2).
        Args:
            user_id: User ID
            
        Returns:
            List of analysis metadata
        """
        try:
            query = """
                SELECT id, metadata, analysis_date, version_number, total_repositories, data_source
                FROM analysis_archive
                WHERE user_id = %s
                ORDER BY version_number DESC
            """
            results = self.db.execute_query(query, (user_id,))
            
            analyses = []
            for row in results:
                analyses.append({
                    'id': row['id'],
                    'metadata': row['metadata'],
                    'analysis_date': row['analysis_date'].isoformat() if row['analysis_date'] else None,
                    'version_number': row['version_number'],
                    'total_repositories': row.get('total_repositories', 0),
                    'data_source': row.get('data_source', 'github')
                })
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error getting all analyses: {e}")
            return []
    
    def get_competences_for_version(self, user_id: int, version_number: int) -> List[Dict[str, Any]]:
        """
        Get historical competences for a specific analysis version.
        
        Args:
            user_id: User ID
            version_number: Version number (1 or 2)
            
        Returns:
            List of competences with their historical values
        """
        try:
            query = "SELECT * FROM get_competences_for_version(%s, %s)"
            results = self.db.execute_query(query, (user_id, version_number))
            
            competences = []
            for row in results:
                competences.append({
                    'competence_id': row['competence_id'],
                    'competence_name': row['competence_name'],
                    'category': row['category'],
                    'procent': float(row['procent']),
                    'usage_frequency': row['usage_frequency'],
                    'rank_name': row['rank_name'],
                    'recorded_at': row['recorded_at'].isoformat() if row['recorded_at'] else None
                })
            
            return competences
            
        except Exception as e:
            logger.error(f"Error getting competences for version: {e}")
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
        jira_email: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get user by GitHub username or Jira email.
        
        Args:
            github_username: GitHub username
            jira_email: Jira email
            
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
            
            query = f"SELECT * FROM users WHERE {' OR '.join(conditions)} LIMIT 1"
            results = self.db.execute_query(query, tuple(params))
            
            if results:
                return dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by identifier: {e}")
            return None
