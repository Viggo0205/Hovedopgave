"""
Developer profile models.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .skills import SkillAssessment


class DeveloperIdentity(BaseModel):
    """Represents developer identity across platforms."""
    
    github_username: Optional[str] = None
    jira_email: Optional[str] = None
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "github_username": "johndoe",
                "jira_email": "john.doe@company.com",
                "full_name": "John Doe",
                "display_name": "John D.",
                "company": "Tech Corp",
                "location": "San Francisco, CA"
            }
        }


class DeveloperMetrics(BaseModel):
    """Basic metrics about a developer."""
    
    total_commits: int = 0
    total_pull_requests: int = 0
    total_issues_created: int = 0
    total_issues_resolved: int = 0
    total_code_reviews: int = 0
    lines_of_code_added: int = 0
    lines_of_code_removed: int = 0
    repositories_contributed: int = 0
    projects_participated: int = 0
    
    # Time-based metrics
    active_days: int = 0
    first_activity_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "total_commits": 1250,
                "total_pull_requests": 89,
                "total_issues_created": 34,
                "total_issues_resolved": 127,
                "total_code_reviews": 156,
                "lines_of_code_added": 45000,
                "lines_of_code_removed": 12000,
                "repositories_contributed": 15,
                "projects_participated": 8,
                "active_days": 245,
                "first_activity_date": "2022-01-15T09:30:00Z",
                "last_activity_date": "2024-11-13T16:45:00Z"
            }
        }


class CollaborationMetrics(BaseModel):
    """Metrics related to collaboration and teamwork."""
    
    code_review_participation_rate: float = 0.0
    average_pr_review_time_hours: float = 0.0
    mentoring_activities: int = 0
    knowledge_sharing_contributions: int = 0
    cross_team_collaboration_count: int = 0
    
    # Communication quality indicators
    comment_quality_score: float = 0.0  # Based on length, clarity, helpfulness
    issue_resolution_rate: float = 0.0
    response_time_hours: float = 0.0
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "code_review_participation_rate": 0.85,
                "average_pr_review_time_hours": 4.2,
                "mentoring_activities": 12,
                "knowledge_sharing_contributions": 23,
                "cross_team_collaboration_count": 5,
                "comment_quality_score": 4.2,
                "issue_resolution_rate": 0.78,
                "response_time_hours": 6.5
            }
        }


class DeveloperProfile(BaseModel):
    """Complete developer profile with identity, metrics, and skills."""
    
    identity: DeveloperIdentity
    metrics: DeveloperMetrics
    collaboration: CollaborationMetrics
    skill_assessment: SkillAssessment
    
    # Analysis metadata
    profile_id: str = Field(..., description="Unique identifier for this profile")
    last_updated: datetime = Field(default_factory=datetime.now)
    analysis_version: str = "1.0"
    data_sources: List[str] = Field(default_factory=list)  # e.g., ["github", "jira"]
    
    # Computed fields
    experience_level: str = Field(default="Unknown")  # Beginner, Intermediate, Senior, Expert
    primary_role: str = Field(default="Unknown")  # Backend, Frontend, Full-stack, etc.
    career_stage: str = Field(default="Unknown")  # Junior, Mid-level, Senior, Lead, etc.
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "identity": {
                    "github_username": "johndoe",
                    "jira_email": "john.doe@company.com",
                    "full_name": "John Doe",
                    "company": "Tech Corp"
                },
                "profile_id": "dev_johndoe_20241113",
                "experience_level": "Senior",
                "primary_role": "Full-stack Developer",
                "career_stage": "Senior Developer",
                "data_sources": ["github", "jira"],
                "analysis_version": "1.0"
            }
        }
    
    def get_summary(self) -> Dict[str, any]:
        """Get a summary of the developer profile."""
        return {
            "name": self.identity.display_name or self.identity.full_name or "Unknown",
            "experience_level": self.experience_level,
            "primary_role": self.primary_role,
            "career_stage": self.career_stage,
            "total_commits": self.metrics.total_commits,
            "total_repositories": self.metrics.repositories_contributed,
            "collaboration_score": self.collaboration.code_review_participation_rate,
            "top_skills": self.skill_assessment.get_top_skills(limit=5),
            "skill_areas": len(self.skill_assessment.technical_skills) + len(self.skill_assessment.soft_skills),
            "last_updated": self.last_updated.isoformat()
        }
    
    def is_github_analyzed(self) -> bool:
        """Check if GitHub analysis was performed for this profile."""
        return "github" in self.data_sources
    
    def is_jira_analyzed(self) -> bool:
        """Check if Jira analysis was performed for this profile."""
        return "jira" in self.data_sources
    
    def get_activity_level(self) -> str:
        """Determine activity level based on metrics."""
        if self.metrics.active_days >= 200:
            return "Very High"
        elif self.metrics.active_days >= 100:
            return "High"
        elif self.metrics.active_days >= 50:
            return "Moderate"
        elif self.metrics.active_days >= 10:
            return "Low"
        else:
            return "Very Low"
    
    def get_collaboration_level(self) -> str:
        """Determine collaboration level based on metrics."""
        collab_score = (
            self.collaboration.code_review_participation_rate * 0.4 +
            min(self.collaboration.mentoring_activities / 10, 1.0) * 0.3 +
            min(self.collaboration.knowledge_sharing_contributions / 20, 1.0) * 0.3
        )
        
        if collab_score >= 0.8:
            return "Excellent"
        elif collab_score >= 0.6:
            return "Good"
        elif collab_score >= 0.4:
            return "Fair"
        else:
            return "Limited"