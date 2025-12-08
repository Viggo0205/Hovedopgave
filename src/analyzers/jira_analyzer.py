"""Jira analyzer for analyzing and processing Jira data."""

from typing import Dict, Any
from collections import defaultdict
from services.jira_service import JiraService
from models.analysis import JiraAnalysisResult
from shared.language_categories import LANGUAGE_CATEGORIES


class JiraAnalyzer:
    """Analyzes Jira data to extract skills and insights."""
    
    def __init__(self, jira_service: JiraService):
        self.jira_service = jira_service
    
    async def analyze_developer(self, user_email: str) -> Dict[str, Any]:
        """Analyze developer skills based on Jira data."""
        
        # Get raw data from service
        profile = self.jira_service.get_user_profile(user_email)
        issues = self.jira_service.get_user_issues(user_email)
        project_data = self.jira_service.get_user_projects(user_email)
        
        # Extract language data from issues (analyzer business logic)
        language_data = self._extract_language_data_from_issues(issues, project_data)
        
        # ANALYSIS LOGIC HERE - using data from service (same as GitHub)
        language_stats = self._analyze_language_skills(language_data, issues)
        expertise_areas = self._categorize_from_language_stats(language_stats)
        
        return {
            "user_email": user_email,
            "profile": profile,
            "language_skills": language_stats,
            "expertise_areas": expertise_areas,
            "total_issues": len(issues),
            "total_projects": len(project_data)
        }
    
    async def analyze_developer_full(self, user_email: str) -> JiraAnalysisResult:
        """Analyze developer and return structured JiraAnalysisResult object."""
        # Get raw data from service
        profile = self.jira_service.get_user_profile(user_email)
        issues = self.jira_service.get_user_issues(user_email)
        project_data = self.jira_service.get_user_projects(user_email)
        language_data = self.jira_service.get_language_data_from_issues(issues, project_data)
        
        # Create JiraAnalysisResult object
        result = JiraAnalysisResult(
            user_email=user_email,
            profile_data=profile,
            total_issues=len(issues),
            primary_languages=list(language_data.keys())[:5]  # Top 5 languages
        )
        
        # Calculate language distribution percentages (same as GitHub)
        total_mentions = sum(language_data.values()) if language_data else 1
        result.language_distribution = {
            lang: (mentions / total_mentions) for lang, mentions in language_data.items()
        }
        
        return result
    
    async def get_basic_profile(self, user_email: str) -> Dict[str, Any]:
        """Get basic profile info for quick queries."""
        profile = self.jira_service.get_user_profile(user_email)
        issues = self.jira_service.get_user_issues(user_email)
        project_data = self.jira_service.get_user_projects(user_email)
        language_data = self.jira_service.get_language_data_from_issues(issues, project_data)
        
        return {
            "user_email": user_email,
            "display_name": profile.get("display_name"),
            "total_issues": len(issues),
            "top_languages": list(language_data.keys())[:3],
            "total_projects": len(project_data)
        }
    
    def _analyze_language_skills(self, language_data: Dict[str, int], issues: list) -> Dict[str, Any]:
        """Analyze programming language usage and skill levels (adapted from GitHub logic)."""
        # Count issues per language (instead of repos)
        language_issues = defaultdict(int)
        for issue in issues:
            # Extract languages from issue content
            issue_languages = self._extract_languages_from_issue(issue)
            for lang in issue_languages:
                language_issues[lang] += 1
        
        # Calculate skill levels based on total mentions (similar to GitHub lines of code)
        skills = {}
        for lang, total_mentions in language_data.items():
            issue_count = language_issues[lang]
            
            if total_mentions > 20:  # Adjusted thresholds for Jira
                level = "Expert"
            elif total_mentions > 10:
                level = "Advanced"  
            elif total_mentions > 5:
                level = "Intermediate"
            else:
                level = "Beginner"
            
            skills[lang] = {
                "level": level,
                "total_mentions": total_mentions,
                "issues": issue_count
            }
        
        return skills
    
    def _categorize_from_language_stats(self, language_stats: Dict[str, Any]) -> Dict[str, list]:
        """Categorize languages from already calculated language stats (same as GitHub)."""
        
        # Define expertise area categories (same as GitHub)
        expertise_areas = {
            "Programming Languages": [],
            "Web Frontend": [],
            "Backend/Server": [],
            "Mobile Development": [],
            "Data/Analytics": [],
            "Other Technologies": []
        }
        
        # Get language categories from shared constants (same as GitHub)
        language_categories = LANGUAGE_CATEGORIES
        
        # Categorize languages based on existing language stats (same logic as GitHub)
        for lang, stats in language_stats.items():
            if stats["total_mentions"] > 3:  # Adjusted threshold for Jira mentions
                categorized = False
                
                # Check each category
                for category, lang_list in language_categories.items():
                    if any(lang.lower() in known_lang.lower() or known_lang.lower() in lang.lower() 
                           for known_lang in lang_list):
                        expertise_areas[category].append(lang)
                        categorized = True
                        break
                
                # If not categorized, add to "Other Technologies"
                if not categorized:
                    expertise_areas["Other Technologies"].append(lang)
        
        # Remove empty categories
        expertise_areas = {k: v for k, v in expertise_areas.items() if v}
        
        return expertise_areas
    
    def _extract_languages_from_issue(self, issue: Dict[str, Any]) -> list:
        """Extract programming languages mentioned in an issue."""
        languages = []
        
        # Check issue description, summary, and comments for language mentions
        text_content = ""
        if issue.get("summary"):
            text_content += issue["summary"].lower() + " "
        if issue.get("description"):
            text_content += issue["description"].lower() + " "
        
        # Look for language keywords in text
        for category, lang_list in LANGUAGE_CATEGORIES.items():
            for lang in lang_list:
                if lang.lower() in text_content:
                    languages.append(lang)
        
        return languages
    
    def _extract_language_data_from_issues(self, issues: list, projects: list) -> Dict[str, int]:
        """Extract language mentions from issue descriptions and summaries (analyzer business logic)."""
        language_mentions = {}
        
        # Get all languages from shared constants
        all_languages = []
        for category_languages in LANGUAGE_CATEGORIES.values():
            all_languages.extend(category_languages)
        
        # Search through all issues for language mentions
        for issue in issues:
            # Combine text content from summary and description
            text_content = ""
            if issue.get("summary"):
                text_content += issue["summary"].lower() + " "
            if issue.get("description"):
                text_content += issue["description"].lower() + " "
            
            # Count mentions of each language
            for language in all_languages:
                if language.lower() in text_content:
                    if language in language_mentions:
                        language_mentions[language] += 1
                    else:
                        language_mentions[language] = 1
        
        # Also check project descriptions
        for project in projects:
            if project.get("description"):
                text_content = project["description"].lower()
                for language in all_languages:
                    if language.lower() in text_content:
                        if language in language_mentions:
                            language_mentions[language] += 1
                        else:
                            language_mentions[language] = 1
        
        return language_mentions
    
    def _extract_language_data_from_issues(self, issues: list, projects: list) -> Dict[str, int]:
        """Extract language mentions from issue descriptions and summaries (analyzer business logic)."""
        language_mentions = {}
        
        # Get all languages from shared constants
        all_languages = []
        for category_languages in LANGUAGE_CATEGORIES.values():
            all_languages.extend(category_languages)
        
        # Search through all issues for language mentions
        for issue in issues:
            # Combine text content from summary and description
            text_content = ""
            if issue.get("summary"):
                text_content += issue["summary"].lower() + " "
            if issue.get("description"):
                text_content += issue["description"].lower() + " "
            
            # Count mentions of each language
            for language in all_languages:
                if language.lower() in text_content:
                    if language in language_mentions:
                        language_mentions[language] += 1
                    else:
                        language_mentions[language] = 1
        
        # Also check project descriptions
        for project in projects:
            if project.get("description"):
                text_content = project["description"].lower()
                for language in all_languages:
                    if language.lower() in text_content:
                        if language in language_mentions:
                            language_mentions[language] += 1
                        else:
                            language_mentions[language] = 1
        
        return language_mentions