import sys
import os
from pathlib import Path

# Set environment to force real mode
os.environ["MOCK_MODE"] = "false"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from developer_skill_analyzer.config import Config
from developer_skill_analyzer.analyzers.github_analyzer import GitHubAnalyzer
import asyncio

async def analyze_viggo_github():
    print("?? ANALYZING VIGGO0205 REAL GITHUB DATA")
    print("=" * 50)
    
    # Force reload config with real mode
    config = Config()
    print(f"Mock mode: {config.mock_mode}")
    print(f"GitHub token: {config.github_token[:10]}... configured")
    
    if not config.github_token:
        print("? No GitHub token found")
        return
    
    try:
        # Initialize GitHub analyzer with real data
        analyzer = GitHubAnalyzer(config.github_token)
        
        print("\n?? Starting analysis of Viggo0205...")
        
        # Analyze your GitHub profile
        result = await analyzer.analyze_developer(
            username="Viggo0205",
            repositories=None,  # Analyze all repos
            include_contributions=True,
            time_range_months=12
        )
        
        print("\n?? ANALYSIS RESULTS:")
        print("=" * 30)
        
        # Print key findings
        if "programming_languages" in result:
            print("?? PROGRAMMING LANGUAGES:")
            for lang, data in result["programming_languages"].items():
                if isinstance(data, dict) and "proficiency_score" in data:
                    print(f"   {lang}: {data['proficiency_score']}/100")
                else:
                    print(f"   {lang}: {data}")
        
        if "repositories_analyzed" in result:
            print(f"\n?? REPOSITORIES ANALYZED: {result['repositories_analyzed']}")
        
        if "total_commits" in result:
            print(f"?? TOTAL COMMITS: {result['total_commits']}")
            
        if "collaboration_score" in result:
            print(f"?? COLLABORATION SCORE: {result['collaboration_score']}")
        
        return result
        
    except Exception as e:
        print(f"? Error analyzing GitHub data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(analyze_viggo_github())
