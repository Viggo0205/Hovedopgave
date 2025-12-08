"""GitHub analyzer for analyzing and processing GitHub data."""

from typing import Dict, Any
from collections import defaultdict
from services.github_service import GitHubService
from models.analysis import GitHubAnalysisResult
from shared.language_categories import LANGUAGE_CATEGORIES



class GitHubAnalyzer:
    """Analyzes GitHub data to extract skills and insights."""
    
    def __init__(self, github_service: GitHubService):
        self.github_service = github_service
    
    async def analyze_developer(self, username: str) -> Dict[str, Any]:
        """Analyze developer skills based on GitHub data."""
        
        # Get raw data from service
        profile = self.github_service.get_user_profile(username)
        repositories = self.github_service.get_user_repositories(username)
        language_data = self.github_service.get_language_data(repositories)
        
        # ANALYSIS LOGIC HERE - using data from service
        language_stats = self._analyze_language_skills(language_data, repositories)
        expertise_areas = self._categorize_from_language_stats(language_stats)
        
        return {
            "username": username,
            "profile": profile,
            "language_skills": language_stats,
            "expertise_areas": expertise_areas,
            "total_repositories": len(repositories)
        }
    
    async def analyze_developer_full(self, username: str) -> GitHubAnalysisResult:
        """Analyze developer and return structured GitHubAnalysisResult object."""
        # Get raw data from service
        profile = self.github_service.get_user_profile(username)
        repositories = self.github_service.get_user_repositories(username)
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
        profile = self.github_service.get_user_profile(username)
        repositories = self.github_service.get_user_repositories(username)
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