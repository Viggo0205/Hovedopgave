"""GitHub analyzer for analyzing and processing GitHub data."""

import logging
from typing import Dict, Any, List
from collections import defaultdict
from services.github_service import GitHubService, GitHubServiceDegradedException
from models.analysis import GitHubAnalysisResult
from shared.language_categories import LANGUAGE_CATEGORIES, get_category_for_language

logger = logging.getLogger(__name__)



class GitHubAnalyzer:
    """Analyzes GitHub data to extract skills and insights."""
    
    def __init__(self, github_service: GitHubService):
        self.github_service = github_service
    
    async def analyze_developer(self, username: str) -> Dict[str, Any]:
        """Analyze developer skills based on GitHub data with rate limiting protection."""
        try:
            # Check if service is degraded before starting
            if GitHubService.is_degraded():
                logger.error(f"Cannot analyze {username} - GitHub service is degraded")
                return {
                    "error": "GitHub integration is temporarily unavailable",
                    "username": username,
                    "degraded": True
                }
            
            # Get raw data from service (all async now)
            profile = await self.github_service.get_user_profile(username)
            repositories = await self.github_service.get_user_repositories(username)
            language_data = self.github_service.get_language_data(repositories)
            
            # ANALYSIS LOGIC HERE - using data from service
            language_stats = self._analyze_language_skills(language_data, repositories)
            expertise_areas = self._categorize_from_language_stats(language_stats)
            
            return {
                "username": username,
                "profile": profile,
                "repositories": repositories,  # Include repositories for metadata storage
                "language_skills": language_stats,
                "language_stats": language_stats,  # Alias for compatibility
                "expertise_areas": expertise_areas,
                "total_repositories": len(repositories)
            }
        except GitHubServiceDegradedException as e:
            logger.error(f"GitHub service degraded while analyzing {username}: {e}")
            return {
                "error": str(e),
                "username": username,
                "degraded": True
            }
    
    async def analyze_developer_full(self, username: str) -> GitHubAnalysisResult:
        """Analyze developer and return structured GitHubAnalysisResult object."""
        # Get raw data from service (async)
        profile = await self.github_service.get_user_profile(username)
        repositories = await self.github_service.get_user_repositories(username)
        language_data = self.github_service.get_language_data(repositories)
        
        # Create GitHubAnalysisResult object
        result = GitHubAnalysisResult(
            username=username,
            profile_data=profile,
            total_repositories=len(repositories),
            primary_languages=list(language_data.keys())[:5]  # Top 5 languages
        )
        
        # Calculate language distribution percentages
        total_lines = sum(language_data.values()) if language_data else 1
        result.language_distribution = {
            lang: (lines / total_lines) for lang, lines in language_data.items()
        }
        
        return result
    
    async def get_basic_profile(self, username: str) -> Dict[str, Any]:
        """Get basic profile info for quick queries."""
        profile = await self.github_service.get_user_profile(username)
        repositories = await self.github_service.get_user_repositories(username)
        language_data = self.github_service.get_language_data(repositories)
        
        return {
            "username": username,
            "name": profile.get("name"),
            "public_repos": profile.get("public_repos", 0),
            "top_languages": list(language_data.keys())[:3],
            "total_repositories": len(repositories)
        }
    
    def _analyze_language_skills(self, language_data: Dict[str, int], repositories: list) -> Dict[str, Any]:
        """Analyze programming language usage and skill levels."""
        # Count repos per language
        language_repos = defaultdict(int)
        for repo in repositories:
            if repo.get("languages"):
                for lang in repo["languages"].keys():
                    language_repos[lang] += 1
        
        # Calculate skill levels based on total lines of code
        skills = {}
        for lang, total_lines in language_data.items():
            repo_count = language_repos[lang]
            
            if total_lines > 10000:
                level = "Expert"
            elif total_lines > 5000:
                level = "Advanced"  
            elif total_lines > 1000:
                level = "Intermediate"
            else:
                level = "Beginner"
            
            skills[lang] = {
                "level": level,
                "total_lines": total_lines,
                "repositories": repo_count
            }
        
        return skills
    

    def _categorize_from_language_stats(self, language_stats: Dict[str, Any]) -> Dict[str, list]:
        """Categorize languages from already calculated language stats."""
        
        # Define expertise area categories
        expertise_areas = {
            "Programming Languages": [],
            "Web Frontend": [],
            "Backend/Server": [],
            "Mobile Development": [],
            "Data/Analytics": [],
            "Other Technologies": []
        }
        
        # Get language categories from dedicated constants file
        language_categories = LANGUAGE_CATEGORIES
        
        # Categorize languages based on existing language stats (no data re-extraction)
        for lang, stats in language_stats.items():
            if stats["total_lines"] > 500:  # only use significant languages
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
    
    async def get_languages_by_category(self, username: str) -> Dict[str, Any]:
        """
        Get all programming languages from a developer's profile organized by categories.
        Shows language distribution across categories and identifies top programming languages.
        
        Args:
            username: GitHub username to analyze
            
        Returns:
            Dictionary with categorized languages and top programming languages
        """
        # Get data from service
        profile = await self.github_service.get_user_profile(username)
        repositories = await self.github_service.get_user_repositories(username)
        language_data = self.github_service.get_language_data(repositories)
        
        # Analyze language skills
        language_stats = self._analyze_language_skills(language_data, repositories)
        
        # Sort languages by total lines to get top languages
        sorted_languages = sorted(
            language_stats.items(),
            key=lambda x: x[1].get("total_lines", 0),
            reverse=True
        )
        
        # Get top programming languages (only those in "Programming Languages" category)
        top_programming_languages = []
        ranks = ["Primært programmeringssprog", "Sekundært sprog", "Tredje mest anvendte sprog"]
        
        for lang, data in sorted_languages:
            category = get_category_for_language(lang)
            if category == "Programming Languages":
                top_programming_languages.append({
                    "language": lang,
                    "rank": ranks[len(top_programming_languages)] if len(top_programming_languages) < 3 else f"{len(top_programming_languages) + 1}. mest anvendte sprog",
                    "total_lines": data.get("total_lines", 0),
                    "level": data.get("level", "Unknown"),
                    "repositories": data.get("repositories", 0)
                })
                if len(top_programming_languages) >= 3:
                    break
        
        # Organize all languages by category
        categorized_languages = {}
        for category, languages in LANGUAGE_CATEGORIES.items():
            categorized_languages[category] = []
            
            # Find all languages in this category from the developer's skills
            for lang, data in language_stats.items():
                if get_category_for_language(lang) == category:
                    categorized_languages[category].append({
                        "language": lang,
                        "level": data.get("level", "Unknown"),
                        "total_lines": data.get("total_lines", 0),
                        "repositories": data.get("repositories", 0)
                    })
            
            # Sort by total lines within each category
            categorized_languages[category].sort(
                key=lambda x: x["total_lines"],
                reverse=True
            )
        
        # Add "Other Technologies" for languages not in predefined categories
        other_languages = []
        for lang, data in language_stats.items():
            if get_category_for_language(lang) == "Other Technologies":
                other_languages.append({
                    "language": lang,
                    "level": data.get("level", "Unknown"),
                    "total_lines": data.get("total_lines", 0),
                    "repositories": data.get("repositories", 0)
                })
        
        if other_languages:
            other_languages.sort(key=lambda x: x["total_lines"], reverse=True)
            categorized_languages["Other Technologies"] = other_languages
        
        # Remove empty categories
        categorized_languages = {
            k: v for k, v in categorized_languages.items() if v
        }
        
        return {
            "username": username,
            "top_programming_languages": top_programming_languages,
            "languages_by_category": categorized_languages,
            "total_languages": len(language_stats),
            "total_repositories": len(repositories)
        }