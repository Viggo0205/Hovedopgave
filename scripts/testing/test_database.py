"""
Test script for database functionality.
Run this to verify database setup and connections.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from developer_skill_analyzer.db.connection import DatabaseConnection
from developer_skill_analyzer.db.repository import DatabaseRepository


def test_connection():
    """Test database connection."""
    print("=" * 50)
    print("Testing Database Connection")
    print("=" * 50)
    
    try:
        db = DatabaseConnection()
        result = db.execute_query("SELECT version()")
        print(f"✓ Connected to PostgreSQL")
        print(f"  Version: {result[0]['version'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_schema():
    """Test that schema is set up correctly."""
    print("\n" + "=" * 50)
    print("Testing Database Schema")
    print("=" * 50)
    
    try:
        db = DatabaseConnection()
        
        # Test tables exist
        tables = ['role', 'users', 'competence', 'rank', 'user_competence', 'analysis_archive']
        for table in tables:
            result = db.execute_query(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (table,)
            )
            if result[0]['exists']:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing")
                return False
        
        # Test views exist
        views = ['user_competence_overview', 'competence_categories']
        for view in views:
            result = db.execute_query(
                "SELECT EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = %s)",
                (view,)
            )
            if result[0]['exists']:
                print(f"✓ View '{view}' exists")
            else:
                print(f"✗ View '{view}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        return False


def test_repository():
    """Test repository functions."""
    print("\n" + "=" * 50)
    print("Testing Database Repository")
    print("=" * 50)
    
    try:
        repo = DatabaseRepository()
        
        # Test get competence categories
        categories = repo.get_competence_categories()
        print(f"✓ Loaded {len(categories)} competence categories")
        for cat, skills in categories.items():
            print(f"  - {cat}: {len(skills)} skills")
        
        # Test get all competences
        competences = repo.get_all_competences()
        print(f"✓ Loaded {len(competences)} competences")
        
        # Test add competence
        comp_id = repo.add_competence(
            name="Test Skill",
            category="frameworks_tools",
            description="This is a test skill"
        )
        print(f"✓ Added test competence (ID: {comp_id})")
        
        # Test get or create user
        user_id = repo.get_or_create_user(
            github_username="test_user",
            full_name="Test User",
            display_name="Tester"
        )
        print(f"✓ Created test user (ID: {user_id})")
        
        # Verify user was actually created - with debug
        verify_user = repo.get_user_by_identifier(github_username="test_user")
        
        # Debug: Check what we got back
        if verify_user:
            verified_user_id = verify_user['id']
            print(f"  Verified user exists with ID: {verified_user_id}")
        else:
            # Try direct query to see if user exists
            db = DatabaseConnection()
            direct_check = db.execute_query("SELECT * FROM users WHERE github_username = %s", ("test_user",))
            if direct_check:
                print(f"  DEBUG: User exists in database: {dict(direct_check[0])}")
                verified_user_id = direct_check[0]['id']
            else:
                print(f"✗ User was not created properly - not found in database")
                return False
        
        # Test update user competence
        repo.update_user_competence(
            user_id=verified_user_id,
            competence_name="Test Skill",
            procent=75.5,
            usage_frequency=10
        )
        print(f"✓ Updated user competence")
        
        # Test get user competence overview
        overview = repo.get_user_competence_overview(verified_user_id)
        print(f"✓ Retrieved user competence overview ({len(overview)} entries)")
        
        # Test save analysis
        test_analysis = {
            "summary": {"total_skills": 5},
            "test_date": datetime.now().isoformat()
        }
        version = repo.save_analysis(verified_user_id, test_analysis)
        print(f"✓ Saved analysis (version {version})")
        
        # Test get latest analysis
        latest = repo.get_latest_analysis(verified_user_id)
        if latest:
            print(f"✓ Retrieved latest analysis (version {latest['version_number']})")
        else:
            print(f"✗ Failed to retrieve latest analysis")
            return False
        
        # Cleanup test data
        db = DatabaseConnection()
        db.execute_query("DELETE FROM users WHERE github_username = 'test_user'", fetch=False)
        db.execute_query("DELETE FROM competence WHERE name = 'Test Skill'", fetch=False)
        print(f"✓ Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"✗ Repository test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stored_procedures():
    """Test stored procedures."""
    print("\n" + "=" * 50)
    print("Testing Stored Procedures")
    print("=" * 50)
    
    try:
        db = DatabaseConnection()
        
        # Test add_competence procedure
        result = db.execute_query(
            "SELECT add_competence(%s, %s, %s)",
            ("SP Test Skill", "frameworks_tools", "Test from stored procedure")
        )
        comp_id = result[0]['add_competence']
        print(f"✓ add_competence procedure works (ID: {comp_id})")
        
        # Test get_or_create_user procedure
        result = db.execute_query(
            "SELECT get_or_create_user(%s, %s, %s, %s, %s, %s)",
            ("sp_test_user", "sp@test.com", "SP Test", "SP Tester", "Test Co", "Test City")
        )
        user_id = result[0]['get_or_create_user']
        print(f"✓ get_or_create_user procedure works (ID: {user_id})")
        
        # Cleanup
        db.execute_query("DELETE FROM users WHERE github_username = 'sp_test_user'", fetch=False)
        db.execute_query("DELETE FROM competence WHERE name = 'SP Test Skill'", fetch=False)
        print(f"✓ Cleaned up stored procedure test data")
        
        return True
        
    except Exception as e:
        print(f"✗ Stored procedure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║  Developer Skill Analyzer - Database Tests  ║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Connection", test_connection()))
    results.append(("Schema", test_schema()))
    results.append(("Repository", test_repository()))
    results.append(("Stored Procedures", test_stored_procedures()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Database is ready to use.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
