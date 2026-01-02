"""Test skill extraction from GitHub analysis"""
import sys
sys.path.insert(0, 'e:\\Nymappe\\Hovedopgave\\src')

from analyzers.github_analyzer import GitHubAnalyzer
from services.github_service import GitHubService
from analyzers.skill_processor import SkillProcessor
import asyncio

async def test():
    # Get GitHub analysis
    service = GitHubService()
    analyzer = GitHubAnalyzer(service)
    result = await analyzer.analyze_developer('Jonasosa')
    
    print('=== GitHub Analysis Result ===')
    print('language_skills:', result.get('language_skills'))
    
    # Process with skill processor
    processor = SkillProcessor()
    skills = processor.process_github_data(result)
    
    print('\n=== Skill Processor Output ===')
    print('Technical skills found:', len(skills.get('technical_skills', [])))
    for skill in skills.get('technical_skills', []):
        print(f"  - {skill['name']}: {skill['level']} (confidence: {skill['confidence_score']:.2f}, usage: {skill['usage_frequency']})")
    
asyncio.run(test())
