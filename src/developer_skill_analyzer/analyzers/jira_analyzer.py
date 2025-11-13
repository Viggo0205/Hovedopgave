"""
Jira data analyzer for extracting developer skills and collaboration metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

from atlassian import Jira
from atlassian.rest_client import HTTPError

from ..models.analysis import JiraAnalysisResult, JiraProjectAnalysis, IssueAnalysis

logger = logging.getLogger(__name__)


class JiraAnalyzer:
    """Analyzes Jira data to extract developer skills and collaboration metrics."""
    
    def __init__(self, server_url: str, email: str, api_token: str):
        """
        Initialize the Jira analyzer.
        
        Args:
            server_url: Jira server URL
            email: User email
            api_token: Jira API token
        """
        self.jira = Jira(
            url=server_url,
            username=email,
            password=api_token,
            cloud=True
        )
        self.server_url = server_url
        self.email = email
    
    async def analyze_developer(
        self,
        email: str,
        projects: Optional[List[str]] = None,
        include_comments: bool = True,
        time_range_months: int = 6
    ) -> Dict[str, Any]:
        """
        Analyze a developer's Jira activity.
        
        Args:
            email: Developer's email address
            projects: Specific projects to analyze
            include_comments: Include comment analysis
            time_range_months: Number of months to analyze
            
        Returns:
            Analysis results dictionary
        """
        try:
            since_date = datetime.now() - timedelta(days=time_range_months * 30)
            
            logger.info(f"Analyzing Jira activity for: {email}")
            
            # Get user information
            user_info = await self._get_user_info(email)
            
            # Get projects to analyze
            projects_to_analyze = await self._get_projects_to_analyze(projects)
            
            # Analyze each project
            project_analyses = []
            for project_key in projects_to_analyze:
                try:
                    project_analysis = await self._analyze_project(
                        project_key, email, since_date, include_comments
                    )
                    if project_analysis:
                        project_analyses.append(project_analysis)
                except Exception as e:
                    logger.warning(f"Failed to analyze project {project_key}: {e}")
                    continue
            
            # Aggregate results
            result = self._aggregate_analysis_results(
                email, user_info, project_analyses, time_range_months
            )
            
            return result.dict()
            
        except HTTPError as e:
            logger.error(f"Jira API error for user {email}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing Jira user {email}: {e}")
            raise
    
    async def _get_user_info(self, email: str) -> Dict[str, Any]:
        """Get user information from Jira."""
        try:
            # Search for user by email
            users = self.jira.search_users(query=email)
            
            if users:
                user = users[0]
                return {
                    "account_id": user.get("accountId"),
                    "display_name": user.get("displayName"),
                    "email_address": user.get("emailAddress"),
                    "active": user.get("active", True),
                    "timezone": user.get("timeZone"),
                    "locale": user.get("locale")
                }
            else:
                return {
                    "email_address": email,
                    "display_name": email,
                    "active": True
                }
                
        except Exception as e:
            logger.warning(f"Could not get user info for {email}: {e}")
            return {
                "email_address": email,
                "display_name": email,
                "active": True
            }
    
    async def _get_projects_to_analyze(
        self, specific_projects: Optional[List[str]]
    ) -> List[str]:
        """Get list of projects to analyze."""
        if specific_projects:
            return specific_projects
        
        try:
            # Get all accessible projects (limited to avoid performance issues)
            projects = self.jira.projects(expand="description,lead")
            return [p["key"] for p in projects[:10]]  # Limit to first 10 projects
            
        except Exception as e:
            logger.error(f"Could not get projects list: {e}")
            return []
    
    async def _analyze_project(
        self,
        project_key: str,
        email: str,
        since_date: datetime,
        include_comments: bool
    ) -> Optional[JiraProjectAnalysis]:
        """Analyze a developer's participation in a specific project."""
        try:
            # Get project information
            project_info = self.jira.get_project(project_key)
            
            project_analysis = JiraProjectAnalysis(
                project_key=project_key,
                project_name=project_info.get("name", project_key)
            )
            
            # Get issues created by the user
            created_issues = await self._get_issues_created_by_user(
                project_key, email, since_date
            )
            project_analysis.issues_created = created_issues
            
            # Get issues assigned to the user
            assigned_issues = await self._get_issues_assigned_to_user(
                project_key, email, since_date
            )
            project_analysis.issues_assigned = assigned_issues
            
            # Get issues commented on by the user (if requested)
            if include_comments:
                commented_issues = await self._get_issues_commented_by_user(
                    project_key, email, since_date
                )
                project_analysis.issues_commented = commented_issues
            
            # Calculate project metrics
            self._calculate_project_metrics(project_analysis)
            
            return project_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing project {project_key}: {e}")
            return None
    
    async def _get_issues_created_by_user(
        self, project_key: str, email: str, since_date: datetime
    ) -> List[IssueAnalysis]:
        """Get issues created by the user in the project."""
        issues = []
        
        try:
            # JQL query for issues created by user
            jql = f'project = "{project_key}" AND reporter = "{email}" AND created >= "{since_date.strftime("%Y-%m-%d")}"'
            
            search_result = self.jira.jql(jql, limit=50)  # Limit results
            
            for issue_data in search_result["issues"]:
                issue_analysis = await self._analyze_issue(issue_data, "creator")
                if issue_analysis:
                    issues.append(issue_analysis)
                    
        except Exception as e:
            logger.warning(f"Could not get created issues for {project_key}: {e}")
        
        return issues
    
    async def _get_issues_assigned_to_user(
        self, project_key: str, email: str, since_date: datetime
    ) -> List[IssueAnalysis]:
        """Get issues assigned to the user in the project."""
        issues = []
        
        try:
            # JQL query for issues assigned to user
            jql = f'project = "{project_key}" AND assignee = "{email}" AND updated >= "{since_date.strftime("%Y-%m-%d")}"'
            
            search_result = self.jira.jql(jql, limit=50)  # Limit results
            
            for issue_data in search_result["issues"]:
                issue_analysis = await self._analyze_issue(issue_data, "assignee")
                if issue_analysis:
                    issues.append(issue_analysis)
                    
        except Exception as e:
            logger.warning(f"Could not get assigned issues for {project_key}: {e}")
        
        return issues
    
    async def _get_issues_commented_by_user(
        self, project_key: str, email: str, since_date: datetime
    ) -> List[IssueAnalysis]:
        """Get issues where the user has commented."""
        issues = []
        
        try:
            # This is more complex as we need to search through comments
            # For now, we'll use a simplified approach
            jql = f'project = "{project_key}" AND updated >= "{since_date.strftime("%Y-%m-%d")}"'
            
            search_result = self.jira.jql(jql, limit=30)  # Limited search
            
            for issue_data in search_result["issues"]:
                # Check if user has commented on this issue
                try:
                    comments = self.jira.get_issue_comments(issue_data["key"])
                    user_commented = any(
                        comment["author"]["emailAddress"] == email 
                        for comment in comments["comments"]
                        if "author" in comment and "emailAddress" in comment["author"]
                    )
                    
                    if user_commented:
                        issue_analysis = await self._analyze_issue(issue_data, "collaborator")
                        if issue_analysis:
                            issues.append(issue_analysis)
                            
                except Exception:
                    continue  # Skip issues we can't access
                    
        except Exception as e:
            logger.warning(f"Could not get commented issues for {project_key}: {e}")
        
        return issues
    
    async def _analyze_issue(
        self, issue_data: Dict[str, Any], role: str
    ) -> Optional[IssueAnalysis]:
        """Analyze a single Jira issue."""
        try:
            fields = issue_data["fields"]
            
            # Parse dates
            created_date = datetime.fromisoformat(
                fields["created"].replace("Z", "+00:00")
            )
            
            resolved_date = None
            time_to_resolution = None
            if fields.get("resolutiondate"):
                resolved_date = datetime.fromisoformat(
                    fields["resolutiondate"].replace("Z", "+00:00")
                )
                time_to_resolution = (resolved_date - created_date).total_seconds() / 3600
            
            # Extract issue details
            issue_analysis = IssueAnalysis(
                key=issue_data["key"],
                issue_type=fields["issuetype"]["name"],
                status=fields["status"]["name"],
                priority=fields.get("priority", {}).get("name", "Unknown"),
                summary=fields["summary"],
                description_length=len(fields.get("description", "") or ""),
                created_date=created_date,
                resolved_date=resolved_date,
                time_to_resolution_hours=time_to_resolution,
                role_in_issue=role
            )
            
            # Extract story points if available
            if "customfield_10004" in fields and fields["customfield_10004"]:
                issue_analysis.story_points = int(fields["customfield_10004"])
            
            # Get comment count
            try:
                comments = self.jira.get_issue_comments(issue_data["key"])
                issue_analysis.comments_count = len(comments["comments"])
            except Exception:
                pass
            
            # Extract skills and technologies from issue content
            issue_analysis.skills_demonstrated = self._extract_skills_from_issue(
                fields.get("summary", ""), 
                fields.get("description", "")
            )
            
            issue_analysis.technologies_mentioned = self._extract_technologies_from_issue(
                fields.get("summary", ""),
                fields.get("description", "")
            )
            
            # Calculate complexity score
            issue_analysis.complexity_score = self._calculate_issue_complexity(
                issue_analysis
            )
            
            return issue_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing issue {issue_data.get('key', 'unknown')}: {e}")
            return None
    
    def _extract_skills_from_issue(self, summary: str, description: str) -> List[str]:
        """Extract demonstrated skills from issue text."""
        text = f"{summary} {description or ''}".lower()
        skills = []
        
        # Programming skills
        programming_patterns = {
            "api development": ["api", "rest", "endpoint", "service"],
            "database": ["database", "sql", "query", "schema"],
            "frontend": ["ui", "ux", "frontend", "interface"],
            "backend": ["backend", "server", "service"],
            "testing": ["test", "testing", "unit test", "integration"],
            "debugging": ["bug", "fix", "debug", "error", "issue"],
            "performance": ["performance", "optimization", "speed", "memory"],
            "security": ["security", "authentication", "authorization"],
            "documentation": ["documentation", "docs", "readme"],
        }
        
        for skill, patterns in programming_patterns.items():
            if any(pattern in text for pattern in patterns):
                skills.append(skill)
        
        return skills
    
    def _extract_technologies_from_issue(self, summary: str, description: str) -> List[str]:
        """Extract mentioned technologies from issue text."""
        text = f"{summary} {description or ''}".lower()
        technologies = []
        
        # Common technologies
        tech_patterns = [
            "java", "python", "javascript", "react", "angular", "vue",
            "spring", "django", "flask", "node.js", "express",
            "mysql", "postgresql", "mongodb", "redis",
            "docker", "kubernetes", "aws", "azure", "gcp",
            "jenkins", "gitlab", "github", "jira"
        ]
        
        for tech in tech_patterns:
            if tech in text:
                technologies.append(tech)
        
        return technologies
    
    def _calculate_issue_complexity(self, issue: IssueAnalysis) -> float:
        """Calculate complexity score for an issue."""
        complexity = 0.0
        
        # Story points contribution
        if issue.story_points:
            complexity += min(issue.story_points / 8.0, 1.0) * 0.4
        
        # Description length (more detailed = more complex)
        if issue.description_length > 0:
            desc_score = min(issue.description_length / 500.0, 1.0)
            complexity += desc_score * 0.2
        
        # Number of comments (more discussion = more complex)
        comment_score = min(issue.comments_count / 10.0, 1.0)
        complexity += comment_score * 0.2
        
        # Time to resolution (longer = more complex)
        if issue.time_to_resolution_hours:
            time_score = min(issue.time_to_resolution_hours / 40.0, 1.0)  # 40 hours as baseline
            complexity += time_score * 0.2
        
        return min(complexity, 1.0)
    
    def _calculate_project_metrics(self, project: JiraProjectAnalysis) -> None:
        """Calculate metrics for a project analysis."""
        all_issues = project.issues_created + project.issues_assigned + project.issues_commented
        project.total_issues_involved = len(set(issue.key for issue in all_issues))
        
        # Calculate average resolution time
        resolved_issues = [i for i in all_issues if i.time_to_resolution_hours is not None]
        if resolved_issues:
            project.average_resolution_time_hours = sum(
                i.time_to_resolution_hours for i in resolved_issues
            ) / len(resolved_issues)
        
        # Count issue types and priorities
        project.issue_types_handled = Counter(issue.issue_type for issue in all_issues)
        project.priorities_handled = Counter(issue.priority for issue in all_issues)
        
        # Determine primary role based on activity
        created_count = len(project.issues_created)
        assigned_count = len(project.issues_assigned)
        commented_count = len(project.issues_commented)
        
        if created_count > assigned_count:
            project.primary_role = "analyst"
        elif assigned_count > 0:
            project.primary_role = "developer"
        elif commented_count > 0:
            project.primary_role = "reviewer"
        else:
            project.primary_role = "observer"
        
        # Extract specialization areas
        all_skills = []
        for issue in all_issues:
            all_skills.extend(issue.skills_demonstrated)
        
        skill_counts = Counter(all_skills)
        project.specialization_areas = [
            skill for skill, count in skill_counts.most_common(5)
        ]
        
        # Calculate collaboration score
        project.collaboration_score = min(
            (commented_count + created_count * 0.5) / max(assigned_count, 1), 2.0
        ) / 2.0
    
    def _aggregate_analysis_results(
        self,
        email: str,
        user_info: Dict[str, Any],
        project_analyses: List[JiraProjectAnalysis],
        time_range_months: int
    ) -> JiraAnalysisResult:
        """Aggregate all analysis results."""
        
        result = JiraAnalysisResult(
            email=email,
            display_name=user_info.get("display_name"),
            projects=project_analyses,
            time_range_analyzed=time_range_months
        )
        
        result.total_projects = len(project_analyses)
        
        # Aggregate issue metrics
        for project in project_analyses:
            result.total_issues_created += len(project.issues_created)
            result.total_issues_assigned += len(project.issues_assigned)
            result.total_comments += sum(
                issue.comments_count for issue in 
                project.issues_created + project.issues_assigned + project.issues_commented
            )
        
        # Calculate performance metrics
        all_assigned_issues = []
        for project in project_analyses:
            all_assigned_issues.extend(project.issues_assigned)
        
        if all_assigned_issues:
            resolved_assigned = [i for i in all_assigned_issues if i.resolved_date]
            result.total_issues_resolved = len(resolved_assigned)
            result.resolution_rate = len(resolved_assigned) / len(all_assigned_issues)
            
            if resolved_assigned:
                result.average_resolution_time_hours = sum(
                    i.time_to_resolution_hours for i in resolved_assigned
                    if i.time_to_resolution_hours
                ) / len([i for i in resolved_assigned if i.time_to_resolution_hours])
        
        # Aggregate technical areas
        technical_areas = defaultdict(int)
        for project in project_analyses:
            for area in project.specialization_areas:
                technical_areas[area] += 1
        
        result.technical_areas = dict(technical_areas)
        
        # Calculate quality scores
        result.comment_quality_score = self._calculate_comment_quality_score(project_analyses)
        result.collaboration_frequency = sum(p.collaboration_score for p in project_analyses) / max(len(project_analyses), 1)
        
        return result
    
    def _calculate_comment_quality_score(self, projects: List[JiraProjectAnalysis]) -> float:
        """Calculate a score for comment quality based on engagement."""
        if not projects:
            return 0.0
        
        total_comments = sum(
            sum(issue.comments_count for issue in project.issues_commented)
            for project in projects
        )
        
        total_issues_engaged = sum(len(project.issues_commented) for project in projects)
        
        if total_issues_engaged == 0:
            return 0.0
        
        # Average comments per engaged issue
        avg_comments = total_comments / total_issues_engaged
        return min(avg_comments / 3.0, 1.0)  # Normalize with 3 comments as "good"