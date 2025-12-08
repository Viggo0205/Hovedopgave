"""
Skill processing engine for combining and analyzing developer skills.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

from models.skills import (
    Skill, SkillLevel, SkillCategory, SkillEvidence, SkillAssessment, SkillGap
)
from models.analysis import GitHubAnalysisResult, JiraAnalysisResult
from db.repository import DatabaseRepository

logger = logging.getLogger(__name__)


class SkillProcessor:
    """Processes and combines skill data from multiple sources."""
    
    def __init__(self, db_repository: Optional[DatabaseRepository] = None):
        """
        Initialize the skill processor.
        
        Args:
            db_repository: Database repository instance (optional)
        """
        self.db_repo = db_repository or DatabaseRepository()
        self.skill_categories = self._initialize_skill_categories()
        self.technology_mappings = self._initialize_technology_mappings()
    
    def _initialize_skill_categories(self) -> Dict[str, List[str]]:
        """Initialize skill category mappings from database."""
        try:
            # Try to load from database first
            categories = self.db_repo.get_competence_categories()
            
            if categories:
                logger.info(f"Loaded skill categories from database: {len(categories)} categories")
                return categories
            else:
                logger.warning("No categories found in database, using fallback defaults")
                return self._get_fallback_categories()
                
        except Exception as e:
            logger.warning(f"Could not load categories from database: {e}. Using fallback defaults.")
            return self._get_fallback_categories()
    
    def _get_fallback_categories(self) -> Dict[str, List[str]]:
        """Fallback categories if database is not available."""
        return {
            "programming_languages": [
                "Python", "JavaScript", "Java", "TypeScript", "C#", "C++", "Go",
                "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "Julia"
            ],
            "frameworks_tools": [
                "React", "Angular", "Vue.js", "Django", "Flask", "Spring", "Express",
                "Node.js", "Docker", "Kubernetes", "Jenkins", "Git", "AWS", "Azure"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
                "SQLite", "Oracle", "SQL Server", "Cassandra", "DynamoDB"
            ],
            "soft_skills": [
                "communication", "leadership", "problem_solving", "collaboration",
                "mentoring", "project_management", "documentation", "testing"
            ],
            "domain_knowledge": [
                "web_development", "mobile_development", "data_science",
                "machine_learning", "devops", "security", "ui_ux", "backend", "frontend"
            ]
        }
    
    def _initialize_technology_mappings(self) -> Dict[str, SkillCategory]:
        """Initialize technology to skill category mappings."""
        mappings = {}
        
        # Programming languages
        for lang in self.skill_categories["programming_languages"]:
            mappings[lang.lower()] = SkillCategory.PROGRAMMING_LANGUAGE
        
        # Frameworks and tools
        framework_mappings = {
            "react": SkillCategory.FRAMEWORK,
            "angular": SkillCategory.FRAMEWORK,
            "vue.js": SkillCategory.FRAMEWORK,
            "django": SkillCategory.FRAMEWORK,
            "flask": SkillCategory.FRAMEWORK,
            "spring": SkillCategory.FRAMEWORK,
            "docker": SkillCategory.TOOL,
            "kubernetes": SkillCategory.TOOL,
            "jenkins": SkillCategory.TOOL,
            "git": SkillCategory.TOOL
        }
        mappings.update(framework_mappings)
        
        # Databases
        for db in self.skill_categories["databases"]:
            mappings[db.lower()] = SkillCategory.DATABASE
        
        return mappings
    
    def process_github_data(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process GitHub analysis data to extract skills.
        
        Args:
            github_data: GitHub analysis results
            
        Returns:
            Skill assessment dictionary
        """
        try:
            skill_assessment = SkillAssessment()
            
            # Extract programming language skills
            self._extract_programming_language_skills(github_data, skill_assessment)
            
            # Extract framework and tool skills
            self._extract_framework_skills(github_data, skill_assessment)
            
            # Extract collaboration skills
            self._extract_collaboration_skills_github(github_data, skill_assessment)
            
            # Extract soft skills from GitHub activity patterns
            self._extract_soft_skills_github(github_data, skill_assessment)
            
            # Calculate overall assessment metrics
            self._calculate_assessment_metrics(skill_assessment)
            
            return {
                "technical_skills": [skill.dict() for skill in skill_assessment.technical_skills],
                "soft_skills": [skill.dict() for skill in skill_assessment.soft_skills],
                "domain_skills": [skill.dict() for skill in skill_assessment.domain_skills],
                "summary": {
                    "total_skills": skill_assessment.total_skills_identified,
                    "primary_specialization": skill_assessment.primary_specialization,
                    "experience_breadth": skill_assessment.experience_breadth_score,
                    "experience_depth": skill_assessment.experience_depth_score
                },
                "recommendations": skill_assessment.get_learning_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error processing GitHub data: {e}")
            return {"error": str(e)}
    
    def _extract_programming_language_skills(
        self, github_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract programming language skills from GitHub data."""
        language_distribution = github_data.get("language_distribution", {})
        primary_languages = github_data.get("primary_languages", [])
        total_commits = github_data.get("total_commits", 0)
        
        for language, percentage in language_distribution.items():
            if percentage < 0.05:  # Skip languages with less than 5% usage
                continue
            
            # Determine skill level based on usage and commit count
            skill_level = self._calculate_language_skill_level(
                language, percentage, total_commits, primary_languages
            )
            
            # Create evidence
            evidence = SkillEvidence(
                source="github_commits",
                description=f"Used {language} in {percentage:.1%} of code across repositories",
                confidence=min(percentage * 2, 1.0),
                frequency=int(total_commits * percentage),
                recency=datetime.now()
            )
            
            # Create skill
            skill = Skill(
                name=language,
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                level=skill_level,
                confidence_score=min(percentage * 2, 1.0),
                usage_frequency=int(total_commits * percentage),
                trend="stable"  # Could be enhanced with historical data
            )
            skill.add_evidence(evidence)
            
            assessment.add_skill(skill)
    
    def _calculate_language_skill_level(
        self, language: str, percentage: float, total_commits: int, primary_languages: List[str]
    ) -> SkillLevel:
        """Calculate skill level for a programming language."""
        # Base score from usage percentage
        base_score = percentage
        
        # Boost for primary languages
        if language in primary_languages[:3]:  # Top 3 languages
            base_score *= 1.2
        
        # Boost based on commit volume
        commit_boost = min(total_commits / 100, 1.0) * 0.2
        base_score += commit_boost
        
        return SkillLevel.from_score(min(base_score, 1.0))
    
    def _extract_framework_skills(
        self, github_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract framework and tool skills from GitHub data."""
        framework_usage = github_data.get("framework_usage", {})
        tool_usage = github_data.get("tool_usage", {})
        repositories = github_data.get("repositories", [])
        
        # Process frameworks
        for framework, usage_count in framework_usage.items():
            if usage_count < 2:  # Skip rarely used frameworks
                continue
            
            skill_level = SkillLevel.from_score(min(usage_count / 10, 1.0))
            
            evidence = SkillEvidence(
                source="github_repositories",
                description=f"Used {framework} in {usage_count} repositories",
                confidence=min(usage_count / 5, 1.0),
                frequency=usage_count,
                recency=datetime.now()
            )
            
            skill = Skill(
                name=framework,
                category=SkillCategory.FRAMEWORK,
                level=skill_level,
                confidence_score=min(usage_count / 5, 1.0),
                usage_frequency=usage_count
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
        
        # Process tools
        for tool, usage_count in tool_usage.items():
            if usage_count < 2:
                continue
            
            skill_level = SkillLevel.from_score(min(usage_count / 8, 1.0))
            
            evidence = SkillEvidence(
                source="github_repositories",
                description=f"Used {tool} in {usage_count} repositories",
                confidence=min(usage_count / 4, 1.0),
                frequency=usage_count,
                recency=datetime.now()
            )
            
            skill = Skill(
                name=tool,
                category=SkillCategory.TOOL,
                level=skill_level,
                confidence_score=min(usage_count / 4, 1.0),
                usage_frequency=usage_count
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
    
    def _extract_collaboration_skills_github(
        self, github_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract collaboration skills from GitHub activity."""
        code_review_participation = github_data.get("code_review_participation", 0)
        total_pull_requests = github_data.get("total_pull_requests", 0)
        open_source_contributions = github_data.get("open_source_contributions", 0)
        
        # Code review skill
        if code_review_participation > 0:
            review_skill_level = SkillLevel.from_score(
                min(code_review_participation / 20, 1.0)
            )
            
            evidence = SkillEvidence(
                source="github_reviews",
                description=f"Participated in {code_review_participation} code reviews",
                confidence=min(code_review_participation / 10, 1.0),
                frequency=code_review_participation,
                recency=datetime.now()
            )
            
            skill = Skill(
                name="Code Review",
                category=SkillCategory.COLLABORATION,
                level=review_skill_level,
                confidence_score=min(code_review_participation / 10, 1.0),
                usage_frequency=code_review_participation
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
        
        # Open source collaboration
        if open_source_contributions > 0:
            os_skill_level = SkillLevel.from_score(
                min(open_source_contributions / 10, 1.0)
            )
            
            evidence = SkillEvidence(
                source="github_contributions",
                description=f"Contributed to {open_source_contributions} open source projects",
                confidence=min(open_source_contributions / 5, 1.0),
                frequency=open_source_contributions,
                recency=datetime.now()
            )
            
            skill = Skill(
                name="Open Source Collaboration",
                category=SkillCategory.COLLABORATION,
                level=os_skill_level,
                confidence_score=min(open_source_contributions / 5, 1.0),
                usage_frequency=open_source_contributions
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
    
    def _extract_soft_skills_github(
        self, github_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract soft skills from GitHub activity patterns."""
        documentation_score = github_data.get("documentation_score", 0.0)
        consistency_score = github_data.get("consistency_score", 0.0)
        total_repositories = github_data.get("total_repositories", 0)
        
        # Documentation skill
        if documentation_score > 0.3:
            doc_skill_level = SkillLevel.from_score(documentation_score)
            
            evidence = SkillEvidence(
                source="github_repositories",
                description=f"Documented {documentation_score:.1%} of repositories",
                confidence=documentation_score,
                frequency=int(total_repositories * documentation_score),
                recency=datetime.now()
            )
            
            skill = Skill(
                name="Documentation",
                category=SkillCategory.COMMUNICATION,
                level=doc_skill_level,
                confidence_score=documentation_score,
                usage_frequency=int(total_repositories * documentation_score)
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
        
        # Consistency/Reliability
        if consistency_score > 0.5:
            consistency_skill_level = SkillLevel.from_score(consistency_score)
            
            evidence = SkillEvidence(
                source="github_activity",
                description=f"Maintained {consistency_score:.1%} consistency in contributions",
                confidence=consistency_score,
                frequency=1,  # Boolean-like metric
                recency=datetime.now()
            )
            
            skill = Skill(
                name="Consistency",
                category=SkillCategory.PROJECT_MANAGEMENT,
                level=consistency_skill_level,
                confidence_score=consistency_score,
                usage_frequency=1
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
    
    def process_jira_data(self, jira_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Jira analysis data to extract skills.
        
        Args:
            jira_data: Jira analysis results
            
        Returns:
            Skill assessment dictionary
        """
        try:
            skill_assessment = SkillAssessment()
            
            # Extract problem-solving skills
            self._extract_problem_solving_skills(jira_data, skill_assessment)
            
            # Extract communication skills
            self._extract_communication_skills_jira(jira_data, skill_assessment)
            
            # Extract domain knowledge
            self._extract_domain_knowledge(jira_data, skill_assessment)
            
            # Extract project management skills
            self._extract_project_management_skills(jira_data, skill_assessment)
            
            # Calculate assessment metrics
            self._calculate_assessment_metrics(skill_assessment)
            
            return {
                "technical_skills": [skill.dict() for skill in skill_assessment.technical_skills],
                "soft_skills": [skill.dict() for skill in skill_assessment.soft_skills],
                "domain_skills": [skill.dict() for skill in skill_assessment.domain_skills],
                "summary": {
                    "total_skills": skill_assessment.total_skills_identified,
                    "primary_specialization": skill_assessment.primary_specialization,
                    "experience_breadth": skill_assessment.experience_breadth_score,
                    "experience_depth": skill_assessment.experience_depth_score
                },
                "collaboration": {
                    "resolution_rate": jira_data.get("resolution_rate", 0.0),
                    "collaboration_frequency": jira_data.get("collaboration_frequency", 0.0),
                    "comment_quality": jira_data.get("comment_quality_score", 0.0)
                },
                "recommendations": skill_assessment.get_learning_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error processing Jira data: {e}")
            return {"error": str(e)}
    
    def _extract_problem_solving_skills(
        self, jira_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract problem-solving skills from Jira data."""
        resolution_rate = jira_data.get("resolution_rate", 0.0)
        avg_resolution_time = jira_data.get("average_resolution_time_hours", 0.0)
        total_issues_resolved = jira_data.get("total_issues_resolved", 0)
        
        if total_issues_resolved > 0:
            # Problem solving skill based on resolution efficiency
            efficiency_score = resolution_rate
            if avg_resolution_time > 0:
                # Lower resolution time is better (max 48 hours as baseline)
                time_efficiency = max(0, 1 - (avg_resolution_time / 48))
                efficiency_score = (efficiency_score + time_efficiency) / 2
            
            skill_level = SkillLevel.from_score(efficiency_score)
            
            evidence = SkillEvidence(
                source="jira_issues",
                description=f"Resolved {total_issues_resolved} issues with {resolution_rate:.1%} success rate",
                confidence=min(total_issues_resolved / 20, 1.0),
                frequency=total_issues_resolved,
                recency=datetime.now()
            )
            
            skill = Skill(
                name="Problem Solving",
                category=SkillCategory.PROBLEM_SOLVING,
                level=skill_level,
                confidence_score=min(total_issues_resolved / 20, 1.0),
                usage_frequency=total_issues_resolved
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
    
    def _extract_communication_skills_jira(
        self, jira_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract communication skills from Jira activity."""
        comment_quality_score = jira_data.get("comment_quality_score", 0.0)
        total_comments = jira_data.get("total_comments", 0)
        collaboration_frequency = jira_data.get("collaboration_frequency", 0.0)
        
        if total_comments > 5:  # Minimum threshold for meaningful assessment
            comm_skill_level = SkillLevel.from_score(
                (comment_quality_score + collaboration_frequency) / 2
            )
            
            evidence = SkillEvidence(
                source="jira_comments",
                description=f"Made {total_comments} comments with quality score {comment_quality_score:.2f}",
                confidence=min(total_comments / 30, 1.0),
                frequency=total_comments,
                recency=datetime.now()
            )
            
            skill = Skill(
                name="Written Communication",
                category=SkillCategory.COMMUNICATION,
                level=comm_skill_level,
                confidence_score=min(total_comments / 30, 1.0),
                usage_frequency=total_comments
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
    
    def _extract_domain_knowledge(
        self, jira_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract domain knowledge from Jira technical areas."""
        technical_areas = jira_data.get("technical_areas", {})
        business_domains = jira_data.get("business_domains", {})
        
        # Process technical areas
        for area, involvement_count in technical_areas.items():
            if involvement_count < 2:
                continue
            
            skill_level = SkillLevel.from_score(min(involvement_count / 10, 1.0))
            
            evidence = SkillEvidence(
                source="jira_issues",
                description=f"Worked on {involvement_count} issues in {area}",
                confidence=min(involvement_count / 5, 1.0),
                frequency=involvement_count,
                recency=datetime.now()
            )
            
            # Map to appropriate domain category
            category = self._map_technical_area_to_category(area)
            
            skill = Skill(
                name=area.replace("_", " ").title(),
                category=category,
                level=skill_level,
                confidence_score=min(involvement_count / 5, 1.0),
                usage_frequency=involvement_count
            )
            skill.add_evidence(evidence)
            assessment.add_skill(skill)
    
    def _map_technical_area_to_category(self, area: str) -> SkillCategory:
        """Map technical area to appropriate skill category."""
        area_lower = area.lower()
        
        domain_mappings = {
            "backend": SkillCategory.WEB_DEVELOPMENT,
            "frontend": SkillCategory.WEB_DEVELOPMENT,
            "api": SkillCategory.WEB_DEVELOPMENT,
            "database": SkillCategory.DATABASE,
            "security": SkillCategory.SECURITY,
            "testing": SkillCategory.TESTING,
            "ui": SkillCategory.UI_UX,
            "ux": SkillCategory.UI_UX,
            "mobile": SkillCategory.MOBILE_DEVELOPMENT,
            "data": SkillCategory.DATA_SCIENCE,
            "devops": SkillCategory.DEVOPS
        }
        
        for keyword, category in domain_mappings.items():
            if keyword in area_lower:
                return category
        
        return SkillCategory.WEB_DEVELOPMENT  # Default
    
    def _extract_project_management_skills(
        self, jira_data: Dict[str, Any], assessment: SkillAssessment
    ) -> None:
        """Extract project management skills from Jira data."""
        total_projects = jira_data.get("total_projects", 0)
        projects = jira_data.get("projects", [])
        
        if total_projects > 1:  # Multi-project experience
            # Calculate leadership indicators
            leadership_score = 0.0
            for project in projects:
                if project.get("primary_role") in ["lead", "analyst"]:
                    leadership_score += 1
            
            if leadership_score > 0:
                leadership_skill_level = SkillLevel.from_score(
                    min(leadership_score / total_projects, 1.0)
                )
                
                evidence = SkillEvidence(
                    source="jira_projects",
                    description=f"Led or analyzed in {int(leadership_score)} out of {total_projects} projects",
                    confidence=min(total_projects / 5, 1.0),
                    frequency=int(leadership_score),
                    recency=datetime.now()
                )
                
                skill = Skill(
                    name="Project Leadership",
                    category=SkillCategory.PROJECT_MANAGEMENT,
                    level=leadership_skill_level,
                    confidence_score=min(total_projects / 5, 1.0),
                    usage_frequency=int(leadership_score)
                )
                skill.add_evidence(evidence)
                assessment.add_skill(skill)
    
    def _calculate_assessment_metrics(self, assessment: SkillAssessment) -> None:
        """Calculate overall assessment metrics."""
        all_skills = assessment.get_all_skills()
        
        if not all_skills:
            return
        
        # Calculate breadth (number of different skill categories)
        categories = set(skill.category for skill in all_skills)
        max_categories = len(SkillCategory)
        assessment.experience_breadth_score = len(categories) / max_categories
        
        # Calculate depth (average skill level in primary areas)
        skill_levels = [skill.level.get_numeric_value() for skill in all_skills]
        avg_level = sum(skill_levels) / len(skill_levels)
        assessment.experience_depth_score = (avg_level - 1) / 3  # Normalize to 0-1
        
        # Identify primary specialization
        assessment.primary_specialization = assessment.identify_primary_specialization()
        
        # Generate skill gaps
        assessment.skill_gaps = self._identify_skill_gaps(assessment)
    
    def _identify_skill_gaps(self, assessment: SkillAssessment) -> List[SkillGap]:
        """Identify potential skill gaps and learning opportunities."""
        gaps = []
        
        # Check for common skill combinations
        has_frontend = any(
            skill.category in [SkillCategory.UI_UX, SkillCategory.WEB_DEVELOPMENT]
            and "frontend" in skill.name.lower()
            for skill in assessment.get_all_skills()
        )
        
        has_backend = any(
            "backend" in skill.name.lower() or skill.category == SkillCategory.DATABASE
            for skill in assessment.get_all_skills()
        )
        
        # Suggest complementary skills
        if has_backend and not has_frontend:
            gaps.append(SkillGap(
                skill_name="Frontend Development",
                category=SkillCategory.WEB_DEVELOPMENT,
                importance="medium",
                target_level=SkillLevel.INTERMEDIATE,
                estimated_learning_time_weeks=12
            ))
        
        if has_frontend and not has_backend:
            gaps.append(SkillGap(
                skill_name="Backend Development",
                category=SkillCategory.WEB_DEVELOPMENT,
                importance="medium",
                target_level=SkillLevel.INTERMEDIATE,
                estimated_learning_time_weeks=10
            ))
        
        # Check for DevOps skills
        has_devops = any(
            skill.category == SkillCategory.DEVOPS
            for skill in assessment.get_all_skills()
        )
        
        if not has_devops and len(assessment.technical_skills) > 5:
            gaps.append(SkillGap(
                skill_name="DevOps",
                category=SkillCategory.DEVOPS,
                importance="high",
                target_level=SkillLevel.INTERMEDIATE,
                estimated_learning_time_weeks=8
            ))
        
        return gaps
    
    def combine_assessments(self, assessments: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple skill assessments from different sources.
        
        Args:
            assessments: Dictionary of source -> assessment data
            
        Returns:
            Combined assessment
        """
        try:
            combined_assessment = SkillAssessment()
            
            # Process each source
            for source, assessment_data in assessments.items():
                if assessment_data.get("error"):
                    continue
                
                # Extract skills from each source
                technical_skills = assessment_data.get("technical_skills", [])
                soft_skills = assessment_data.get("soft_skills", [])
                domain_skills = assessment_data.get("domain_skills", [])
                
                # Add skills to combined assessment
                for skill_data in technical_skills + soft_skills + domain_skills:
                    try:
                        skill = Skill(**skill_data)
                        combined_assessment.add_skill(skill)
                    except Exception as e:
                        logger.warning(f"Error adding skill from {source}: {e}")
                        continue
            
            # Merge duplicate skills
            self._merge_duplicate_skills(combined_assessment)
            
            # Calculate combined metrics
            self._calculate_assessment_metrics(combined_assessment)
            
            return {
                "technical_skills": [skill.dict() for skill in combined_assessment.technical_skills],
                "soft_skills": [skill.dict() for skill in combined_assessment.soft_skills],
                "domain_skills": [skill.dict() for skill in combined_assessment.domain_skills],
                "analysis_date": datetime.now().isoformat(),
                "summary": {
                    "total_skills": combined_assessment.total_skills_identified,
                    "primary_specialization": combined_assessment.primary_specialization,
                    "experience_breadth": combined_assessment.experience_breadth_score,
                    "experience_depth": combined_assessment.experience_depth_score
                },
                "top_skills": [skill.name for skill in combined_assessment.get_top_skills(10)],
                "improvement_areas": [gap.skill_name for gap in combined_assessment.skill_gaps],
                "career_recommendations": combined_assessment.career_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error combining assessments: {e}")
            return {
                "error": str(e),
                "analysis_date": datetime.now().isoformat()
            }
    
    def _merge_duplicate_skills(self, assessment: SkillAssessment) -> None:
        """Merge duplicate skills from different sources."""
        skill_groups = defaultdict(list)
        
        # Group skills by name
        for skill in assessment.get_all_skills():
            skill_groups[skill.name.lower()].append(skill)
        
        # Merge duplicates
        for skill_name, skills in skill_groups.items():
            if len(skills) > 1:
                # Keep the skill with highest confidence
                best_skill = max(skills, key=lambda s: s.confidence_score)
                
                # Combine evidence from all sources
                all_evidence = []
                total_frequency = 0
                for skill in skills:
                    all_evidence.extend(skill.evidence)
                    total_frequency += skill.usage_frequency
                
                best_skill.evidence = all_evidence
                best_skill.usage_frequency = total_frequency
                
                # Remove duplicates from assessment
                for skill in skills[1:]:  # Keep first, remove others
                    if skill in assessment.technical_skills:
                        assessment.technical_skills.remove(skill)
                    elif skill in assessment.soft_skills:
                        assessment.soft_skills.remove(skill)
                    elif skill in assessment.domain_skills:
                        assessment.domain_skills.remove(skill)
    
    def compare_developers(
        self,
        dev1_analysis: Dict[str, Any],
        dev2_analysis: Dict[str, Any],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare skill profiles between two developers.
        
        Args:
            dev1_analysis: First developer's analysis
            dev2_analysis: Second developer's analysis
            metrics: Specific metrics to compare
            
        Returns:
            Comparison results
        """
        try:
            comparison = {
                "summary": {},
                "skill_gaps": {},
                "strengths_comparison": {},
                "recommendations": []
            }
            
            # Extract skills from both analyses
            dev1_skills = self._extract_skills_from_analysis(dev1_analysis)
            dev2_skills = self._extract_skills_from_analysis(dev2_analysis)
            
            # Compare skill coverage
            comparison["summary"]["dev1_total_skills"] = len(dev1_skills)
            comparison["summary"]["dev2_total_skills"] = len(dev2_skills)
            
            # Find common and unique skills
            dev1_skill_names = set(skill.name for skill in dev1_skills)
            dev2_skill_names = set(skill.name for skill in dev2_skills)
            
            common_skills = dev1_skill_names.intersection(dev2_skill_names)
            dev1_unique = dev1_skill_names - dev2_skill_names
            dev2_unique = dev2_skill_names - dev1_skill_names
            
            comparison["summary"]["common_skills"] = list(common_skills)
            comparison["summary"]["dev1_unique_skills"] = list(dev1_unique)
            comparison["summary"]["dev2_unique_skills"] = list(dev2_unique)
            
            # Compare skill levels for common skills
            skill_level_comparison = {}
            for skill_name in common_skills:
                dev1_skill = next(s for s in dev1_skills if s.name == skill_name)
                dev2_skill = next(s for s in dev2_skills if s.name == skill_name)
                
                skill_level_comparison[skill_name] = {
                    "dev1_level": dev1_skill.level.value,
                    "dev2_level": dev2_skill.level.value,
                    "advantage": "dev1" if dev1_skill.level.get_numeric_value() > dev2_skill.level.get_numeric_value() else "dev2" if dev2_skill.level.get_numeric_value() > dev1_skill.level.get_numeric_value() else "equal"
                }
            
            comparison["strengths_comparison"] = skill_level_comparison
            
            # Generate recommendations
            comparison["recommendations"] = self._generate_comparison_recommendations(
                dev1_unique, dev2_unique, skill_level_comparison
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing developers: {e}")
            return {"error": str(e)}
    
    def _extract_skills_from_analysis(self, analysis: Dict[str, Any]) -> List[Skill]:
        """Extract skills from analysis data."""
        skills = []
        
        skill_assessment = analysis.get("skill_assessment", {})
        for skill_category in ["technical_skills", "soft_skills", "domain_skills"]:
            skill_data_list = skill_assessment.get(skill_category, [])
            for skill_data in skill_data_list:
                try:
                    skill = Skill(**skill_data)
                    skills.append(skill)
                except Exception:
                    continue
        
        return skills
    
    def _generate_comparison_recommendations(
        self,
        dev1_unique: set,
        dev2_unique: set,
        skill_comparison: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on developer comparison."""
        recommendations = []
        
        # Recommend cross-learning
        if dev1_unique and dev2_unique:
            recommendations.append(
                "Consider cross-training opportunities where each developer can learn from the other's unique skills"
            )
        
        # Recommend skill development for weaker areas
        weaker_skills = [
            skill for skill, comparison in skill_comparison.items()
            if comparison["advantage"] != "equal"
        ]
        
        if weaker_skills:
            recommendations.append(
                f"Focus on strengthening skills where there are level differences: {', '.join(weaker_skills[:3])}"
            )
        
        # Team composition recommendations
        if len(dev1_unique) > len(dev2_unique):
            recommendations.append(
                "Developer 1 has broader skill coverage and might be better suited for diverse project requirements"
            )
        elif len(dev2_unique) > len(dev1_unique):
            recommendations.append(
                "Developer 2 has broader skill coverage and might be better suited for diverse project requirements"
            )
        
        return recommendations
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """Get the skill categories mapping."""
        return self.skill_categories