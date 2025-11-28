"""
Competence level calculation models and configuration.

This module implements configurable calculation models for determining
skill/competence levels based on activity data and frequency patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, ConfigDict
import json

logger = logging.getLogger(__name__)


class CompetenceMetric(str, Enum):
    """Types of metrics used for competence calculation."""
    
    FREQUENCY = "frequency"              # How often skill is used
    VOLUME = "volume"                   # Total amount/size of work
    CONSISTENCY = "consistency"         # Regular usage over time
    RECENCY = "recency"                # How recently used
    COMPLEXITY = "complexity"          # Complexity of work done
    COLLABORATION = "collaboration"    # Team/collaborative usage
    INNOVATION = "innovation"          # Novel/creative usage
    QUALITY = "quality"               # Quality indicators


@dataclass
class CompetenceData:
    """Raw data for competence calculation."""
    
    skill_name: str
    frequency: int = 0                 # Number of uses/occurrences
    volume: float = 0.0               # Total size/amount (bytes, hours, etc.)
    consistency_score: float = 0.0    # 0-1 score for consistency over time
    recency_days: int = 0             # Days since last use
    complexity_score: float = 0.0     # 0-1 score for complexity
    collaboration_score: float = 0.0  # 0-1 score for collaborative work
    quality_score: float = 0.0        # 0-1 score for quality indicators
    time_span_months: int = 0          # Total months of experience
    
    # Additional context
    projects: List[str] = None
    evidence_sources: List[str] = None
    
    def __post_init__(self):
        if self.projects is None:
            self.projects = []
        if self.evidence_sources is None:
            self.evidence_sources = []


class CompetenceLevel(str, Enum):
    """Competence levels with clear definitions."""
    
    NONE = "none"
    BASIC = "basic"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"
    
    def get_numeric_value(self) -> int:
        """Get numeric representation (0-5)."""
        mapping = {
            self.NONE: 0,
            self.BASIC: 1,
            self.DEVELOPING: 2,
            self.COMPETENT: 3,
            self.PROFICIENT: 4,
            self.EXPERT: 5
        }\r
    )
        return mapping[self]
    
    @classmethod
    def from_score(cls, score: float) -> "CompetenceLevel":
        """Convert normalized score (0-1) to competence level."""
        if score >= 0.9:
            return cls.EXPERT
        elif score >= 0.7:
            return cls.PROFICIENT
        elif score >= 0.5:
            return cls.COMPETENT
        elif score >= 0.3:
            return cls.DEVELOPING
        elif score >= 0.1:
            return cls.BASIC
        else:
            return cls.NONE


class CalculationModel(BaseModel):
    """Configuration for competence level calculation."""
    
    name: str
    version: str = "1.0"
    description: str = ""
    
    # Weight configuration for different metrics (must sum to 1.0)
    weights: Dict[CompetenceMetric, float] = Field(default_factory=dict)
    
    # Thresholds for different competence levels
    level_thresholds: Dict[CompetenceLevel, float] = Field(default_factory=dict)
    
    # Normalization parameters
    frequency_max: int = 100           # Max frequency for normalization
    volume_max: float = 1000000.0     # Max volume for normalization
    recency_max_days: int = 365       # Max days for recency calculation
    
    # Bonus multipliers
    consistency_bonus: float = 1.2    # Multiplier for consistent usage
    collaboration_bonus: float = 1.1  # Multiplier for collaborative work
    innovation_bonus: float = 1.15    # Multiplier for innovative work
    
    model_config = ConfigDict(\r\n        json_schema_extra={
            "example": {
                "name": "Default Programming Language Model",
                "version": "1.0",
                "description": "Standard model for programming language competence",
                "weights": {
                    "frequency": 0.25,
                    "volume": 0.20,
                    "consistency": 0.15,
                    "recency": 0.15,
                    "complexity": 0.15,
                    "quality": 0.10
                }
            }
        }\r
    )
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = sum(self.weights.values())
        return abs(total - 1.0) < 0.01  # Allow small floating point errors


class CompetenceCalculator:
    """Calculates competence levels using configurable models."""
    
    def __init__(self, model: CalculationModel = None):
        """
        Initialize calculator with a calculation model.
        
        Args:
            model: Calculation model to use. If None, uses default model.
        """
        self.model = model or self._create_default_model()
        self.calculation_history: List[Dict[str, Any]] = []
    
    def _create_default_model(self) -> CalculationModel:
        """Create default calculation model."""
        return CalculationModel(
            name="Default Technical Skill Model",
            version="1.0",
            description="Balanced model for technical skill assessment",
            weights={
                CompetenceMetric.FREQUENCY: 0.25,
                CompetenceMetric.VOLUME: 0.20,
                CompetenceMetric.CONSISTENCY: 0.15,
                CompetenceMetric.RECENCY: 0.15,
                CompetenceMetric.COMPLEXITY: 0.15,
                CompetenceMetric.QUALITY: 0.10
            },
            level_thresholds={
                CompetenceLevel.NONE: 0.0,
                CompetenceLevel.BASIC: 0.1,
                CompetenceLevel.DEVELOPING: 0.3,
                CompetenceLevel.COMPETENT: 0.5,
                CompetenceLevel.PROFICIENT: 0.7,
                CompetenceLevel.EXPERT: 0.9
            }
        )
    
    def calculate_competence_level(
        self, 
        data: CompetenceData,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate competence level for a skill based on provided data.
        
        Args:
            data: Competence data for the skill
            context: Additional context for calculation
            
        Returns:
            Dictionary with competence level and detailed breakdown
        """
        try:
            # Normalize all metrics to 0-1 range
            normalized_metrics = self._normalize_metrics(data)
            
            # Calculate weighted score
            weighted_score = self._calculate_weighted_score(normalized_metrics)
            
            # Apply bonuses
            final_score = self._apply_bonuses(weighted_score, data, normalized_metrics)
            
            # Determine competence level
            competence_level = self._determine_level(final_score)
            
            # Create detailed result
            result = {
                "skill_name": data.skill_name,
                "competence_level": competence_level,
                "final_score": min(final_score, 1.0),  # Cap at 1.0
                "base_score": weighted_score,
                "normalized_metrics": normalized_metrics,
                "raw_data": {
                    "frequency": data.frequency,
                    "volume": data.volume,
                    "consistency": data.consistency_score,
                    "recency_days": data.recency_days,
                    "complexity": data.complexity_score,
                    "time_span_months": data.time_span_months
                },
                "calculation_details": {
                    "model_name": self.model.name,
                    "model_version": self.model.version,
                    "weights_used": dict(self.model.weights),
                    "bonuses_applied": self._get_bonuses_applied(data, normalized_metrics)
                },
                "recommendations": self._generate_recommendations(competence_level, data),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            # Store in calculation history
            self.calculation_history.append({
                "skill": data.skill_name,
                "level": competence_level,
                "score": final_score,
                "timestamp": datetime.now()
            })
            
            logger.info(f"Calculated competence for {data.skill_name}: {competence_level} (score: {final_score:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating competence for {data.skill_name}: {str(e)}")
            return {
                "skill_name": data.skill_name,
                "error": f"Calculation failed: {str(e)}",
                "competence_level": CompetenceLevel.NONE,
                "final_score": 0.0
            }
    
    def _normalize_metrics(self, data: CompetenceData) -> Dict[str, float]:
        """Normalize all metrics to 0-1 range."""
        normalized = {}
        
        # Frequency normalization (logarithmic for better distribution)
        if data.frequency > 0:
            normalized["frequency"] = min(1.0, data.frequency / self.model.frequency_max)
        else:
            normalized["frequency"] = 0.0
        
        # Volume normalization
        normalized["volume"] = min(1.0, data.volume / self.model.volume_max)
        
        # Consistency (already 0-1)
        normalized["consistency"] = max(0.0, min(1.0, data.consistency_score))
        
        # Recency (inverse of days - more recent = higher score)
        if data.recency_days <= 0:
            normalized["recency"] = 1.0
        else:
            recency_score = 1.0 - (data.recency_days / self.model.recency_max_days)
            normalized["recency"] = max(0.0, recency_score)
        
        # Complexity (already 0-1)
        normalized["complexity"] = max(0.0, min(1.0, data.complexity_score))
        
        # Quality (already 0-1)
        normalized["quality"] = max(0.0, min(1.0, data.quality_score))
        
        # Collaboration (already 0-1)
        normalized["collaboration"] = max(0.0, min(1.0, data.collaboration_score))
        
        return normalized
    
    def _calculate_weighted_score(self, normalized_metrics: Dict[str, float]) -> float:
        """Calculate weighted score based on model weights."""
        score = 0.0
        
        for metric, weight in self.model.weights.items():
            if metric.value in normalized_metrics:
                contribution = normalized_metrics[metric.value] * weight
                score += contribution
                logger.debug(f"Metric {metric.value}: {normalized_metrics[metric.value]:.3f} * {weight:.3f} = {contribution:.3f}")
        
        return score
    
    def _apply_bonuses(
        self, 
        base_score: float, 
        data: CompetenceData,
        normalized_metrics: Dict[str, float]
    ) -> float:
        """Apply bonus multipliers based on special conditions."""
        multiplier = 1.0
        
        # Consistency bonus
        if data.consistency_score > 0.7:
            multiplier *= self.model.consistency_bonus
        
        # Collaboration bonus
        if data.collaboration_score > 0.5:
            multiplier *= self.model.collaboration_bonus
        
        # Experience duration bonus (long-term usage)
        if data.time_span_months > 24:  # 2+ years
            multiplier *= 1.1
        elif data.time_span_months > 12:  # 1+ years
            multiplier *= 1.05
        
        return base_score * multiplier
    
    def _determine_level(self, score: float) -> CompetenceLevel:
        """Determine competence level based on final score."""
        # Sort thresholds in descending order
        sorted_levels = sorted(
            self.model.level_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for level, threshold in sorted_levels:
            if score >= threshold:
                return level
        
        return CompetenceLevel.NONE
    
    def _get_bonuses_applied(
        self,
        data: CompetenceData,
        normalized_metrics: Dict[str, float]
    ) -> List[str]:
        """Get list of bonuses that were applied."""
        bonuses = []
        
        if data.consistency_score > 0.7:
            bonuses.append("consistency_bonus")
        
        if data.collaboration_score > 0.5:
            bonuses.append("collaboration_bonus")
        
        if data.time_span_months > 24:
            bonuses.append("long_term_experience_bonus")
        elif data.time_span_months > 12:
            bonuses.append("experience_bonus")
        
        return bonuses
    
    def _generate_recommendations(
        self,
        level: CompetenceLevel,
        data: CompetenceData
    ) -> List[str]:
        """Generate recommendations for skill improvement."""
        recommendations = []
        
        if level == CompetenceLevel.NONE:
            recommendations.append("Start using this skill in projects to build foundational knowledge")
            recommendations.append("Take introductory courses or tutorials")
        
        elif level == CompetenceLevel.BASIC:
            recommendations.append("Increase usage frequency through regular practice")
            recommendations.append("Work on more complex projects involving this skill")
        
        elif level == CompetenceLevel.DEVELOPING:
            recommendations.append("Focus on consistency - use this skill regularly")
            recommendations.append("Collaborate with others to learn best practices")
        
        elif level == CompetenceLevel.COMPETENT:
            recommendations.append("Take on leadership roles in projects using this skill")
            recommendations.append("Explore advanced features and patterns")
        
        elif level == CompetenceLevel.PROFICIENT:
            recommendations.append("Mentor others and contribute to community knowledge")
            recommendations.append("Innovate and develop new solutions with this skill")
        
        elif level == CompetenceLevel.EXPERT:
            recommendations.append("Lead architectural decisions involving this skill")
            recommendations.append("Contribute to open source projects or create new tools")
        
        # Add specific recommendations based on weak areas
        if data.consistency_score < 0.3:
            recommendations.append("Improve consistency by using this skill more regularly")
        
        if data.collaboration_score < 0.3:
            recommendations.append("Participate in team projects involving this skill")
        
        if data.complexity_score < 0.4:
            recommendations.append("Challenge yourself with more complex problems")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def batch_calculate(
        self,
        skill_data_list: List[CompetenceData],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate competence levels for multiple skills."""
        results = {}
        summary = {
            "total_skills": len(skill_data_list),
            "levels_distribution": {},
            "average_score": 0.0,
            "calculation_timestamp": datetime.now().isoformat()
        }\r
    )
        
        total_score = 0.0
        level_counts = {}
        
        for skill_data in skill_data_list:
            result = self.calculate_competence_level(skill_data, context)
            results[skill_data.skill_name] = result
            
            # Update summary statistics
            level = result.get("competence_level", CompetenceLevel.NONE)
            level_counts[level] = level_counts.get(level, 0) + 1
            total_score += result.get("final_score", 0.0)
        
        # Finalize summary
        summary["levels_distribution"] = level_counts
        summary["average_score"] = total_score / max(len(skill_data_list), 1)
        summary["model_used"] = {
            "name": self.model.name,
            "version": self.model.version
        }\r
    )
        
        return {
            "results": results,
            "summary": summary
        }\r
    )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current calculation model."""
        return {
            "name": self.model.name,
            "version": self.model.version,
            "description": self.model.description,
            "weights": dict(self.model.weights),
            "thresholds": {level.value: threshold for level, threshold in self.model.level_thresholds.items()},
            "parameters": {
                "frequency_max": self.model.frequency_max,
                "volume_max": self.model.volume_max,
                "recency_max_days": self.model.recency_max_days
            },
            "bonuses": {
                "consistency_bonus": self.model.consistency_bonus,
                "collaboration_bonus": self.model.collaboration_bonus,
                "innovation_bonus": self.model.innovation_bonus
            }
        }\r
    )
    
    def update_model(self, new_model: CalculationModel) -> bool:
        """Update the calculation model."""
        if not new_model.validate_weights():
            logger.error("Invalid model: weights do not sum to 1.0")
            return False
        
        old_model = self.model.name
        self.model = new_model
        logger.info(f"Updated calculation model from '{old_model}' to '{new_model.name}'")
        return True


# Predefined calculation models for different skill types
class PredefinedModels:
    """Collection of predefined calculation models."""
    
    @staticmethod
    def programming_language_model() -> CalculationModel:
        """Model optimized for programming languages."""
        return CalculationModel(
            name="Programming Language Assessment Model",
            version="1.1",
            description="Optimized for programming language competence assessment",
            weights={
                CompetenceMetric.FREQUENCY: 0.30,
                CompetenceMetric.VOLUME: 0.25,
                CompetenceMetric.CONSISTENCY: 0.20,
                CompetenceMetric.COMPLEXITY: 0.15,
                CompetenceMetric.RECENCY: 0.10
            },
            frequency_max=200,
            volume_max=5000000.0  # 5MB of code
        )
    
    @staticmethod
    def framework_model() -> CalculationModel:
        """Model optimized for frameworks and tools."""
        return CalculationModel(
            name="Framework/Tool Assessment Model",
            version="1.1",
            description="Optimized for framework and tool competence assessment",
            weights={
                CompetenceMetric.FREQUENCY: 0.25,
                CompetenceMetric.COMPLEXITY: 0.25,
                CompetenceMetric.RECENCY: 0.20,
                CompetenceMetric.CONSISTENCY: 0.15,
                CompetenceMetric.COLLABORATION: 0.15
            },
            frequency_max=50,
            recency_max_days=180  # 6 months
        )
    
    @staticmethod
    def soft_skill_model() -> CalculationModel:
        """Model optimized for soft skills."""
        return CalculationModel(
            name="Soft Skill Assessment Model",
            version="1.0",
            description="Optimized for soft skill competence assessment",
            weights={
                CompetenceMetric.COLLABORATION: 0.35,
                CompetenceMetric.CONSISTENCY: 0.25,
                CompetenceMetric.FREQUENCY: 0.20,
                CompetenceMetric.QUALITY: 0.20
            },
            collaboration_bonus=1.3,
            consistency_bonus=1.4
        )
