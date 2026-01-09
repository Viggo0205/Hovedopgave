# tests/test_issue_analysis_async.py
import pytest
import asyncio
from unittest.mock import MagicMock
from freezegun import freeze_time
from datetime import datetime, timedelta

import pytest_asyncio
from developer_skill_analyzer.analyzers.jira_analyzer import JiraAnalyzer
from developer_skill_analyzer.models.analysis import IssueAnalysis

@pytest_asyncio.fixture
async def analyzer_with_mock_jira():
    a = JiraAnalyzer("https://example.atlassian.net", "me@example.com", "token")
    # Replace a.jira with a MagicMock that has required methods
    mock_jira = MagicMock()
    # Simulate jql returning one issue
    issue_fields = {
        "created": "2025-01-01T10:00:00.000+00:00",
        "issuetype": {"name": "Task"},
        "status": {"name": "Done"},
        "summary": "Implement feature X in Django",
        "description": "Use Django, PostgreSQL and docker. Add tests.",
        # some Jira instances use custom story-points field - emulate it missing or present
        "customfield_10004": 3,
        "resolutiondate": "2025-01-03T12:00:00.000+00:00",
        "priority": {"name": "Medium"},
    }
    mock_issue = {"key": "PROJ-1", "fields": issue_fields}
    mock_jira.jql.return_value = {"issues": [mock_issue]}
    # comments for the issue
    mock_jira.get_issue_comments.return_value = {"comments": [{"author": {"emailAddress": "me@example.com"}}]}
    mock_jira.search_users.return_value = [{"accountId": "123", "displayName": "Me", "emailAddress": "me@example.com"}]
    mock_jira.projects.return_value = [{"key": "PROJ", "name": "Project"}]
    mock_jira.get_project.return_value = {"name": "Project"}
    a.jira = mock_jira
    return a

@pytest.mark.asyncio
async def test_get_issues_created_by_user_and_analyze(analyzer_with_mock_jira):
    a = analyzer_with_mock_jira
    since_date = datetime.utcnow() - timedelta(days=365)
    issues = await a._get_issues_created_by_user("PROJ", "me@example.com", since_date)
    assert len(issues) == 1
    ia = issues[0]
    assert ia.key == "PROJ-1"
    assert "django" in ia.technologies_mentioned or "postgresql" in ia.technologies_mentioned

@pytest.mark.asyncio
async def test_analyze_developer_end_to_end(analyzer_with_mock_jira):
    a = analyzer_with_mock_jira
    result = await a.analyze_developer("me@example.com", projects=["PROJ"], include_comments=True, time_range_months=12)
    # result is a dict via result.dict() earlier in analyze_developer
    assert result["email"] == "me@example.com"
    assert result["total_projects"] >= 0
    # keys expected in JiraAnalysisResult
    assert "technical_areas" in result
