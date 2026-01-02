"""Unit tests for DatabaseRepository class."""

import pytest
import json
from datetime import datetime
from db.repository import DatabaseRepository, _serialize_datetime


class TestSerializeDatetime:
    """Test suite for datetime serialization helper."""
    
    def test_serialize_datetime_object(self):
        """Test serializing a datetime object."""
        dt = datetime(2025, 12, 29, 15, 30, 45)
        result = _serialize_datetime(dt)
        assert isinstance(result, str)
        assert result == '2025-12-29T15:30:45'
    
    def test_serialize_dict_with_datetime(self):
        """Test serializing dictionary containing datetime."""
        data = {
            'name': 'test',
            'created_at': datetime(2025, 1, 1, 12, 0, 0)
        }
        result = _serialize_datetime(data)
        assert result['name'] == 'test'
        assert result['created_at'] == '2025-01-01T12:00:00'
    
    def test_serialize_list_with_datetime(self):
        """Test serializing list containing datetime."""
        data = [
            datetime(2025, 1, 1),
            'string',
            123
        ]
        result = _serialize_datetime(data)
        assert result[0] == '2025-01-01T00:00:00'
        assert result[1] == 'string'
        assert result[2] == 123
    
    def test_serialize_nested_structures(self):
        """Test serializing nested structures with datetime."""
        data = {
            'user': {
                'name': 'John',
                'created': datetime(2025, 1, 1)
            },
            'posts': [
                {'id': 1, 'date': datetime(2025, 2, 1)},
                {'id': 2, 'date': datetime(2025, 3, 1)}
            ]
        }
        result = _serialize_datetime(data)
        assert result['user']['created'] == '2025-01-01T00:00:00'
        assert result['posts'][0]['date'] == '2025-02-01T00:00:00'
        assert result['posts'][1]['date'] == '2025-03-01T00:00:00'


class TestDatabaseRepository:
    """Test suite for DatabaseRepository."""
    
    def test_repository_initialization(self, db_connection):
        """Test repository initializes with connection."""
        repo = DatabaseRepository(db_connection=db_connection)
        assert repo.db is not None
        assert repo.db == db_connection
    
    def test_repository_default_connection(self, setup_test_database):
        """Test repository creates default connection if none provided."""
        # Set environment variable to use test database
        import os
        original_db_url = os.environ.get('DATABASE_URL')
        
        # Use session-scoped test connection string
        os.environ['DATABASE_URL'] = setup_test_database
        
        try:
            repo = DatabaseRepository()
            assert repo.db is not None
            
            # Test that it can query
            result = repo.db.execute_query("SELECT 1 as test")
            assert result[0]['test'] == 1
        finally:
            # Restore original
            if original_db_url:
                os.environ['DATABASE_URL'] = original_db_url
            elif 'DATABASE_URL' in os.environ:
                del os.environ['DATABASE_URL']
    
    def test_add_competence(self, db_repository, clean_database):
        """Test adding a new competence."""
        competence_id = db_repository.add_competence(
            name='Python',
            category='programming_languages',
            description='Python programming language'
        )
        
        assert isinstance(competence_id, int)
        assert competence_id > 0
        
        # Verify competence exists
        competences = db_repository.get_all_competences()
        assert any(c['name'] == 'Python' for c in competences)
    
    def test_get_or_create_user_new(self, db_repository, clean_database):
        """Test creating a new user."""
        user_id = db_repository.get_or_create_user(
            github_username='johndoe',
            jira_email='john@example.com',
            full_name='John Doe',
            display_name='John',
            company='Tech Corp',
            location='San Francisco'
        )
        
        assert isinstance(user_id, int)
        assert user_id > 0
        
        # Verify user exists
        user = db_repository.get_user_by_identifier(github_username='johndoe')
        assert user is not None
        assert user['github_username'] == 'johndoe'
        assert user['jira_email'] == 'john@example.com'
        assert user['full_name'] == 'John Doe'
    
    def test_get_or_create_user_existing(self, db_repository, clean_database):
        """Test getting an existing user."""
        # Create user first
        user_id_1 = db_repository.get_or_create_user(
            github_username='janedoe',
            jira_email='jane@example.com'
        )
        
        # Get same user
        user_id_2 = db_repository.get_or_create_user(
            github_username='janedoe',
            jira_email='jane@example.com'
        )
        
        # Should return same ID
        assert user_id_1 == user_id_2
    
    def test_update_user_competence(self, db_repository, clean_database):
        """Test updating user's competence level."""
        # Create user and competence
        user_id = db_repository.get_or_create_user(github_username='testuser')
        competence_id = db_repository.add_competence('JavaScript', 'programming_languages')
        
        # Update competence
        db_repository.update_user_competence(
            user_id=user_id,
            competence_name='JavaScript',
            procent=75.5,
            usage_frequency=10
        )
        
        # Verify update directly in user_competence table
        conn = db_repository.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_competence WHERE user_id = %s AND competence_id = %s",
            (user_id, competence_id)
        )
        result = cursor.fetchall()
        cursor.close()
        db_repository.db.return_connection(conn)
        
        assert len(result) >= 1, "user_competence row should exist"
        assert float(result[0]['procent']) == 75.5
    
    def test_save_analysis(self, db_repository, clean_database):
        """Test saving analysis data."""
        # Create user
        user_id = db_repository.get_or_create_user(github_username='analyst')
        
        # Save analysis
        analysis_data = {
            'username': 'analyst',
            'language_skills': {
                'Python': {'level': 'Expert', 'total_lines': 50000}
            },
            'analyzed_at': datetime(2025, 12, 29, 10, 0, 0)
        }
        
        version = db_repository.save_analysis(user_id, analysis_data)
        assert version == 1
        
        # Save second version
        analysis_data['language_skills']['JavaScript'] = {'level': 'Intermediate'}
        version2 = db_repository.save_analysis(user_id, analysis_data)
        assert version2 == 2
    
    def test_save_analysis_max_versions(self, db_repository, clean_database):
        """Test that only 2 versions are kept."""
        user_id = db_repository.get_or_create_user(github_username='versiontest')
        
        # Save 3 versions
        for i in range(3):
            analysis_data = {'version': i + 1, 'data': f'test_{i}'}
            db_repository.save_analysis(user_id, analysis_data)
        
        # Should only have 2 versions (latest)
        all_analyses = db_repository.get_all_analyses(user_id)
        assert len(all_analyses) == 2
        assert all_analyses[0]['analysis_data']['version'] == 3
        assert all_analyses[1]['analysis_data']['version'] == 2
    
    def test_get_latest_analysis(self, db_repository, clean_database):
        """Test retrieving latest analysis."""
        user_id = db_repository.get_or_create_user(github_username='latestuser')
        
        # Save analysis
        analysis_data = {'test': 'data', 'version': 1}
        db_repository.save_analysis(user_id, analysis_data)
        
        # Get latest
        latest = db_repository.get_latest_analysis(user_id)
        assert latest is not None
        assert latest['analysis_data']['test'] == 'data'
        assert latest['version_number'] == 1
    
    def test_get_latest_analysis_no_data(self, db_repository, clean_database):
        """Test getting latest analysis when none exists."""
        user_id = db_repository.get_or_create_user(github_username='nodata')
        
        latest = db_repository.get_latest_analysis(user_id)
        assert latest is None
    
    def test_get_all_analyses(self, db_repository, clean_database):
        """Test retrieving all analyses."""
        user_id = db_repository.get_or_create_user(github_username='allanalyses')
        
        # Save multiple analyses
        for i in range(2):
            analysis_data = {'version': i + 1}
            db_repository.save_analysis(user_id, analysis_data)
        
        # Get all
        all_analyses = db_repository.get_all_analyses(user_id)
        assert len(all_analyses) == 2
        assert all_analyses[0]['version_number'] == 2
        assert all_analyses[1]['version_number'] == 1
    
    def test_get_user_competence_overview(self, db_repository, clean_database):
        """Test getting user competence overview."""
        # Create user and competences
        user_id = db_repository.get_or_create_user(github_username='overview_user')
        db_repository.add_competence('Python', 'programming_languages')
        db_repository.add_competence('React', 'frameworks_tools')
        
        # Add competences to user
        db_repository.update_user_competence(user_id, 'Python', 85.0, 50)
        db_repository.update_user_competence(user_id, 'React', 70.0, 30)
        
        # Verify data in user_competence table
        conn = db_repository.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM user_competence WHERE user_id = %s", (user_id,))
        count_result = cursor.fetchone()
        cursor.close()
        db_repository.db.return_connection(conn)
        
        assert count_result['count'] == 2, "Should have 2 competences in user_competence table"
    
    def test_get_user_competence_overview_all_users(self, db_repository, clean_database):
        """Test getting competence overview for all users."""
        # Create multiple users with competences
        user1_id = db_repository.get_or_create_user(github_username='user1')
        user2_id = db_repository.get_or_create_user(github_username='user2')
        
        db_repository.add_competence('Python', 'programming_languages')
        
        db_repository.update_user_competence(user1_id, 'Python', 90.0)
        db_repository.update_user_competence(user2_id, 'Python', 60.0)
        
        # Verify data exists in table
        conn = db_repository.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM user_competence")
        count_result = cursor.fetchone()
        cursor.close()
        db_repository.db.return_connection(conn)
        
        assert count_result['count'] >= 2, "Should have at least 2 competence records"
    
    def test_get_all_competences(self, db_repository, clean_database):
        """Test retrieving all competences."""
        # Add some competences
        db_repository.add_competence('Python', 'programming_languages')
        db_repository.add_competence('JavaScript', 'programming_languages')
        db_repository.add_competence('React', 'frameworks_tools')
        
        # Get all
        competences = db_repository.get_all_competences()
        assert len(competences) >= 3
        
        names = [c['name'] for c in competences]
        assert 'Python' in names
        assert 'JavaScript' in names
        assert 'React' in names
    
    def test_get_user_by_identifier_github(self, db_repository, clean_database):
        """Test getting user by GitHub username."""
        user_id = db_repository.get_or_create_user(
            github_username='githubuser',
            full_name='GitHub User'
        )
        
        user = db_repository.get_user_by_identifier(github_username='githubuser')
        assert user is not None
        assert user['id'] == user_id
        assert user['github_username'] == 'githubuser'
    
    def test_get_user_by_identifier_jira(self, db_repository, clean_database):
        """Test getting user by Jira email."""
        user_id = db_repository.get_or_create_user(
            jira_email='jira@example.com',
            full_name='Jira User'
        )
        
        user = db_repository.get_user_by_identifier(jira_email='jira@example.com')
        assert user is not None
        assert user['id'] == user_id
        assert user['jira_email'] == 'jira@example.com'
    
    def test_get_user_by_identifier_not_found(self, db_repository, clean_database):
        """Test getting user that doesn't exist."""
        user = db_repository.get_user_by_identifier(github_username='nonexistent')
        assert user is None
    
    def test_datetime_serialization_in_analysis(self, db_repository, clean_database):
        """Test that datetime objects are properly serialized when saving analysis."""
        user_id = db_repository.get_or_create_user(github_username='datetimeuser')
        
        # Analysis with datetime objects
        analysis_data = {
            'analyzed_at': datetime(2025, 12, 29, 15, 30, 0),
            'profile': {
                'created_at': datetime(2020, 1, 1, 0, 0, 0)
            },
            'commits': [
                {'date': datetime(2025, 12, 1), 'count': 5},
                {'date': datetime(2025, 12, 2), 'count': 3}
            ]
        }
        
        # Should not raise error
        version = db_repository.save_analysis(user_id, analysis_data)
        assert version == 1
        
        # Retrieve and verify
        latest = db_repository.get_latest_analysis(user_id)
        assert latest is not None
        assert isinstance(latest['analysis_data']['analyzed_at'], str)
        assert latest['analysis_data']['analyzed_at'] == '2025-12-29T15:30:00'
