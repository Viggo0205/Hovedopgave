# Developer Skill Analyzer - MCP Server

A Model Context Protocol (MCP) server that analyzes developer skills based on GitHub and Jira data, with PostgreSQL database integration for persistent storage and analysis versioning.

## 🚀 Quick Setup

### 1. Install PostgreSQL
```powershell
# Download and install PostgreSQL from:
# https://www.postgresql.org/download/
# Default credentials: postgres/postgres, port 5432
```

### 2. Setup Database
```powershell
# Run the automated setup script
.\setup_database.bat

# Or manually:
psql -U postgres -c "CREATE DATABASE developer_skills;"
psql -U postgres -d developer_skills -f src\developer_skill_analyzer\db\schema.sql
```

### 3. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials:
# GITHUB_TOKEN=your_actual_github_token_here
# MOCK_MODE=false
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills
```

### 4. Install Dependencies
```powershell
pip install psycopg2-binary
pip install -r requirements.txt  # or pip install -e .
```

### 5. Test Database Connection
```powershell
python test_database.py
```

### 6. Run the MCP Client
```powershell
python mcp_client.py
```

## 🤖 Features

### MCP Server
- ✅ FastMCP server with PostgreSQL integration
- ✅ GitHub profile and repository analysis
- ✅ Jira project and issue analysis
- ✅ Skill extraction and proficiency assessment
- ✅ **Database persistence with version control**
- ✅ **Dynamic skill catalog management**
- ✅ **Analysis history tracking (max 2 versions)**
- ✅ Team expertise mapping

### Database Features
- ✅ **Persistent storage** of all analyses
- ✅ **Automatic version management** (keeps 2 versions)
- ✅ **Dynamic competence catalog** loaded from database
- ✅ **User competence tracking** with proficiency percentages
- ✅ **Skill ranking system** (Beginner/Intermediate/Advanced/Expert)
- ✅ **SQL analytics** for team insights

### Multi-AI Client
- ✅ Claude 3.5 Sonnet integration
- ✅ GPT-4 Turbo integration
- 🚧 Gemini Pro support (coming soon)
- 🚧 Local model support (Ollama)
- ✅ AI model comparison mode
- ✅ Natural language understanding

### Resources
- Developer skill profiles and assessments
- Technology usage patterns
- Collaboration metrics
- Learning progression analysis

### Prompts
- Skill assessment templates
- Developer comparison frameworks
- Growth recommendation generators

## Installation

### Prerequisites
- Python 3.9 or higher
- Git
- Access to GitHub API (personal access token)
- Access to Jira API (API token or credentials)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd developer-skill-analyzer
```

2. Install dependencies using uv:
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# GitHub API
GITHUB_ACCESS_TOKEN=your_github_token_here

# Jira API
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your_jira_api_token

# Optional: Rate limiting
API_RATE_LIMIT=100  # requests per minute
```

## Usage

### Running the Server

```bash
# Using uv
uv run dev-skill-analyzer

# Or activate virtual environment and run directly
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m developer_skill_analyzer.server
```

### Connecting to MCP Clients

#### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "developer-skill-analyzer": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/developer-skill-analyzer",
        "dev-skill-analyzer"
      ],
      "env": {
        "GITHUB_ACCESS_TOKEN": "your_token",
        "JIRA_SERVER_URL": "your_jira_url",
        "JIRA_EMAIL": "your_email",
        "JIRA_API_TOKEN": "your_jira_token"
      }
    }
  }
}
```

#### VS Code with GitHub Copilot

Configure in your VS Code MCP settings or `mcp.json`:

```json
{
  "servers": {
    "developer-skill-analyzer": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "dev-skill-analyzer"],
      "cwd": "/path/to/developer-skill-analyzer"
    }
  }
}
```

## API Examples

### Analyze GitHub Developer

```python
# Tool call example
await call_tool("analyze_github_developer", {
    "username": "octocat",
    "repositories": ["Hello-World", "git-consortium"],
    "include_contributions": True,
    "time_range_months": 12
})
```

### Analyze Jira Developer

```python
# Tool call example
await call_tool("analyze_jira_developer", {
    "email": "developer@company.com",
    "projects": ["PROJ-1", "PROJ-2"],
    "include_comments": True,
    "time_range_months": 6
})
```

## Development

### Project Structure

```
developer-skill-analyzer/
├── src/
│   └── developer_skill_analyzer/
│       ├── __init__.py
│       ├── server.py              # Main MCP server
│       ├── config.py              # Configuration management
│       ├── models/                # Data models
│       │   ├── __init__.py
│       │   ├── developer.py       # Developer profile models
│       │   ├── skills.py          # Skill models
│       │   └── analysis.py        # Analysis result models
│       ├── analyzers/             # Analysis engines
│       │   ├── __init__.py
│       │   ├── github_analyzer.py # GitHub data analysis
│       │   ├── jira_analyzer.py   # Jira data analysis
│       │   └── skill_processor.py # Skill extraction and scoring
│       ├── integrations/          # External API integrations
│       │   ├── __init__.py
│       │   ├── github_client.py   # GitHub API client
│       │   └── jira_client.py     # Jira API client
│       └── utils/                 # Utility functions
│           ├── __init__.py
│           ├── rate_limiter.py    # API rate limiting
│           └── cache.py           # Response caching
├── tests/                         # Test files
├── docs/                          # Documentation
├── .env.example                   # Environment template
├── .gitignore
├── README.md
└── pyproject.toml
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=developer_skill_analyzer

# Run specific test file
uv run pytest tests/test_github_analyzer.py
```

### Code Quality

```bash
# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8 .
uv run mypy .

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Architecture

### Skill Analysis Pipeline

1. **Data Collection**: Gather data from GitHub and Jira APIs
2. **Preprocessing**: Clean and normalize data structures
3. **Feature Extraction**: Extract relevant metrics and patterns
4. **Skill Classification**: Categorize activities into skill areas
5. **Proficiency Scoring**: Calculate skill levels based on complexity and frequency
6. **Report Generation**: Create comprehensive skill profiles

### Skill Categories

- **Programming Languages**: Python, JavaScript, Java, etc.
- **Frameworks & Tools**: React, Django, Docker, etc.
- **Soft Skills**: Communication, Leadership, Problem-solving
- **Domain Knowledge**: Web Development, Data Science, DevOps
- **Collaboration**: Code Reviews, Mentoring, Documentation

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `uv run pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built using the [Model Context Protocol](https://modelcontextprotocol.io/)
- Utilizes [FastMCP](https://gofastmcp.com/) for rapid development
- GitHub API integration via [PyGithub](https://pygithub.readthedocs.io/)
- Jira API integration via [atlassian-python-api](https://atlassian-python-api.readthedocs.io/)