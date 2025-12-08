"""
Python-based database setup script (alternative to setup_database.bat)
Does not require psql command line tool
"""

import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass

def setup_database():
    """Setup PostgreSQL database using Python."""
    
    print("=" * 50)
    print("Developer Skill Analyzer - Database Setup (Python)")
    print("=" * 50)
    print()
    
    # Configuration
    db_config = {
        'user': 'postgres',
        'password': '1234',
        'host': 'localhost',
        'port': '5432'
    }
    db_name = 'developer_skills'
    schema_file = 'src/developer_skill_analyzer/db/schema.sql'
    
    # Check schema file exists
    if not os.path.exists(schema_file):
        print(f"ERROR: Schema file not found: {schema_file}")
        print("Please run this from the project root directory")
        return False
    
    print(f"[1/3] Schema file found: {schema_file}")
    
    try:
        # Connect to PostgreSQL (default database)
        print(f"\n[2/3] Connecting to PostgreSQL at {db_config['host']}:{db_config['port']}...")
        conn = psycopg2.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            database='postgres'  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"Database '{db_name}' already exists")
            cursor.execute(f"DROP DATABASE {db_name}")
            print(f"Dropped existing database")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Created database '{db_name}'")
        
        cursor.close()
        conn.close()
        
        # Connect to new database and run schema
        print(f"\n[3/3] Initializing schema and data...")
        conn = psycopg2.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            database=db_name
        )
        cursor = conn.cursor()
        
        # Read and execute schema file
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        
        # Verify setup
        cursor.execute("SELECT COUNT(*) FROM competence")
        competence_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rank")
        rank_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✓ Schema initialized successfully")
        print(f"✓ Loaded {rank_count} rank levels")
        print(f"✓ Loaded {competence_count} default competences")
        
        print("\n" + "=" * 50)
        print("Database setup completed successfully!")
        print("=" * 50)
        print()
        print(f"Database: {db_name}")
        print(f"User: {db_config['user']}")
        print(f"Connection string: postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_name}")
        print()
        print("Next steps:")
        print("1. Update your .env file with the DATABASE_URL")
        print("2. Run: python test_database.py")
        print("3. Start the MCP server")
        print()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\nERROR: Could not connect to PostgreSQL")
        print(f"Details: {e}")
        print("\nPossible issues:")
        print("1. PostgreSQL is not installed")
        print("2. PostgreSQL service is not running")
        print("3. Wrong password (default is 'postgres')")
        print("4. PostgreSQL is on a different port")
        print("\nTo start PostgreSQL service:")
        print("  Windows: services.msc -> find 'postgresql' -> Start")
        return False
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
