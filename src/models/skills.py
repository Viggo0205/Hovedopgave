"""
Skill-related models and data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class SkillLevel(str, Enum):
    """Enumeration of skill proficiency levels."""
    
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    
    def get_numeric_value(self) -> int:
        """Get numeric representation of skill level."""
        mapping = {
            self.BEGINNER: 1,
            self.INTERMEDIATE: 2,
            self.ADVANCED: 3,
            self.EXPERT: 4
        }
        return mapping[self]
    
    @classmethod
    def from_score(cls, score: float) -> "SkillLevel":
        """Convert a numeric score (0-1) to skill level."""
        if score >= 0.8:
            return cls.EXPERT
        elif score >= 0.6:
            return cls.ADVANCED
        elif score >= 0.3:
            return cls.INTERMEDIATE
        else:
            return cls.BEGINNER
    
    @classmethod
    def from_confidence(cls, confidence: float) -> "SkillLevel":
        """Convert a confidence score (0-1) to skill level."""
        return cls.from_score(confidence)


class SkillCategory(str, Enum):
    """Categories of skills that can be analyzed."""
    
    # Technical Skills
    TECHNICAL = "technical"
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    DATABASE = "database"
    CLOUD_PLATFORM = "cloud_platform"
    METHODOLOGY = "methodology"
    ARCHITECTURE = "architecture"
    
    # Soft Skills
    SOFT_SKILL = "soft_skill"
    COMMUNICATION = "communication"
    LEADERSHIP = "leadership"
    PROBLEM_SOLVING = "problem_solving"
    COLLABORATION = "collaboration"
    MENTORING = "mentoring"
    PROJECT_MANAGEMENT = "project_management"
    
    # Domain Knowledge
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    DEVOPS = "devops"
    SECURITY = "security"
    TESTING = "testing"
    UI_UX = "ui_ux"


class SkillEvidence(BaseModel):
    """Evidence supporting a skill assessment."""
    
    source: str  # e.g., "github_commits", "jira_issues", "code_reviews"
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    frequency: int = 0  # How often this evidence appears
    recency: datetime  # When this evidence was last observed
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source": "github_commits",
                "description": "Used Python in 45 commits across 8 repositories",
                "confidence": 0.95,
                "frequency": 45,
                "recency": "2024-11-13T10:30:00Z"
            }
        }
    )


class Skill(BaseModel):
    """Represents a specific skill with proficiency assessment."""
    
    name: str
    category: SkillCategory
    level: SkillLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Additional metrics
    usage_frequency: int = 0  # How often this skill is used
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    trend: str = "stable"  # "growing", "stable", "declining"
    
    # Supporting evidence
    evidence: List[SkillEvidence] = Field(default_factory=list)
    related_skills: List[str] = Field(default_factory=list)
    
    # Context information
    projects_used_in: List[str] = Field(default_factory=list)
    complexity_level: str = "medium"  # "low", "medium", "high"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Python",
                "category": "programming_language",
                "level": "advanced",
                "confidence_score": 0.9,
                "usage_frequency": 156,
                "trend": "growing",
                "complexity_level": "high",
                "projects_used_in": ["api-service", "data-pipeline", "ml-model"]
            }
        }
    )
    
    def add_evidence(self, evidence: SkillEvidence) -> None:
        """Add evidence supporting this skill."""
        self.evidence.append(evidence)
        # Update metrics based on evidence
        if evidence.recency:
            if not self.last_observed or evidence.recency > self.last_observed:
                self.last_observed = evidence.recency
            if not self.first_observed or evidence.recency < self.first_observed:
                self.first_observed = evidence.recency
    
    def get_experience_months(self) -> int:
        """Calculate experience in months for this skill."""
        if not self.first_observed or not self.last_observed:
            return 0
        
        delta = self.last_observed - self.first_observed
        return max(1, int(delta.days / 30))
    
    def get_activity_score(self) -> float:
        """Calculate activity score based on usage and recency."""
        base_score = min(self.usage_frequency / 100.0, 1.0)  # Normalize frequency
        
        # Apply recency boost
        if self.last_observed:
            days_since = (datetime.now() - self.last_observed).days
            recency_factor = max(0.1, 1.0 - (days_since / 365))  # Decay over a year
            return base_score * recency_factor
        
        return base_score


class SkillGroup(BaseModel):
    """A group of related skills."""
    
    name: str
    category: SkillCategory
    skills: List[Skill]
    group_confidence: float = Field(ge=0.0, le=1.0)
    
    def get_average_level(self) -> float:
        """Get average skill level in this group."""
        if not self.skills:
            return 0.0
        
        total = sum(skill.level.get_numeric_value() for skill in self.skills)
        return total / len(self.skills)
    
    def get_strongest_skill(self) -> Optional[Skill]:
        """Get the strongest skill in this group."""
        if not self.skills:
            return None
        
        return max(self.skills, key=lambda s: s.confidence_score * s.level.get_numeric_value())


class SkillGap(BaseModel):
    """Represents a gap in skills or areas for improvement."""
    
    skill_name: str
    category: SkillCategory
    importance: str = "medium"  # "low", "medium", "high", "critical"
    current_level: SkillLevel = SkillLevel.BEGINNER
    target_level: SkillLevel
    
    # Learning recommendations
    learning_resources: List[str] = Field(default_factory=list)
    estimated_learning_time_weeks: Optional[int] = None
    prerequisites: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skill_name": "Kubernetes",
                "category": "tool",
                "importance": "high",
                "current_level": "beginner",
                "target_level": "intermediate",
                "estimated_learning_time_weeks": 8,
                "prerequisites": ["Docker", "Container orchestration basics"]
            }
        }
    )


class SkillAssessment(BaseModel):
    """Complete skill assessment for a developer."""
    
    # Core skill groups
    technical_skills: List[Skill] = Field(default_factory=list)
    soft_skills: List[Skill] = Field(default_factory=list)
    domain_skills: List[Skill] = Field(default_factory=list)
    
    # Skill groups for organization
    skill_groups: List[SkillGroup] = Field(default_factory=list)
    
    # Analysis metadata
    assessment_date: datetime = Field(default_factory=datetime.now)
    analysis_confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Insights and recommendations
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    career_recommendations: List[str] = Field(default_factory=list)
    
    # Summary statistics
    total_skills_identified: int = 0
    primary_specialization: Optional[str] = None
    experience_breadth_score: float = 0.0
    experience_depth_score: float = 0.0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_skills_identified": 23,
                "primary_specialization": "Backend Development",
                "experience_breadth_score": 0.75,
                "experience_depth_score": 0.85,
                "analysis_confidence": 0.9,
                "data_quality_score": 0.88
            }
        }
    )
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the appropriate category."""
        if skill.category in [
            SkillCategory.PROGRAMMING_LANGUAGE,
            SkillCategory.FRAMEWORK,
            SkillCategory.TOOL,
            SkillCategory.DATABASE,
            SkillCategory.CLOUD_PLATFORM,
            SkillCategory.METHODOLOGY,
            SkillCategory.ARCHITECTURE
        ]:
            self.technical_skills.append(skill)
        elif skill.category in [
            SkillCategory.COMMUNICATION,
            SkillCategory.LEADERSHIP,
            SkillCategory.PROBLEM_SOLVING,
            SkillCategory.COLLABORATION,
            SkillCategory.MENTORING,
            SkillCategory.PROJECT_MANAGEMENT
        ]:
            self.soft_skills.append(skill)
        else:
            self.domain_skills.append(skill)
        
        self.total_skills_identified = len(self.get_all_skills())
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills across all categories."""
        return self.technical_skills + self.soft_skills + self.domain_skills
    
    def get_top_skills(self, limit: int = 10) -> List[Skill]:
        """Get top skills by confidence and level."""
        all_skills = self.get_all_skills()
        return sorted(
            all_skills,
            key=lambda s: s.confidence_score * s.level.get_numeric_value(),
            reverse=True
        )[:limit]
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a specific category."""
        return [skill for skill in self.get_all_skills() if skill.category == category]
    
    def calculate_specialization_score(self) -> Dict[str, float]:
        """Calculate specialization scores for different areas."""
        category_scores = {}
        
        for category in SkillCategory:
            skills = self.get_skills_by_category(category)
            if skills:
                avg_score = sum(
                    s.confidence_score * s.level.get_numeric_value() 
                    for s in skills
                ) / len(skills)
                category_scores[category.value] = avg_score
        
        return category_scores
    
    def identify_primary_specialization(self) -> str:
        """Identify the primary area of specialization."""
        scores = self.calculate_specialization_score()
        if scores:
            primary = max(scores.items(), key=lambda x: x[1])
            return primary[0].replace("_", " ").title()
        return "General Development"
    
    def get_learning_recommendations(self) -> List[str]:
        """Generate learning recommendations based on skill gaps."""
        recommendations = []
        
        # High-importance skill gaps
        critical_gaps = [gap for gap in self.skill_gaps if gap.importance == "critical"]
        for gap in critical_gaps[:3]:  # Top 3 critical gaps
            recommendations.append(
                f"Priority: Learn {gap.skill_name} to reach {gap.target_level.value} level"
            )
        
        # Growth opportunities
        for area in self.growth_areas[:2]:  # Top 2 growth areas
            recommendations.append(f"Expand knowledge in {area}")
        
        return recommendations