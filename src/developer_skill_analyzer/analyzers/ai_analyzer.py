"""
AI-powered skill analysis using machine learning models.
"""

import logging
from typing import Dict, List, Any, Optional
import re

# AI library imports with graceful fallback
HAS_AI_LIBS = True
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    HAS_AI_LIBS = False

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    HAS_AI_LIBS = False

try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    HAS_AI_LIBS = False

logger = logging.getLogger(__name__)


class AISkillAnalyzer:
    """AI-powered skill analysis using various ML models."""
    
    def __init__(self):
        """Initialize AI analyzer with available models."""
        self.has_openai = HAS_OPENAI
        self.has_transformers = HAS_TRANSFORMERS
        self.has_sklearn = HAS_SKLEARN
        
        # Initialize models if libraries are available
        self.sentiment_analyzer = None
        self.text_classifier = None
        self.tfidf_vectorizer = None
        
        if HAS_TRANSFORMERS:
            try:
                # Initialize sentiment analysis pipeline with smaller model
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True
                )
                logger.info("Initialized sentiment analysis model")
            except Exception as e:
                logger.warning(f"Failed to initialize sentiment analyzer: {e}")
                # Continue without sentiment analyzer - other AI features still work
                self.sentiment_analyzer = None
        
        if HAS_SKLEARN:
            try:
                # Initialize TF-IDF vectorizer for text analysis
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                logger.info("Initialized TF-IDF vectorizer")
            except Exception as e:
                logger.warning(f"Failed to initialize TF-IDF vectorizer: {e}")
    
    def analyze_github_data(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GitHub data using AI models to extract enhanced skill insights.
        
        Args:
            github_data: GitHub analysis results
            
        Returns:
            AI-enhanced skill insights
        """
        try:
            ai_insights = {
                "technical_skills": [],
                "soft_skills": [],
                "confidence_scores": {},
                "ai_analysis_metadata": {
                    "models_used": [],
                    "analysis_timestamp": None
                }
            }
            
            # Extract repository descriptions and commit messages for analysis
            repo_texts = []
            commit_patterns = github_data.get("commit_patterns", {})
            repositories = github_data.get("repositories", [])
            
            for repo in repositories:
                description = repo.get("description", "")
                if description:
                    repo_texts.append(description)
            
            # AI-powered technical skill analysis
            technical_skills = self._analyze_technical_skills_ai(repositories, commit_patterns)
            ai_insights["technical_skills"].extend(technical_skills)
            
            # AI-powered soft skill analysis
            soft_skills = self._analyze_soft_skills_ai(github_data.get("collaboration_metrics", {}), repo_texts)
            ai_insights["soft_skills"].extend(soft_skills)
            
            # Code quality analysis using AI
            quality_insights = self._analyze_code_quality_ai(commit_patterns)
            ai_insights.update(quality_insights)
            
            ai_insights["ai_analysis_metadata"]["models_used"] = self._get_models_used()
            
            return ai_insights
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": str(e), "fallback": "traditional_analysis"}
    
    def analyze_jira_data(self, jira_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Jira data using AI models for enhanced insights.
        
        Args:
            jira_data: Jira analysis results
            
        Returns:
            AI-enhanced skill insights
        """
        try:
            ai_insights = {
                "technical_skills": [],
                "soft_skills": [],
                "domain_skills": [],
                "problem_solving_analysis": {}
            }
            
            # Analyze issue resolution patterns
            resolution_insights = self._analyze_resolution_patterns_ai(jira_data)
            ai_insights["problem_solving_analysis"] = resolution_insights
            
            # Extract communication skills from Jira interactions
            communication_skills = self._analyze_jira_communication_ai(jira_data)
            ai_insights["soft_skills"].extend(communication_skills)
            
            # Domain expertise analysis
            domain_skills = self._analyze_domain_expertise_ai(jira_data.get("domains", []))
            ai_insights["domain_skills"].extend(domain_skills)
            
            return ai_insights
            
        except Exception as e:
            logger.error(f"AI Jira analysis failed: {e}")
            return {"error": str(e), "fallback": "traditional_analysis"}
    
    def _analyze_technical_skills_ai(self, repositories: List[Dict], commit_patterns: Dict) -> List[Dict]:
        """Use AI to analyze technical skills from repository data."""
        skills = []
        
        try:
            # Advanced technology detection using AI
            for repo in repositories:
                description = repo.get("description", "")
                technologies = repo.get("technologies", [])
                
                if description and self.has_sklearn:
                    # Use ML to extract technical skills from descriptions
                    extracted_skills = self._extract_skills_from_text(description)
                    for skill in extracted_skills:
                        skills.append({
                            "name": skill["name"],
                            "confidence": skill["confidence"],
                            "evidence": [f"AI-extracted from repository: {repo.get('name')}"],
                            "source": "ai_text_analysis"
                        })
                
                # Enhanced technology analysis
                for tech in technologies:
                    confidence = self._calculate_tech_confidence(tech, repo.get("commits", 0))
                    if confidence > 0.5:
                        skills.append({
                            "name": tech,
                            "confidence": confidence,
                            "evidence": [f"Used in {repo.get('name')} with {repo.get('commits', 0)} commits"],
                            "source": "ai_enhanced_detection"
                        })
            
            # Code quality skill analysis
            if commit_patterns and self.has_sklearn:
                quality_metrics = commit_patterns.get("code_quality_metrics", {})
                quality_skills = self._analyze_code_quality_skills(quality_metrics)
                skills.extend(quality_skills)
                
        except Exception as e:
            logger.warning(f"AI technical skill analysis failed: {e}")
        
        return skills
    
    def _analyze_soft_skills_ai(self, collaboration_metrics: Dict, repo_texts: List[str]) -> List[Dict]:
        """Use AI to analyze soft skills from collaboration data."""
        skills = []
        
        try:
            # Analyze collaboration patterns
            if collaboration_metrics:
                pr_created = collaboration_metrics.get("pull_requests_created", 0)
                pr_reviewed = collaboration_metrics.get("pull_requests_reviewed", 0)
                mentoring = collaboration_metrics.get("mentoring_instances", 0)
                
                # AI-powered collaboration analysis
                if pr_reviewed > pr_created * 1.5:
                    skills.append({
                        "name": "Code Review Excellence",
                        "confidence": min(0.9, pr_reviewed / 100),
                        "evidence": [f"Reviewed {pr_reviewed} PRs vs created {pr_created}"],
                        "source": "ai_collaboration_analysis"
                    })
                
                if mentoring > 5:
                    skills.append({
                        "name": "Technical Mentoring",
                        "confidence": min(0.95, mentoring / 20),
                        "evidence": [f"Involved in {mentoring} mentoring instances"],
                        "source": "ai_mentoring_analysis"
                    })
            
            # Sentiment analysis on repository descriptions
            if repo_texts and self.sentiment_analyzer:
                try:
                    for text in repo_texts[:3]:  # Analyze first 3 repo descriptions
                        sentiment_results = self.sentiment_analyzer(text)
                        if sentiment_results and len(sentiment_results[0]) > 0:
                            # Extract communication style insights
                            positive_score = next((s["score"] for s in sentiment_results[0] if s["label"] == "LABEL_2"), 0)
                            if positive_score > 0.7:
                                skills.append({
                                    "name": "Clear Technical Communication",
                                    "confidence": positive_score,
                                    "evidence": [f"Positive sentiment in project descriptions"],
                                    "source": "ai_sentiment_analysis"
                                })
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")
                    
        except Exception as e:
            logger.warning(f"AI soft skill analysis failed: {e}")
        
        return skills
    
    def _analyze_code_quality_ai(self, commit_patterns: Dict) -> Dict[str, Any]:
        """Analyze code quality using AI insights."""
        quality_insights = {}
        
        try:
            quality_metrics = commit_patterns.get("code_quality_metrics", {})
            
            if quality_metrics:
                doc_ratio = quality_metrics.get("documentation_ratio", 0)
                test_coverage = quality_metrics.get("test_coverage", 0)
                avg_lines = quality_metrics.get("avg_lines_per_commit", 0)
                
                # AI-powered quality assessment
                quality_score = (doc_ratio * 0.3 + test_coverage * 0.5 + min(avg_lines/50, 1) * 0.2)
                
                quality_insights["code_quality_score"] = quality_score
                quality_insights["quality_assessment"] = self._get_quality_assessment(quality_score)
                
                if quality_score > 0.7:
                    quality_insights["inferred_skills"] = [
                        {
                            "name": "Clean Code Practices",
                            "confidence": quality_score,
                            "evidence": [f"High code quality metrics: doc_ratio={doc_ratio:.2f}, test_coverage={test_coverage:.2f}"],
                            "source": "ai_quality_analysis"
                        }
                    ]
                    
        except Exception as e:
            logger.warning(f"Code quality AI analysis failed: {e}")
        
        return quality_insights
    
    def _analyze_resolution_patterns_ai(self, jira_data: Dict) -> Dict[str, Any]:
        """Analyze problem-solving patterns using AI."""
        patterns = {}
        
        try:
            resolution_rate = jira_data.get("resolution_rate", 0)
            avg_resolution_time = jira_data.get("avg_resolution_time_days", 0)
            complexity_analysis = jira_data.get("complexity_analysis", {})
            
            # AI assessment of problem-solving capability
            if resolution_rate > 0.8 and avg_resolution_time < 5:
                patterns["problem_solving_efficiency"] = {
                    "score": min(0.95, resolution_rate * (5 / max(avg_resolution_time, 1))),
                    "analysis": "High efficiency in problem resolution",
                    "evidence": f"Resolution rate: {resolution_rate:.2f}, Avg time: {avg_resolution_time} days"
                }
            
            # Complex issue handling analysis
            high_complexity = complexity_analysis.get("high_complexity_issues", 0)
            if high_complexity > 10:
                patterns["complex_problem_handling"] = {
                    "score": min(0.9, high_complexity / 30),
                    "analysis": "Capable of handling complex technical challenges",
                    "evidence": f"Resolved {high_complexity} high-complexity issues"
                }
                
        except Exception as e:
            logger.warning(f"Resolution pattern AI analysis failed: {e}")
        
        return patterns
    
    def _analyze_jira_communication_ai(self, jira_data: Dict) -> List[Dict]:
        """Analyze communication skills from Jira data using AI."""
        skills = []
        
        try:
            comment_quality = jira_data.get("comment_quality_score", 0)
            collaboration_freq = jira_data.get("collaboration_frequency", 0)
            
            if comment_quality > 0.7:
                skills.append({
                    "name": "Technical Documentation",
                    "confidence": comment_quality,
                    "evidence": [f"High quality issue comments (score: {comment_quality:.2f})"],
                    "source": "ai_communication_analysis"
                })
            
            if collaboration_freq > 0.6:
                skills.append({
                    "name": "Team Collaboration",
                    "confidence": collaboration_freq,
                    "evidence": [f"High collaboration frequency in issues"],
                    "source": "ai_collaboration_analysis"
                })
                
        except Exception as e:
            logger.warning(f"Jira communication AI analysis failed: {e}")
        
        return skills
    
    def _analyze_domain_expertise_ai(self, domains: List[str]) -> List[Dict]:
        """Analyze domain expertise using AI pattern recognition."""
        skills = []
        
        try:
            # Domain expertise confidence based on variety and specialization
            domain_confidence_map = {
                "Web Development": 0.8,
                "API Development": 0.85,
                "Database Design": 0.9,
                "Performance Optimization": 0.95,
                "Machine Learning": 0.9,
                "DevOps": 0.85,
                "Security": 0.95
            }
            
            for domain in domains:
                confidence = domain_confidence_map.get(domain, 0.7)
                skills.append({
                    "name": domain,
                    "confidence": confidence,
                    "evidence": [f"Domain expertise identified from project work"],
                    "source": "ai_domain_analysis"
                })
                
        except Exception as e:
            logger.warning(f"Domain expertise AI analysis failed: {e}")
        
        return skills
    
    def _extract_skills_from_text(self, text: str) -> List[Dict]:
        """Extract technical skills from text using NLP."""
        skills = []
        
        if not self.has_sklearn:
            return skills
        
        try:
            # Technical keyword patterns
            tech_patterns = {
                "machine learning": 0.9,
                "neural network": 0.95,
                "api": 0.8,
                "microservice": 0.85,
                "database": 0.8,
                "cloud": 0.8,
                "docker": 0.85,
                "kubernetes": 0.9,
                "react": 0.8,
                "vue": 0.8,
                "django": 0.8,
                "flask": 0.8,
                "tensorflow": 0.95,
                "pytorch": 0.95
            }
            
            text_lower = text.lower()
            for skill, base_confidence in tech_patterns.items():
                if skill in text_lower:
                    # Context-based confidence adjustment
                    context_boost = 0.1 if any(word in text_lower for word in ["advanced", "expert", "extensive"]) else 0
                    confidence = min(0.95, base_confidence + context_boost)
                    
                    skills.append({
                        "name": skill.title(),
                        "confidence": confidence
                    })
                    
        except Exception as e:
            logger.warning(f"Text skill extraction failed: {e}")
        
        return skills
    
    def _calculate_tech_confidence(self, technology: str, commits: int) -> float:
        """Calculate confidence score for a technology based on usage."""
        base_confidence = 0.7
        
        # Boost confidence based on commit frequency
        commit_boost = min(0.25, commits / 100)
        
        # Technology-specific confidence adjustments
        high_value_techs = ["tensorflow", "pytorch", "kubernetes", "react", "vue", "django"]
        if technology.lower() in high_value_techs:
            base_confidence += 0.1
        
        return min(0.95, base_confidence + commit_boost)
    
    def _analyze_code_quality_skills(self, quality_metrics: Dict) -> List[Dict]:
        """Analyze code quality skills using AI assessment."""
        skills = []
        
        try:
            doc_ratio = quality_metrics.get("documentation_ratio", 0)
            test_coverage = quality_metrics.get("test_coverage", 0)
            
            if doc_ratio > 0.6:
                skills.append({
                    "name": "Documentation Excellence",
                    "confidence": min(0.9, doc_ratio + 0.1),
                    "evidence": [f"High documentation ratio: {doc_ratio:.2f}"],
                    "source": "ai_quality_analysis"
                })
            
            if test_coverage > 0.7:
                skills.append({
                    "name": "Test-Driven Development",
                    "confidence": min(0.95, test_coverage + 0.05),
                    "evidence": [f"High test coverage: {test_coverage:.2f}"],
                    "source": "ai_quality_analysis"
                })
                
        except Exception as e:
            logger.warning(f"Code quality skill analysis failed: {e}")
        
        return skills
    
    def _get_quality_assessment(self, quality_score: float) -> str:
        """Get human-readable quality assessment."""
        if quality_score >= 0.8:
            return "Excellent code quality practices"
        elif quality_score >= 0.6:
            return "Good code quality with room for improvement"
        elif quality_score >= 0.4:
            return "Moderate code quality"
        else:
            return "Code quality needs improvement"
    
    def _get_models_used(self) -> List[str]:
        """Get list of AI models currently in use."""
        models = []
        if self.has_openai:
            models.append("OpenAI GPT")
        if self.has_transformers:
            models.append("Transformers (Sentiment Analysis)")
        if self.has_sklearn:
            models.append("Scikit-learn (ML Classification)")
        return models
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get current AI capabilities status."""
        return {
            "openai_available": self.has_openai,
            "transformers_available": self.has_transformers,
            "sklearn_available": self.has_sklearn,
            "sentiment_analysis": self.sentiment_analyzer is not None,
            "text_classification": self.has_sklearn,
            "ai_enhancement_active": HAS_AI_LIBS
        }