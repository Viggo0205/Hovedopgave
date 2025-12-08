"""
Standardized API response models for external data consumers.

These models define the contract for data exposed via MCP tools,
ensuring consistent structure and excluding sensitive personal information.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from .skills import SkillLevel, SkillCategory


class LanguageSkill(BaseModel):
    """Individual programming language skill assessment."""
    
    language: str
    level: SkillLevel
    lines_of_code: int = 0
    repositories_count: int = 0
    percentage_of_work: float = 0.0
    last_used: Optional[datetime] = None


class ExpertiseArea(BaseModel):
    """Developer expertise in a specific technical area."""
    
    category: str
    languages: List[str]
    proficiency: SkillLevel
    project_count: int = 0


class DeveloperProfileResponse(BaseModel):
    """
    Sanitized developer profile for external API consumption.
    
    This model contains only non-sensitive information suitable for
    data analysis and does not include any personal identifiable information.
    """
    
    username: str = Field(..., description="Developer's username (GitHub/Jira)")
    display_name: Optional[str] = Field(None, description="Public display name")
    
    # Skill assessments
    language_skills: Dict[str, LanguageSkill] = Field(
        default_factory=dict,
        description="Programming language proficiencies"
    )
    expertise_areas: Dict[str, ExpertiseArea] = Field(
        default_factory=dict,
        description="Technical expertise areas"
    )
    
    # Activity metrics
    total_repositories: int = Field(0, description="Total repositories contributed to")
    total_commits: int = Field(0, description="Total commits made")
    total_pull_requests: int = Field(0, description="Total pull requests")
    total_issues: int = Field(0, description="Total issues worked on")
    
    # Profile metadata
    account_age_days: Optional[int] = Field(None, description="Days since account creation")
    last_activity: Optional[datetime] = Field(None, description="Last recorded activity")
    
    # Analysis metadata
    analysis_date: datetime = Field(
        default_factory=datetime.now,
        description="When this analysis was performed"
    )
    data_sources: List[str] = Field(
        default_factory=list,
        description="Data sources used (github, jira, etc.)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "display_name": "John Doe",
                "language_skills": {
                    "Python": {
                        "language": "Python",
                        "level": "expert",
                        "lines_of_code": 50000,
                        "repositories_count": 15,
                        "percentage_of_work": 45.5
                    }
                },
                "total_repositories": 25,
                "total_commits": 1250,
                "analysis_date": "2025-12-08T10:30:00"
            }
        }
    )


class DeveloperComparisonResponse(BaseModel):
    """Response model for comparing two developers."""
    
    developers: Dict[str, str] = Field(
        ...,
        description="Developer usernames being compared"
    )
    individual_profiles: Dict[str, DeveloperProfileResponse] = Field(
        ...,
        description="Complete profiles for each developer"
    )
    
    comparison_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="High-level comparison metrics"
    )
    
    analysis_date: datetime = Field(default_factory=datetime.now)


class TeamAnalysisResponse(BaseModel):
    """Response model for team-wide skill analysis."""
    
    team_name: str
    member_count: int
    
    team_profiles: List[DeveloperProfileResponse] = Field(
        default_factory=list,
        description="Profiles for all team members"
    )
    
    # Aggregate team metrics
    total_languages: int = Field(0, description="Unique languages across team")
    coverage_by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="Number of team members per expertise area"
    )
    skill_gaps: List[str] = Field(
        default_factory=list,
        description="Areas where team lacks expertise"
    )
    
    analysis_date: datetime = Field(default_factory=datetime.now)


class ExportResponse(BaseModel):
    """Response model for data export operations."""
    
    success: bool
    file_path: str
    records_exported: int = 0
    file_size_bytes: Optional[int] = None
    format: str = "json"
    timestamp: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None
