"""
Complete Database Setup Script
===============================
Runs ALL database setup operations in correct order:
1. Creates database
2. Loads schema
3. Applies migrations (audit log)
4. Verifies installation

Usage:
    python setup_database_complete.py
"""

import sys
import os
import subprocess
import psycopg2
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '1234',  # Change this to your password
    'database': 'developer_skills'
}

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def run_sql_file(cursor, filepath, description):
    """Execute a SQL file."""
    print(f"Loading {description}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
        print(f"[OK] {description} completed")
        return True
    except Exception as e:
        print(f"[ERROR] {description} failed: {e}")
        return False

def create_database():
    """Create the database if it doesn't exist."""
    print_section("Step 1: Database Creation")
    
    try:
        # Connect to postgres database to create our database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        
        if cursor.fetchone():
            print(f"[INFO] Database '{DB_CONFIG['database']}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"[OK] Database '{DB_CONFIG['database']}' created")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database creation failed: {e}")
        return False

def load_schema():
    """Load the main schema."""
    print_section("Step 2: Schema Loading")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Load main schema
        schema_path = Path('src/db/schema.sql')
        success = run_sql_file(cursor, schema_path, "Main schema (schema.sql)")
        
        cursor.close()
        conn.close()
        return success
        
    except Exception as e:
        print(f"[ERROR] Schema loading failed: {e}")
        return False

def apply_migrations():
    """Apply audit log migration."""
    print_section("Step 3: Applying Migrations")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        migrations_dir = Path('migrations')
        if not migrations_dir.exists():
            print("[INFO] No migrations directory found, skipping...")
            return True
        
        migrations = sorted(migrations_dir.glob('*.sql'))
        
        if not migrations:
            print("[INFO] No migrations to apply")
            return True
        
        for migration in migrations:
            run_sql_file(cursor, migration, f"Migration: {migration.name}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False

def verify_installation():
    """Verify database installation."""
    print_section("Step 4: Verification")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"[OK] Found {table_count} tables")
        
        # Check functions
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.routines 
            WHERE routine_schema = 'public'
        """)
        function_count = cursor.fetchone()[0]
        print(f"[OK] Found {function_count} stored functions")
        
        # Check views
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.views 
            WHERE table_schema = 'public'
        """)
        view_count = cursor.fetchone()[0]
        print(f"[OK] Found {view_count} views")
        
        # List key tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTables: {', '.join(tables)}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False

def main():
    """Main setup flow."""
    print("\n" + "="*60)
    print("  Developer Skill Analyzer - Complete Database Setup")
    print("="*60)
    
    # Run all steps
    steps = [
        ("Database Creation", create_database),
        ("Schema Loading", load_schema),
        ("Migrations", apply_migrations),
        ("Verification", verify_installation),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            success = step_func()
            if not success:
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print_section("Setup Summary")
    
    if failed_steps:
        print("[ERROR] Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\n[!] Please fix the errors and run again")
        return 1
    else:
        print("[OK] Database setup completed successfully!")
        print("\nNext steps:")
        print("   1. Update .env file with your credentials")
        print("   2. Run tests: pytest tests/")
        print("   3. Setup Claude Desktop: python scripts/utilities/setup_claude_desktop.py")
        print("   4. Start server: scripts/start_mcp_server.bat")
        return 0

if __name__ == "__main__":
    sys.exit(main())
