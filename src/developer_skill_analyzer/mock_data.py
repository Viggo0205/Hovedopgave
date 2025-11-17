"""
Mock data for MCP server testing
"""

from datetime import datetime, timedelta
import random

# Mock GitHub data
MOCK_GITHUB_DATA = {
    "johnsmith": {
        "username": "johnsmith",
        "name": "John Smith",
        "email": "john.smith@example.com",
        "repositories": [
            {
                "name": "backend-api",
                "language": "Python",
                "stars": 45,
                "forks": 12,
                "commits": 156,
                "last_activity": "2024-11-10"
            },
            {
                "name": "web-dashboard", 
                "language": "JavaScript",
                "stars": 23,
                "forks": 8,
                "commits": 89,
                "last_activity": "2024-11-08"
            },
            {
                "name": "ml-pipeline",
                "language": "Python", 
                "stars": 67,
                "forks": 19,
                "commits": 234,
                "last_activity": "2024-11-12"
            }
        ],
        "languages": {
            "Python": 0.65,
            "JavaScript": 0.25,
            "TypeScript": 0.08,
            "SQL": 0.02
        },
        "commit_history": {
            "total_commits": 479,
            "commits_last_month": 34,
            "commits_last_year": 456,
            "average_commits_per_month": 38
        }
    },
    "sarahjohnson": {
        "username": "sarahjohnson",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "repositories": [
            {
                "name": "react-components",
                "language": "JavaScript",
                "stars": 89,
                "forks": 25,
                "commits": 203,
                "last_activity": "2024-11-11"
            },
            {
                "name": "ui-kit",
                "language": "TypeScript",
                "stars": 156,
                "forks": 43,
                "commits": 312,
                "last_activity": "2024-11-13"
            }
        ],
        "languages": {
            "JavaScript": 0.45,
            "TypeScript": 0.35,
            "CSS": 0.15,
            "HTML": 0.05
        },
        "commit_history": {
            "total_commits": 515,
            "commits_last_month": 42,
            "commits_last_year": 498,
            "average_commits_per_month": 43
        }
    },
    "mikechen": {
        "username": "mikechen",
        "name": "Mike Chen",
        "email": "mike.chen@example.com",
        "repositories": [
            {
                "name": "k8s-deployments",
                "language": "YAML",
                "stars": 34,
                "forks": 12,
                "commits": 145,
                "last_activity": "2024-11-09"
            },
            {
                "name": "docker-images",
                "language": "Dockerfile",
                "stars": 78,
                "forks": 23,
                "commits": 189,
                "last_activity": "2024-11-14"
            },
            {
                "name": "terraform-modules",
                "language": "HCL",
                "stars": 92,
                "forks": 31,
                "commits": 267,
                "last_activity": "2024-11-12"
            }
        ],
        "languages": {
            "Python": 0.30,
            "Shell": 0.25,
            "YAML": 0.20,
            "Dockerfile": 0.15,
            "HCL": 0.10
        },
        "commit_history": {
            "total_commits": 601,
            "commits_last_month": 48,
            "commits_last_year": 578,
            "average_commits_per_month": 50
        }
    }
}

# Mock Jira data
MOCK_JIRA_DATA = {
    "john.smith@example.com": {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "issues_assigned": 45,
        "issues_resolved": 42,
        "issues_created": 23,
        "comments_made": 187,
        "projects": ["BACKEND", "API", "CORE"],
        "issue_types": {
            "Bug": 18,
            "Feature": 15,
            "Task": 9,
            "Story": 3
        },
        "resolution_time_avg": 2.3,  # days
        "comment_quality_score": 0.87
    },
    "sarah.johnson@example.com": {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "issues_assigned": 38,
        "issues_resolved": 36,
        "issues_created": 19,
        "comments_made": 156,
        "projects": ["FRONTEND", "UI", "UX"],
        "issue_types": {
            "Bug": 12,
            "Feature": 20,
            "Task": 4,
            "Story": 2
        },
        "resolution_time_avg": 1.8,  # days
        "comment_quality_score": 0.92
    },
    "mike.chen@example.com": {
        "name": "Mike Chen",
        "email": "mike.chen@example.com",
        "issues_assigned": 52,
        "issues_resolved": 48,
        "issues_created": 31,
        "comments_made": 203,
        "projects": ["DEVOPS", "INFRA", "DEPLOY"],
        "issue_types": {
            "Bug": 15,
            "Feature": 8,
            "Task": 25,
            "Story": 4
        },
        "resolution_time_avg": 1.2,  # days
        "comment_quality_score": 0.85
    }
}

def get_mock_github_data(username: str):
    """Get mock GitHub data for a user"""
    username_lower = username.lower().replace(" ", "").replace("-", "").replace("_", "")
    
    # Try to find exact match first
    for mock_user in MOCK_GITHUB_DATA:
        if mock_user.lower() == username_lower:
            return MOCK_GITHUB_DATA[mock_user]
    
    # Return default mock data if not found
    return {
        "username": username,
        "name": username.replace("_", " ").replace("-", " ").title(),
        "email": f"{username.lower()}@example.com",
        "repositories": [
            {
                "name": "sample-project",
                "language": "Python",
                "stars": random.randint(10, 100),
                "forks": random.randint(2, 20),
                "commits": random.randint(50, 200),
                "last_activity": "2024-11-10"
            }
        ],
        "languages": {
            "Python": 0.60,
            "JavaScript": 0.25,
            "SQL": 0.15
        },
        "commit_history": {
            "total_commits": random.randint(100, 500),
            "commits_last_month": random.randint(10, 50),
            "commits_last_year": random.randint(200, 400),
            "average_commits_per_month": random.randint(20, 45)
        }
    }

def get_mock_jira_data(email: str):
    """Get mock Jira data for a user"""
    if email in MOCK_JIRA_DATA:
        return MOCK_JIRA_DATA[email]
    
    # Return default mock data
    return {
        "name": email.split("@")[0].replace(".", " ").title(),
        "email": email,
        "issues_assigned": random.randint(20, 60),
        "issues_resolved": random.randint(18, 55),
        "issues_created": random.randint(10, 30),
        "comments_made": random.randint(50, 200),
        "projects": ["PROJECT1", "PROJECT2"],
        "issue_types": {
            "Bug": random.randint(5, 20),
            "Feature": random.randint(8, 25),
            "Task": random.randint(3, 15),
            "Story": random.randint(1, 8)
        },
        "resolution_time_avg": round(random.uniform(1.0, 3.0), 1),
        "comment_quality_score": round(random.uniform(0.7, 0.95), 2)
    }

# Employee database for MCP tools
MOCK_EMPLOYEES = [
    {"name": "John Smith", "email": "john.smith@example.com", "github": "johnsmith", "team": "Backend"},
    {"name": "Sarah Johnson", "email": "sarah.johnson@example.com", "github": "sarahjohnson", "team": "Frontend"},
    {"name": "Mike Chen", "email": "mike.chen@example.com", "github": "mikechen", "team": "DevOps"},
    {"name": "Emily Davis", "email": "emily.davis@example.com", "github": "emilydavis", "team": "Mobile"},
    {"name": "Alex Rodriguez", "email": "alex.rodriguez@example.com", "github": "alexrodriguez", "team": "Data"},
    {"name": "Lisa Wang", "email": "lisa.wang@example.com", "github": "lisawang", "team": "Backend"},
    {"name": "David Brown", "email": "david.brown@example.com", "github": "davidbrown", "team": "Frontend"},
    {"name": "Anna Kumar", "email": "anna.kumar@example.com", "github": "annakumar", "team": "Backend"}
]

# Technical stack data
MOCK_TECHNICAL_STACK = {
    "programming_languages": [
        {"name": "Python", "usage_percentage": 75, "expertise_level": "Advanced"},
        {"name": "JavaScript", "usage_percentage": 85, "expertise_level": "Expert"},
        {"name": "TypeScript", "usage_percentage": 60, "expertise_level": "Advanced"},
        {"name": "Java", "usage_percentage": 45, "expertise_level": "Intermediate"},
        {"name": "Go", "usage_percentage": 30, "expertise_level": "Intermediate"},
        {"name": "Rust", "usage_percentage": 15, "expertise_level": "Beginner"}
    ],
    "frameworks": [
        {"name": "React", "usage_percentage": 70, "expertise_level": "Expert"},
        {"name": "Django", "usage_percentage": 55, "expertise_level": "Advanced"},
        {"name": "FastAPI", "usage_percentage": 40, "expertise_level": "Advanced"},
        {"name": "Angular", "usage_percentage": 35, "expertise_level": "Intermediate"},
        {"name": "Vue.js", "usage_percentage": 25, "expertise_level": "Intermediate"},
        {"name": "Spring Boot", "usage_percentage": 30, "expertise_level": "Intermediate"}
    ],
    "tools": [
        {"name": "Docker", "usage_percentage": 80, "expertise_level": "Advanced"},
        {"name": "Kubernetes", "usage_percentage": 60, "expertise_level": "Advanced"},
        {"name": "AWS", "usage_percentage": 70, "expertise_level": "Advanced"},
        {"name": "Git", "usage_percentage": 95, "expertise_level": "Expert"},
        {"name": "Jenkins", "usage_percentage": 50, "expertise_level": "Intermediate"},
        {"name": "Terraform", "usage_percentage": 45, "expertise_level": "Intermediate"}
    ]
}