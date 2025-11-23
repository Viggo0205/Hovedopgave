# tests/test_extractors.py
import pytest
from datetime import datetime, timedelta
from developer_skill_analyzer.analyzers.jira_analyzer import JiraAnalyzer
from developer_skill_analyzer.models.analysis import IssueAnalysis

@pytest.fixture
def analyzer():
    # init with dummy params
    return JiraAnalyzer("https://example.atlassian.net", "me@example.com", "token")

def test_extract_skills_from_issue_basic(analyzer):
    summary = "Fix bug in API endpoint and write unit test"
    description = "This task contains SQL queries and documentation updates."
    skills = analyzer._extract_skills_from_issue(summary, description)
    assert "api development" in skills
    assert "testing" in skills
    assert "database" in skills
    assert "documentation" in skills

def test_extract_technologies_from_issue_basic(analyzer):
    summary = "Migrate service to Django and use PostgreSQL"
    description = "Also configure docker and AWS deployment"
    techs = analyzer._extract_technologies_from_issue(summary, description)
    assert "django" in techs
    assert "postgresql" in techs
    assert "docker" in techs
    assert "aws" in techs

def test_calculate_issue_complexity_various():
    issue = IssueAnalysis(
        key="TEST-1",
        issue_type="Bug",
        status="Done",
        priority="High",
        summary="s",
        description_length=600,
        created_date=datetime.utcnow(),
        resolved_date=datetime.utcnow() + timedelta(hours=24),
        time_to_resolution_hours=24,
        role_in_issue="assignee"
    )
    issue.story_points = 5
    issue.comments_count = 4

    from developer_skill_analyzer.analyzers.jira_analyzer import JiraAnalyzer
    analyzer = JiraAnalyzer("url", "e", "t")
    score = analyzer._calculate_issue_complexity(issue)
    assert 0.0 <= score <= 1.0
    # Expect contributions from story points, description, comments and time
    assert score > 0.3