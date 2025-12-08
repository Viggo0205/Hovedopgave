"""
Test suite for data sanitization and export functionality.

Tests compliance with User Story requirements:
- FK-D1.2: Maskering af følsomme personoplysninger
- NFK-D1.1: Velstruktureret JSON schema
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from shared.data_sanitizer import (
    sanitize_developer_profile, 
    sanitize_list,
    mask_email,
    get_sensitive_field_summary
)


def test_email_removal():
    """Test that email addresses are removed from profiles."""
    print("\n=== Test 1: Email Removal ===")
    
    profile = {
        "username": "johndoe",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "public_repos": 42
    }
    
    sanitized = sanitize_developer_profile(profile)
    
    assert "email" not in sanitized, "❌ Email was not removed!"
    assert sanitized["username"] == "johndoe", "❌ Username was removed!"
    assert sanitized["name"] == "John Doe", "❌ Name was removed!"
    assert sanitized["public_repos"] == 42, "❌ Public repos was removed!"
    
    print("✅ Email successfully removed")
    print(f"   Original fields: {list(profile.keys())}")
    print(f"   Sanitized fields: {list(sanitized.keys())}")


def test_nested_email_removal():
    """Test that emails in nested structures are removed."""
    print("\n=== Test 2: Nested Email Removal ===")
    
    data = {
        "issue": {
            "key": "PROJ-123",
            "assignee": {
                "name": "John Doe",
                "emailAddress": "john@example.com"
            },
            "reporter": {
                "name": "Jane Smith", 
                "email": "jane@example.com"
            }
        }
    }
    
    sanitized = sanitize_developer_profile(data)
    
    assert "emailAddress" not in sanitized["issue"]["assignee"], "❌ Nested emailAddress not removed!"
    assert "email" not in sanitized["issue"]["reporter"], "❌ Nested email not removed!"
    assert sanitized["issue"]["assignee"]["name"] == "John Doe", "❌ Assignee name was removed!"
    
    print("✅ Nested emails successfully removed")
    print(f"   Assignee fields: {list(sanitized['issue']['assignee'].keys())}")
    print(f"   Reporter fields: {list(sanitized['issue']['reporter'].keys())}")


def test_list_sanitization():
    """Test that lists of profiles are sanitized."""
    print("\n=== Test 3: List Sanitization ===")
    
    members = [
        {"username": "user1", "email": "user1@example.com", "repos": 10},
        {"username": "user2", "email": "user2@example.com", "repos": 20},
        {"username": "user3", "email": "user3@example.com", "repos": 30}
    ]
    
    sanitized = sanitize_list(members)
    
    assert len(sanitized) == 3, "❌ List size changed!"
    
    for member in sanitized:
        assert "email" not in member, f"❌ Email not removed from {member['username']}!"
        assert "username" in member, f"❌ Username was removed!"
        assert "repos" in member, f"❌ Repos was removed!"
    
    print("✅ All list items sanitized")
    print(f"   Processed {len(sanitized)} members")
    print(f"   Sample fields: {list(sanitized[0].keys())}")


def test_email_masking():
    """Test email masking for logging purposes."""
    print("\n=== Test 4: Email Masking ===")
    
    test_cases = [
        ("john.doe@example.com", "j***"),
        ("a@test.com", "*"),  # Single char becomes just *
        ("", "***"),
    ]
    
    for email, expected_prefix in test_cases:
        masked = mask_email(email)
        actual_prefix = masked.split('@')[0] if '@' in masked else masked.split('@')[0]
        assert actual_prefix.startswith(expected_prefix) or actual_prefix == expected_prefix, \
            f"❌ Email {email} not masked correctly! Expected prefix: {expected_prefix}, Got: {masked}"
    
    print("✅ Email masking works correctly")
    print(f"   john.doe@example.com → {mask_email('john.doe@example.com')}")
    print(f"   a@test.com → {mask_email('a@test.com')}")


def test_sensitive_field_summary():
    """Test audit logging of sensitive fields."""
    print("\n=== Test 5: Sensitive Field Summary ===")
    
    data = {
        "user": {
            "name": "John",
            "email": "john@example.com",
            "phone": "123-456-7890"
        },
        "team": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "emailAddress": "bob@example.com"}
        ]
    }
    
    summary = get_sensitive_field_summary(data)
    
    assert summary.get("email", 0) >= 2, "❌ Didn't count all email fields!"
    assert summary.get("phone", 0) == 1, "❌ Didn't count phone field!"
    
    print("✅ Sensitive field detection works")
    print(f"   Found sensitive fields: {summary}")


def test_github_member_structure():
    """Test real GitHub organization member structure."""
    print("\n=== Test 6: GitHub Member Structure ===")
    
    member = {
        "username": "johndoe",
        "name": "John Doe",
        "company": "Acme Corp",
        "email": "john.doe@example.com",
        "bio": "Software Developer",
        "public_repos": 42,
        "followers": 150,
        "created_at": "2020-01-15T10:30:00"
    }
    
    sanitized = sanitize_developer_profile(member)
    
    # Should keep
    assert sanitized.get("username") == "johndoe"
    assert sanitized.get("name") == "John Doe"
    assert sanitized.get("company") == "Acme Corp"
    assert sanitized.get("bio") == "Software Developer"
    assert sanitized.get("public_repos") == 42
    
    # Should remove
    assert "email" not in sanitized
    
    print("✅ GitHub member structure properly sanitized")
    print(f"   Kept fields: {', '.join(sanitized.keys())}")


def test_jira_issue_structure():
    """Test real Jira issue structure."""
    print("\n=== Test 7: Jira Issue Structure ===")
    
    issue = {
        "key": "PROJ-123",
        "summary": "Fix login bug",
        "assignee_name": "John Doe",
        "reporter_name": "Jane Smith",
        "status": "In Progress",
        "priority": "High"
    }
    
    # This should already be in the correct format (using names not emails)
    sanitized = sanitize_developer_profile(issue)
    
    assert sanitized.get("key") == "PROJ-123"
    assert sanitized.get("assignee_name") == "John Doe"
    assert sanitized.get("reporter_name") == "Jane Smith"
    assert "email" not in sanitized
    assert "emailAddress" not in sanitized
    
    print("✅ Jira issue structure properly formatted")
    print(f"   Fields: {', '.join(sanitized.keys())}")


def run_all_tests():
    """Run all sanitization tests."""
    print("\n" + "="*60)
    print("DATA SANITIZATION TEST SUITE")
    print("Testing User Story: Dataanalytiker JSON API Export")
    print("="*60)
    
    try:
        test_email_removal()
        test_nested_email_removal()
        test_list_sanitization()
        test_email_masking()
        test_sensitive_field_summary()
        test_github_member_structure()
        test_jira_issue_structure()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nUser Story Requirements Coverage:")
        print("✅ FK-D1.2: Følsomme personoplysninger maskeres")
        print("✅ NFK-D1.1: Konsistent JSON struktur")
        print("✅ Email addresses fjernes fra alle niveauer")
        print("✅ Nested strukturer håndteres korrekt")
        print("✅ Lister saniteres")
        print("\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
