"""Jira service for raw data fetching from Jira API."""

from typing import Dict, Any, List
from atlassian import Jira
from config import Config


class JiraService:
    """Service for fetching raw data from Jira API."""
    
    def __init__(self):
        self.config = Config()
        jira_token = self.config.jira_api_token
        jira_email = self.config.jira_email
        jira_url = self.config.jira_server_url
        
        # Initialize Jira client
        self.jira = Jira(
            url=jira_url,
            username=jira_email,
            password=jira_token,
            cloud=True
        )
    
    def get_user_profile(self, user_email: str) -> Dict[str, Any]:
        """Get raw user profile data from Jira."""
        try:
            user = self.jira.user(user_email)
            return {
                "email": user_email,
                "display_name": user.get("displayName"),
                "account_id": user.get("accountId"),
                "account_type": user.get("accountType"),
                "active": user.get("active", True)
            }
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return {
                "email": user_email,
                "display_name": "Unknown User",
                "account_id": None,
                "account_type": "atlassian",
                "active": False
            }
    
    def get_user_issues(self, user_email: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get raw issue data for a user."""
        try:
            # JQL query to find issues assigned to or reported by user
            jql = f'assignee = "{user_email}" OR reporter = "{user_email}" ORDER BY created DESC'
            
            issues = self.jira.jql(jql, limit=limit)
            issue_list = []
            
            for issue_data in issues.get("issues", []):
                issue = {
                    "key": issue_data.get("key"),
                    "summary": issue_data.get("fields", {}).get("summary"),
                    "description": issue_data.get("fields", {}).get("description"),
                    "issue_type": issue_data.get("fields", {}).get("issuetype", {}).get("name"),
                    "status": issue_data.get("fields", {}).get("status", {}).get("name"),
                    "priority": issue_data.get("fields", {}).get("priority", {}).get("name"),
                    "project_key": issue_data.get("fields", {}).get("project", {}).get("key"),
                    "created": issue_data.get("fields", {}).get("created"),
                    "updated": issue_data.get("fields", {}).get("updated"),
                    "assignee": issue_data.get("fields", {}).get("assignee", {}).get("emailAddress") if issue_data.get("fields", {}).get("assignee") else None,
                    "reporter": issue_data.get("fields", {}).get("reporter", {}).get("emailAddress") if issue_data.get("fields", {}).get("reporter") else None
                }
                issue_list.append(issue)
            
            return issue_list
            
        except Exception as e:
            print(f"Error fetching user issues: {e}")
            return []
    
    def get_user_projects(self, user_email: str) -> List[Dict[str, Any]]:
        """Get raw project data where user has activity."""
        try:
            # Get issues to determine which projects user is involved in
            user_issues = self.get_user_issues(user_email, limit=200)
            
            # Extract unique project keys
            project_keys = set()
            for issue in user_issues:
                if issue.get("project_key"):
                    project_keys.add(issue["project_key"])
            
            # Get project details for each project
            projects = []
            for project_key in project_keys:
                try:
                    project = self.jira.project(project_key)
                    project_data = {
                        "key": project.get("key"),
                        "name": project.get("name"),
                        "description": project.get("description"),
                        "project_type": project.get("projectTypeKey"),
                        "lead": project.get("lead", {}).get("emailAddress") if project.get("lead") else None
                    }
                    projects.append(project_data)
                except Exception:
                    # If can't access project details, add basic info
                    projects.append({
                        "key": project_key,
                        "name": project_key,
                        "description": None,
                        "project_type": "unknown",
                        "lead": None
                    })
            
            return projects
            
        except Exception as e:
            print(f"Error fetching user projects: {e}")
            return []
    
