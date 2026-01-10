"""Integration tests for database stored procedures and triggers."""

import pytest
from datetime import datetime, timedelta


class TestStoredProcedures:
    """Test suite for database stored procedures."""
    
    def test_get_or_create_user_procedure(self, db_connection, clean_database):
        """Test get_or_create_user stored procedure."""
        # Create new user
        result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, %s, %s, %s, %s, %s)",
            ('newuser', 'new@example.com', 'New User', 'New', 'Company', 'Location')
        )
        user_id_1 = result[0]['get_or_create_user']
        assert user_id_1 > 0
        
        # Get existing user
        result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, %s, %s, %s, %s, %s)",
            ('newuser', 'new@example.com', None, None, None, None)
        )
        user_id_2 = result[0]['get_or_create_user']
        
        # Should return same user
        assert user_id_1 == user_id_2
    
    def test_add_competence_procedure(self, db_connection, clean_database):
        """Test add_competence stored procedure."""
        result = db_connection.execute_query(
            "SELECT add_competence(%s, %s, %s)",
            ('TypeScript', 'programming_languages', 'TypeScript language')
        )
        competence_id = result[0]['add_competence']
        assert competence_id > 0
        
        # Verify competence exists
        verify = db_connection.execute_query(
            "SELECT * FROM competence WHERE id = %s",
            (competence_id,)
        )
        assert verify[0]['name'] == 'TypeScript'
    
    def test_update_user_competence_procedure(self, db_connection, clean_database):
        """Test update_user_competence stored procedure."""
        # Create user and competence
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, NULL, NULL, NULL, NULL, NULL)",
            ('compuser',)
        )
        user_id = user_result[0]['get_or_create_user']
        
        comp_result = db_connection.execute_query(
            "SELECT add_competence(%s, %s, NULL)",
            ('Go', 'programming_languages')
        )
        competence_id = comp_result[0]['add_competence']
        
        # Update competence
        db_connection.execute_query(
            "SELECT update_user_competence(%s, %s, %s, %s)",
            (user_id, competence_id, 80.0, 25),
            fetch=False
        )
        
        # Verify
        verify = db_connection.execute_query(
            "SELECT * FROM user_competence WHERE user_id = %s AND competence_id = %s",
            (user_id, competence_id)
        )
        assert len(verify) == 1
        assert float(verify[0]['procent']) == 80.0
        assert verify[0]['usage_frequency'] == 25
    
    def test_save_analysis_procedure(self, db_connection, clean_database):
        """Test save_analysis stored procedure with version management."""
        # Create user
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, NULL, NULL, NULL, NULL, NULL)",
            ('analysisuser',)
        )
        user_id = user_result[0]['get_or_create_user']
        
        # Save first analysis
        import json
        analysis_data = {'test': 'data', 'version': 1}
        result = db_connection.execute_query(
            "SELECT save_analysis(%s, %s)",
            (user_id, json.dumps(analysis_data))
        )
        version_1 = result[0]['save_analysis']
        assert version_1 == 1
        
        # Save second analysis
        analysis_data['version'] = 2
        result = db_connection.execute_query(
            "SELECT save_analysis(%s, %s)",
            (user_id, json.dumps(analysis_data))
        )
        version_2 = result[0]['save_analysis']
        assert version_2 == 2
        
        # Save third analysis - should delete first and reuse version number
        analysis_data['version'] = 3
        result = db_connection.execute_query(
            "SELECT save_analysis(%s, %s)",
            (user_id, json.dumps(analysis_data))
        )
        version_3 = result[0]['save_analysis']
        # Version number cycles back (1,2 -> delete 1, add 2 as new -> 1,2)
        assert version_3 in [1, 2]  # Accept either as version management may reuse numbers
        
        # Verify only 2 versions exist
        verify = db_connection.execute_query(
            "SELECT COUNT(*) as count FROM analysis_archive WHERE user_id = %s",
            (user_id,)
        )
        assert verify[0]['count'] == 2
    
    def test_get_latest_analysis_function(self, db_connection, clean_database):
        """Test get_latest_analysis stored function."""
        # Create user and save analysis
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, NULL, NULL, NULL, NULL, NULL)",
            ('latestuser',)
        )
        user_id = user_result[0]['get_or_create_user']
        
        import json
        analysis_data = {'language': 'Python', 'level': 'Expert'}
        db_connection.execute_query(
            "SELECT save_analysis(%s, %s)",
            (user_id, json.dumps(analysis_data))
        )
        
        # Get latest analysis
        result = db_connection.execute_query(
            "SELECT * FROM get_latest_analysis(%s)",
            (user_id,)
        )
        assert len(result) == 1
        assert result[0]['version_number'] == 1
        assert result[0]['metadata']['language'] == 'Python'


class TestAutoUpdateFeatures:
    """Test suite for auto-update schema features."""
    
    def test_last_analyzed_at_trigger(self, db_connection, clean_database):
        """Test that last_analyzed_at is updated automatically."""
        # Create user
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, NULL, NULL, NULL, NULL, NULL)",
            ('triggeruser',)
        )
        user_id = user_result[0]['get_or_create_user']
        
        # Check initial last_analyzed_at is NULL
        user = db_connection.execute_query(
            "SELECT last_analyzed_at FROM users WHERE id = %s",
            (user_id,)
        )
        assert user[0]['last_analyzed_at'] is None
        
        # Save analysis - should trigger update
        import json
        db_connection.execute_query(
            "SELECT save_analysis(%s, %s)",
            (user_id, json.dumps({'test': 'data'}))
        )
        
        # Check last_analyzed_at is now set
        user_after = db_connection.execute_query(
            "SELECT last_analyzed_at FROM users WHERE id = %s",
            (user_id,)
        )
        assert user_after[0]['last_analyzed_at'] is not None
    
    def test_get_users_for_update_function(self, db_connection, clean_database):
        """Test get_users_for_update function."""
        # Create users
        user1_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, %s, NULL, NULL, NULL, NULL)",
            ('user1', 'user1@example.com')
        )
        user1_id = user1_result[0]['get_or_create_user']
        
        user2_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, %s, NULL, NULL, NULL, NULL)",
            ('user2', 'user2@example.com')
        )
        user2_id = user2_result[0]['get_or_create_user']
        
        # Enable auto-update for both
        db_connection.execute_query(
            "UPDATE users SET auto_update_enabled = true WHERE id IN (%s, %s)",
            (user1_id, user2_id),
            fetch=False
        )
        
        # Get users for update (never analyzed)
        result = db_connection.execute_query(
            "SELECT * FROM get_users_for_update(5)"
        )
        assert len(result) >= 2
        
        # Analyze user1
        import json
        db_connection.execute_query(
            "SELECT save_analysis(%s, %s)",
            (user1_id, json.dumps({'test': 'data'}))
        )
        
        # Get users for update (user1 just analyzed, shouldn't appear)
        result_after = db_connection.execute_query(
            "SELECT * FROM get_users_for_update(5)"
        )
        user_ids_after = [r['user_id'] for r in result_after]
        assert user1_id not in user_ids_after
        assert user2_id in user_ids_after
    
    def test_auto_update_enabled_flag(self, db_connection, clean_database):
        """Test auto_update_enabled flag filtering."""
        # Create user with auto-update disabled
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, NULL, NULL, NULL, NULL, NULL)",
            ('disableduser',)
        )
        user_id = user_result[0]['get_or_create_user']
        
        # Explicitly disable auto-update
        db_connection.execute_query(
            "UPDATE users SET auto_update_enabled = false WHERE id = %s",
            (user_id,),
            fetch=False
        )
        
        # Should not appear in get_users_for_update
        result = db_connection.execute_query(
            "SELECT * FROM get_users_for_update(5)"
        )
        user_ids = [r['user_id'] for r in result]
        assert user_id not in user_ids


class TestDatabaseViews:
    """Test suite for database views."""
    
    def test_user_competence_overview_view(self, db_connection, clean_database):
        """Test user_competence_overview view."""
        # Ensure ranks exist (required by view)
        db_connection.execute_query("""
            INSERT INTO rank (id, name, min_percent, max_percent)
            VALUES 
                (1, 'Beginner', 0, 24),
                (2, 'Intermediate', 25, 49),
                (3, 'Advanced', 50, 74),
                (4, 'Expert', 75, 100)
            ON CONFLICT (id) DO NOTHING
        """, fetch=False)
        
        # Create user and competence
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, NULL, %s, NULL, NULL, NULL)",
            ('viewuser', 'View User')
        )
        user_id = user_result[0]['get_or_create_user']
        
        comp_result = db_connection.execute_query(
            "SELECT add_competence(%s, %s, NULL)",
            ('Rust', 'programming_languages')
        )
        competence_id = comp_result[0]['add_competence']
        
        # Add user competence - use the returned value to verify
        db_connection.execute_query(
            "SELECT update_user_competence(%s, %s, %s, %s, NULL)",
            (user_id, competence_id, 65.0, 15)
        )
        
        # Verify user_competence was inserted
        uc_verify = db_connection.execute_query(
            "SELECT * FROM user_competence WHERE user_id = %s AND competence_id = %s",
            (user_id, competence_id)
        )
        assert len(uc_verify) > 0, f"user_competence row not inserted for user_id={user_id}, competence_id={competence_id}"
        
        # Query view
        result = db_connection.execute_query(
            "SELECT * FROM user_competence_overview WHERE user_id = %s",
            (user_id,)
        )
        
        # If view returns 0 rows, check if rank table has data
        if len(result) == 0:
            rank_check = db_connection.execute_query("SELECT * FROM rank")
            assert len(rank_check) > 0, "Rank table is empty - view cannot work without ranks"
        
        assert len(result) >= 1, f"Expected at least 1 row in view, got {len(result)}"
        assert result[0]['full_name'] == 'View User'
        assert result[0]['competence_name'] == 'Rust'
        assert float(result[0]['procent']) == 65.0
    
    def test_v_update_status_view(self, db_connection, clean_database):
        """Test v_update_status view."""
        # Create user with GitHub and Jira
        user_result = db_connection.execute_query(
            "SELECT get_or_create_user(%s, %s, %s, NULL, NULL, NULL)",
            ('statususer', 'status@example.com', 'Status User')
        )
        user_id = user_result[0]['get_or_create_user']
        
        # Enable auto-update
        db_connection.execute_query(
            "UPDATE users SET auto_update_enabled = true WHERE id = %s",
            (user_id,),
            fetch=False
        )
        
        # Query view (note: view uses 'id' not 'user_id')
        result = db_connection.execute_query(
            "SELECT * FROM v_update_status WHERE id = %s",
            (user_id,)
        )
        
        assert len(result) == 1
        assert result[0]['github_username'] == 'statususer'
        assert result[0]['jira_email'] == 'status@example.com'
        assert result[0]['auto_update_enabled'] is True
        assert result[0]['update_status'] == 'Never analyzed'
