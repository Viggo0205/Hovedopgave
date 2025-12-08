"""
Analysis result models for GitHub and Jira data processing.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from models.skills import SkillAssessment


class RepositoryAnalysis(BaseModel):
    """Analysis results for a single repository."""
    
    name: str
    url: str
    description: Optional[str] = None
    primary_language: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)  # Language -> lines of code
    
    # Contribution metrics
    commits_count: int = 0
    additions: int = 0
    deletions: int = 0
    pull_requests: int = 0
    issues_created: int = 0
    issues_resolved: int = 0
    
    # Repository characteristics
    stars: int = 0
    forks: int = 0
    size_kb: int = 0
    topics: List[str] = Field(default_factory=list)
    
    # Time information
    first_contribution: Optional[datetime] = None
    last_contribution: Optional[datetime] = None
    
    # Analysis insights
    complexity_score: float = 0.0  # Based on code patterns, architecture
    collaboration_level: str = "low"  # "low", "medium", "high"
    role_in_project: str = "contributor"  # "owner", "maintainer", "contributor", "occasional"


class GitHubAnalysisResult(BaseModel):
    """Complete GitHub analysis results for a developer."""
    
    username: str
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Repository analysis
    repositories: List[RepositoryAnalysis] = Field(default_factory=list)
    total_repositories: int = 0
    owned_repositories: int = 0
    contributed_repositories: int = 0
    
    # Overall metrics
    total_commits: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    total_pull_requests: int = 0
    total_issues: int = 0
    total_stars_earned: int = 0
    
    # Language analysis
    primary_languages: List[str] = Field(default_factory=list)
    language_distribution: Dict[str, float] = Field(default_factory=dict)
    language_trends: Dict[str, str] = Field(default_factory=dict)  # Language -> "growing"/"stable"/"declining"
    
    # Activity patterns
    commit_frequency: Dict[str, int] = Field(default_factory=dict)  # Day/month -> count
    active_hours: List[int] = Field(default_factory=list)  # Hours of day when active
    consistency_score: float = 0.0  # How consistent is the activity
    
    # Collaboration insights
    code_review_participation: int = 0
    mentoring_activities: int = 0
    open_source_contributions: int = 0
    cross_project_collaboration: int = 0
    
    # Technical insights
    framework_usage: Dict[str, int] = Field(default_factory=dict)
    tool_usage: Dict[str, int] = Field(default_factory=dict)
    testing_patterns: Dict[str, int] = Field(default_factory=dict)
    documentation_score: float = 0.0
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.now)
    time_range_analyzed: int = 12  # months
    data_completeness: float = 1.0
    rate_limit_encountered: bool = False
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get a summary of GitHub activity."""
        return {
            "total_contributions": self.total_commits + self.total_pull_requests + self.total_issues,
            "repository_count": self.total_repositories,
            "primary_language": self.primary_languages[0] if self.primary_languages else "Unknown",
            "collaboration_level": self.get_collaboration_level(),
            "consistency": self.consistency_score,
            "analysis_period_months": self.time_range_analyzed
        }
    
    def get_collaboration_level(self) -> str:
        """Determine collaboration level based on metrics."""
        collab_score = (
            self.code_review_participation +
            self.cross_project_collaboration +
            self.open_source_contributions
        )
        
        if collab_score >= 50:
            return "High"
        elif collab_score >= 20:
            return "Medium"
        else:
            return "Low"


class IssueAnalysis(BaseModel):
    """Analysis of a Jira issue."""
    
    key: str
    issue_type: str
    status: str
    priority: str
    summary: str
    description_length: int = 0
    
    # Time metrics
    created_date: datetime
    resolved_date: Optional[datetime] = None
    time_to_resolution_hours: Optional[float] = None
    
    # Complexity indicators
    story_points: Optional[int] = None
    complexity_score: float = 0.0  # Estimated based on description, comments, etc.
    technical_complexity: str = "medium"  # "low", "medium", "high"
    
    # Collaboration metrics
    comments_count: int = 0
    watchers_count: int = 0
    assignee_changes: int = 0
    
    # Skills demonstrated
    skills_demonstrated: List[str] = Field(default_factory=list)
    technologies_mentioned: List[str] = Field(default_factory=list)
    
    # Role indicators
    role_in_issue: str = "assignee"  # "creator", "assignee", "reviewer", "collaborator"


class JiraProjectAnalysis(BaseModel):
    """Analysis of participation in a Jira project."""
    
    project_key: str
    project_name: str
    
    # Issue participation
    issues_created: List[IssueAnalysis] = Field(default_factory=list)
    issues_assigned: List[IssueAnalysis] = Field(default_factory=list)
    issues_commented: List[IssueAnalysis] = Field(default_factory=list)
    
    # Metrics
    total_issues_involved: int = 0
    average_resolution_time_hours: float = 0.0
    issue_types_handled: Dict[str, int] = Field(default_factory=dict)
    priorities_handled: Dict[str, int] = Field(default_factory=dict)
    
    # Role and contribution patterns
    primary_role: str = "developer"  # "developer", "tester", "analyst", "lead"
    specialization_areas: List[str] = Field(default_factory=list)
    collaboration_score: float = 0.0


class JiraAnalysisResult(BaseModel):
    """Complete Jira analysis results for a developer."""
    
    email: str
    display_name: Optional[str] = None
    
    # Project participation
    projects: List[JiraProjectAnalysis] = Field(default_factory=list)
    total_projects: int = 0
    
    # Overall issue metrics
    total_issues_created: int = 0
    total_issues_assigned: int = 0
    total_issues_resolved: int = 0
    total_comments: int = 0
    
    # Performance metrics
    average_resolution_time_hours: float = 0.0
    resolution_rate: float = 0.0  # Percentage of assigned issues resolved
    issue_quality_score: float = 0.0  # Based on clarity, completeness
    
    # Communication analysis
    comment_quality_score: float = 0.0
    collaboration_frequency: float = 0.0
    knowledge_sharing_score: float = 0.0
    
    # Skill indicators
    technical_areas: Dict[str, int] = Field(default_factory=dict)  # Area -> involvement count
    business_domains: Dict[str, int] = Field(default_factory=dict)
    problem_complexity_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Growth indicators
    skill_progression: Dict[str, List[float]] = Field(default_factory=dict)  # Skill -> scores over time
    responsibility_growth: List[str] = Field(default_factory=list)
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.now)
    time_range_analyzed: int = 6  # months
    data_completeness: float = 1.0
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get a summary of Jira activity."""
        return {
            "total_issues": self.total_issues_created + self.total_issues_assigned,
            "project_count": self.total_projects,
            "resolution_rate": self.resolution_rate,
            "avg_resolution_time": self.average_resolution_time_hours,
            "collaboration_score": self.collaboration_frequency,
            "analysis_period_months": self.time_range_analyzed
        }


class AnalysisResult(BaseModel):
    """Combined analysis result from multiple sources."""
    
    developer_id: str
    
    # Source-specific results
    github_analysis: Optional[GitHubAnalysisResult] = None
    jira_analysis: Optional[JiraAnalysisResult] = None
    
    # Combined skill assessment
    combined_skill_assessment: Optional[SkillAssessment] = None
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.now)
    sources_analyzed: List[str] = Field(default_factory=list)
    analysis_completeness: float = 1.0
    confidence_score: float = 0.0
    
    # Executive summary
    summary: Dict[str, Any] = Field(default_factory=dict)
    key_strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    career_recommendations: List[str] = Field(default_factory=list)
    
    def has_github_data(self) -> bool:
        """Check if GitHub analysis data is available."""
        return self.github_analysis is not None
    
    def has_jira_data(self) -> bool:
        """Check if Jira analysis data is available."""
        return self.jira_analysis is not None
    
    def get_overall_activity_score(self) -> float:
        """Calculate overall activity score across all sources."""
        scores = []
        
        if self.github_analysis:
            github_score = min(self.github_analysis.total_commits / 100, 1.0)
            scores.append(github_score)
        
        if self.jira_analysis:
            jira_score = min(self.jira_analysis.total_issues_resolved / 50, 1.0)
            scores.append(jira_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate an executive summary of the analysis."""
        summary = {
            "developer_id": self.developer_id,
            "analysis_date": self.analysis_date.isoformat(),
            "data_sources": self.sources_analyzed,
            "overall_confidence": self.confidence_score,
            "activity_score": self.get_overall_activity_score()
        }
        
        if self.combined_skill_assessment:
            summary.update({
                "total_skills_identified": self.combined_skill_assessment.total_skills_identified,
                "primary_specialization": self.combined_skill_assessment.primary_specialization,
                "top_skills": [skill.name for skill in self.combined_skill_assessment.get_top_skills(5)]
            })
        
        return summary