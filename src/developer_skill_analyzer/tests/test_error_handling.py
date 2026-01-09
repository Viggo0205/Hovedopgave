# tests/test_error_handling.py
import pytest
from unittest.mock import MagicMock
from atlassian.errors import ApiError as HTTPError
from  developer_skill_analyzer.analyzers.jira_analyzer import JiraAnalyzer

def test_get_projects_handles_error():
    a = JiraAnalyzer("url", "e", "t")
    mock_jira = MagicMock()
    mock_jira.projects.side_effect = Exception("Connection failed")
    a.jira = mock_jira

    # call the coroutine via asyncio (method is async)
    import asyncio
    projects = asyncio.run(a._get_projects_to_analyze(None))
    assert projects == []