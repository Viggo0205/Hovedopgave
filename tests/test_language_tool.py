"""
Test script for the get_developer_languages MCP tool
"""
import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from services.github_service import GitHubService
from analyzers.github_analyzer import GitHubAnalyzer


async def test_language_tool():
    """Test the get_languages_by_category analyzer method with Viggo0205"""
    print("Testing get_languages_by_category analyzer...")
    print("-" * 60)
    
    # Initialize service and analyzer
    github_service = GitHubService()
    analyzer = GitHubAnalyzer(github_service)
    
    # Test with Viggo0205 (we have their profile already)
    result = analyzer.get_languages_by_category("Viggo0205")
    
    # Pretty print the result
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Also print in the requested Danish format
    if "top_programming_languages" in result:
        print("\n" + "=" * 60)
        print("Top programmeringssprog:")
        print("=" * 60)
        for lang_info in result["top_programming_languages"]:
            print(f"\n{lang_info['language']} - {lang_info['rank']}")
            print(f"  Level: {lang_info['level']}")
            print(f"  Lines of code: {lang_info['total_lines']:,}")
            print(f"  Repositories: {lang_info['repositories']}")
    
    # Print categorized languages
    if "languages_by_category" in result:
        print("\n" + "=" * 60)
        print("Sprog efter kategorier:")
        print("=" * 60)
        for category, languages in result["languages_by_category"].items():
            print(f"\n{category}:")
            for lang in languages:
                print(f"  - {lang['language']} ({lang['level']}) - {lang['total_lines']:,} linjer i {lang['repositories']} repos")


if __name__ == "__main__":
    asyncio.run(test_language_tool())
