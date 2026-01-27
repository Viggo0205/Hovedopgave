"""Unit tests for DatabaseConnection class."""

import pytest  # type: ignore
from db.connection import DatabaseConnection


class TestDatabaseConnection:
    """Test suite for DatabaseConnection."""
    
    def test_connection_initialization(self, setup_test_database, test_connection_string):
        """Test database connection initializes successfully."""
        db = DatabaseConnection(connection_string=test_connection_string)
        assert db is not None
        assert db.connection_string == test_connection_string
        assert db._pool is not None
        db.close_all()
    
    def test_get_connection(self, db_connection):
        """Test getting a connection from the pool."""
        conn = db_connection.get_connection()
        assert conn is not None
        
        # Test connection is usable
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        assert result['test'] == 1
        
        cursor.close()
        db_connection.return_connection(conn)
    
    def test_return_connection(self, db_connection):
        """Test returning a connection to the pool."""
        conn = db_connection.get_connection()
        db_connection.return_connection(conn)
        
        # Should be able to get another connection
        conn2 = db_connection.get_connection()
        assert conn2 is not None
        db_connection.return_connection(conn2)
    
    def test_execute_query_select(self, db_connection):
        """Test executing a SELECT query."""
        result = db_connection.execute_query("SELECT 1 as num, 'test' as str")
        assert len(result) == 1
        assert result[0]['num'] == 1
        assert result[0]['str'] == 'test'
    
    def test_execute_query_with_params(self, db_connection, clean_database):
        """Test executing query with parameters."""
        # Insert a test user
        query = """
            INSERT INTO users (github_username, full_name)
            VALUES (%s, %s)
            RETURNING id
        """
        result = db_connection.execute_query(query, ('testuser', 'Test User'))
        assert len(result) == 1
        assert 'id' in result[0]
        
        # Query with parameters
        query = "SELECT * FROM users WHERE github_username = %s"
        result = db_connection.execute_query(query, ('testuser',))
        assert len(result) == 1
        assert result[0]['github_username'] == 'testuser'
        assert result[0]['full_name'] == 'Test User'
    
    def test_execute_query_no_fetch(self, db_connection, clean_database):
        """Test executing query without fetching results."""
        query = """
            INSERT INTO users (github_username, full_name)
            VALUES (%s, %s)
        """
        result = db_connection.execute_query(
            query, 
            ('nofetchuser', 'No Fetch User'),
            fetch=False
        )
        assert result is None
        
        # Verify data was inserted
        verify_query = "SELECT * FROM users WHERE github_username = %s"
        verify_result = db_connection.execute_query(verify_query, ('nofetchuser',))
        assert len(verify_result) == 1
    
    def test_execute_transaction_commit(self, db_connection, clean_database):
        """Test transaction commit."""
        query = """
            INSERT INTO users (github_username, full_name)
            VALUES (%s, %s)
        """
        db_connection.execute_transaction([
            (query, ('user1', 'User One')),
            (query, ('user2', 'User Two'))
        ])
        
        # Verify both inserted
        result = db_connection.execute_query("SELECT COUNT(*) as count FROM users")
        assert result[0]['count'] == 2
    
    def test_execute_transaction_rollback(self, db_connection, clean_database):
        """Test transaction rollback on error."""
        query = """
            INSERT INTO users (github_username, full_name)
            VALUES (%s, %s)
        """
        
        # Second query will fail (duplicate username)
        with pytest.raises(Exception):
            db_connection.execute_transaction([
                (query, ('user1', 'User One')),
                (query, ('user1', 'User One Again'))  # Duplicate - should fail
            ])
        
        # Verify nothing was inserted (rollback)
        result = db_connection.execute_query("SELECT COUNT(*) as count FROM users")
        assert result[0]['count'] == 0
    
    def test_health_check_healthy(self, db_connection):
        """Test health check when database is healthy."""
        is_healthy = db_connection.health_check()
        assert is_healthy is True
    
    def test_health_check_unhealthy(self, test_connection_string):
        """Test health check with invalid connection."""
        bad_connection_string = test_connection_string.replace('5432', '9999')
        
        # Should raise exception during initialization due to bad port
        with pytest.raises(Exception):
            db = DatabaseConnection(connection_string=bad_connection_string)
    
    def test_connection_pool_reuse(self, db_connection):
        """Test connection pool reuses connections."""
        # Get and return multiple connections
        connections = []
        for _ in range(3):
            conn = db_connection.get_connection()
            connections.append(conn)
        
        # Return all connections
        for conn in connections:
            db_connection.return_connection(conn)
        
        # Get connections again - should reuse from pool
        conn_reused = db_connection.get_connection()
        assert conn_reused is not None
        db_connection.return_connection(conn_reused)
    
    def test_close_all_connections(self, test_connection_string):
        """Test closing all connections in pool."""
        db = DatabaseConnection(connection_string=test_connection_string)
        
        # Get some connections
        conn1 = db.get_connection()
        db.return_connection(conn1)
        
        # Close all
        db.close_all()
        
        # Pool should be closed
        assert db._pool is None or db._pool.closed
        
        # After closing, should not be able to get connections from closed pool
        # This is expected behavior - would need to create new DatabaseConnection instance
