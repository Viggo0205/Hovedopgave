"""Pytest configuration and fixtures for database tests."""

import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Generator

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db.connection import DatabaseConnection
from db.repository import DatabaseRepository


@pytest.fixture(scope="session")
def test_db_config():
    """Configuration for test database."""
    return {
        'host': 'localhost',
        'port': 5432,
        'database': 'developer_skills_test',
        'user': 'postgres',
        'password': 'Zappanoel1229!'  # Match your actual PostgreSQL password
    }


@pytest.fixture(scope="session")
def test_connection_string(test_db_config):
    """Generate test database connection string."""
    return (
        f"postgresql://{test_db_config['user']}:{test_db_config['password']}@"
        f"{test_db_config['host']}:{test_db_config['port']}/{test_db_config['database']}"
    )


@pytest.fixture(scope="session")
def setup_test_database(test_db_config, test_connection_string):
    """Create test database and schema before all tests."""
    # Connect to default postgres database to create test database
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        database='postgres',
        user=test_db_config['user'],
        password=test_db_config['password']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Drop and recreate test database
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
        cursor.execute(f"CREATE DATABASE {test_db_config['database']}")
        print(f"\n✓ Test database '{test_db_config['database']}' created")
    finally:
        cursor.close()
        conn.close()
    
    # Connect to test database and load schema
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        database=test_db_config['database'],
        user=test_db_config['user'],
        password=test_db_config['password']
    )
    cursor = conn.cursor()
    
    try:
        # Load main schema
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'db', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        cursor.execute(schema_sql)
        
        # Load auto-update schema
        auto_update_schema_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'db', 'auto_update_schema.sql')
        with open(auto_update_schema_path, 'r', encoding='utf-8') as f:
            auto_update_sql = f.read()
        cursor.execute(auto_update_sql)
        
        conn.commit()
        print("✓ Test database schema loaded")
        
    finally:
        cursor.close()
        conn.close()
    
    yield test_connection_string
    
    # Teardown: Drop test database after all tests
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        database='postgres',
        user=test_db_config['user'],
        password=test_db_config['password']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
        print(f"\n✓ Test database '{test_db_config['database']}' dropped")
    finally:
        cursor.close()
        conn.close()


@pytest.fixture
def db_connection(setup_test_database, test_connection_string) -> Generator[DatabaseConnection, None, None]:
    """Provide a clean database connection for each test."""
    connection = DatabaseConnection(connection_string=test_connection_string)
    yield connection
    connection.close_all()


@pytest.fixture
def db_repository(db_connection) -> DatabaseRepository:
    """Provide a repository instance for each test."""
    return DatabaseRepository(db_connection=db_connection)


@pytest.fixture
def clean_database(db_connection):
    """Clean all data from test database tables before each test."""
    conn = db_connection.get_connection()
    cursor = conn.cursor()
    
    try:
        # Disable triggers temporarily
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Delete data in dependency order
        cursor.execute("DELETE FROM analysis_archive")
        cursor.execute("DELETE FROM user_competence")
        cursor.execute("DELETE FROM competence")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM rank")
        cursor.execute("DELETE FROM role")
        
        # Re-enable triggers
        cursor.execute("SET session_replication_role = 'origin';")
        
        conn.commit()
    finally:
        cursor.close()
        db_connection.return_connection(conn)
    
    yield
