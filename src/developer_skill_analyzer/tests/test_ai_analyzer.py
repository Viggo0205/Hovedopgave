import pytest
from developer_skill_analyzer.analyzers.ai_analyzer import AISkillAnalyzer

@pytest.fixture
def analyzer():
    return AISkillAnalyzer()

def test_capabilities_flags(analyzer):
    caps = analyzer.get_capabilities()
    assert "openai_available" in caps
    assert "transformers_available" in caps
    assert "sklearn_available" in caps
    assert isinstance(caps["ai_enhancement_active"], bool)

def test_analyze_github_data_returns_expected_keys(analyzer):
    mock_data = {
        "repositories": [
            {
                "name": "TestRepo",
                "description": "A machine learning project using TensorFlow and Docker",
                "technologies": ["TensorFlow", "Docker"],
                "commits": 120
            }
        ],
        "commit_patterns": {
            "code_quality_metrics": {
                "documentation_ratio": 0.7,
                "test_coverage": 0.8,
                "avg_lines_per_commit": 40
            }
        },
        "collaboration_metrics": {
            "pull_requests_created": 10,
            "pull_requests_reviewed": 25,
            "mentoring_instances": 6
        }
    }

    result = analyzer.analyze_github_data(mock_data)
    assert "technical_skills" in result
    assert "soft_skills" in result
    assert "code_quality_score" in result
    assert isinstance(result["technical_skills"], list)
    # Case-insensitive check
    assert any(skill["name"].lower() == "tensorflow" for skill in result["technical_skills"])

def test_analyze_jira_data_returns_expected_keys(analyzer):
    mock_data = {
        "resolution_rate": 0.9,
        "avg_resolution_time_days": 3,
        "complexity_analysis": {"high_complexity_issues": 15},
        "comment_quality_score": 0.8,
        "collaboration_frequency": 0.7,
        "domains": ["Web Development", "Security"]
    }

    result = analyzer.analyze_jira_data(mock_data)
    assert "technical_skills" in result
    assert "soft_skills" in result
    assert "domain_skills" in result
    assert "problem_solving_analysis" in result
    assert any(skill["name"] == "Security" for skill in result["domain_skills"])

def test_extract_skills_from_text(analyzer):
    text = "This project uses advanced neural network and Docker for deployment."
    skills = analyzer._extract_skills_from_text(text)
    names = [s["name"] for s in skills]
    assert "Neural Network" in names
    assert "Docker" in names

def test_calculate_tech_confidence(analyzer):
    confidence = analyzer._calculate_tech_confidence("TensorFlow", commits=200)
    assert confidence > 0.7
    assert confidence <= 0.95

def test_quality_assessment(analyzer):
    assert analyzer._get_quality_assessment(0.85) == "Excellent code quality practices"
    assert analyzer._get_quality_assessment(0.65) == "Good code quality with room for improvement"
    assert analyzer._get_quality_assessment(0.45) == "Moderate code quality"
    assert analyzer._get_quality_assessment(0.2) == "Code quality needs improvement"
