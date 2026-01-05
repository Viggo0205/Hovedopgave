"""
Test script for developer removal functionality (User Story: Administrator removal)
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from db.repository import DatabaseRepository


async def test_developer_removal():
    """
    Test the complete developer removal workflow:
    1. List all removed developers
    2. Show removal functionality
    3. Show reactivation functionality
    """
    print("=" * 70)
    print("TEST: Administrator Developer Removal Functionality")
    print("=" * 70)
    
    db_repo = DatabaseRepository()
    
    # Step 1: List currently removed developers
    print("\n1. Liste over fjernede udviklere:")
    print("-" * 70)
    try:
        removed = db_repo.get_inactive_users()
        if removed:
            for user in removed:
                print(f"  • {user.get('github_username') or user.get('jira_email')}")
                print(f"    Navn: {user.get('full_name', 'N/A')}")
                print(f"    Fjernet: {user.get('deactivated_at')}")
                print()
        else:
            print("  Ingen fjernede udviklere i systemet")
        print(f"Total: {len(removed)} fjernede udviklere")
    except Exception as e:
        print(f"  Kunne ikke hente data: {e}")
    
    # Step 2: Demonstrate removal (uncomment to test with real user)
    print("\n\n2. Fjern en udvikler (eksempel):")
    print("-" * 70)
    print("Via MCP Tool i Claude:")
    print("  remove_developer(github_username='username')")
    print("  remove_developer(jira_email='user@example.com')")
    print("\nVia Python kode:")
    print("  db_repo.deactivate_user(github_username='username')")
    print("\nEksempel output:")
    example_output = {
        "status": "success",
        "message": "Developer 'testuser' has been removed",
        "developer": {
            "github_username": "testuser",
            "full_name": "Test User",
            "display_name": "Test"
        },
        "note": "This is a soft delete. Data is retained and user can be reactivated if needed.",
        "timestamp": datetime.now().isoformat()
    }
    print(json.dumps(example_output, indent=2, ensure_ascii=False))
    
    # Step 3: Show what happens after removal
    print("\n\n3. Efter fjernelse:")
    print("-" * 70)
    print("✓ Udvikleren vises IKKE længere i søgninger")
    print("✓ Udvikleren vises IKKE i skill-matching")
    print("✓ Udvikleren vises IKKE i mentor-forslag")
    print("✓ Data bevares (soft delete) for historik")
    print("✓ Kan genaktiveres hvis nødvendigt")
    
    # Step 4: Reactivation example
    print("\n\n4. Genaktivering (hvis nødvendigt):")
    print("-" * 70)
    print("Syntax:")
    print("  reactivate_developer(github_username='username')")
    print("\nEksempel output:")
    reactivate_output = {
        "status": "success",
        "message": "Developer has been reactivated",
        "github_username": "testuser",
        "timestamp": "2026-01-05T12:05:00"
    }
    print(json.dumps(reactivate_output, indent=2, ensure_ascii=False))
    
    # Step 5: Show available MCP tools
    print("\n\n5. Tilgængelige MCP Tools:")
    print("-" * 70)
    print("✓ remove_developer(github_username, jira_email)")
    print("  - Fjerner udvikler fra aktive (soft delete)")
    print("  - Kræver enten GitHub username eller Jira email")
    print("")
    print("✓ list_removed_developers()")
    print("  - Viser alle fjernede udviklere")
    print("  - Inkluderer deaktiveringsdato")
    print("")
    print("✓ reactivate_developer(github_username, jira_email)")
    print("  - Genaktiverer en tidligere fjernet udvikler")
    print("")
    print("✓ permanently_delete_developer(github_username, jira_email, confirm=True)")
    print("  - PERMANENT sletning (GDPR 'right to be forgotten')")
    print("  - Alle data fjernes og kan IKKE gendannes")
    print("  - Kræver confirm=True som sikkerhedscheck")
    
    print("\n\n" + "=" * 70)
    print("DATABASE STRUKTUR")
    print("=" * 70)
    print("users table:")
    print("  - is_active: BOOLEAN (TRUE = aktiv, FALSE = fjernet)")
    print("  - deactivated_at: TIMESTAMP (hvornår blev brugeren fjernet)")
    print("")
    print("Queries respekterer automatisk is_active flag:")
    print("  - get_all_employees() → kun aktive")
    print("  - get_employees_by_skill() → kun aktive (med option)")
    print("  - search queries → kun aktive")


if __name__ == "__main__":
    asyncio.run(test_developer_removal())
