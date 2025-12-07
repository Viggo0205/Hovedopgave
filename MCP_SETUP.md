# MCP Server Setup Guide
## 🚀 Quick Start - Developer Skill Analyzer

This MCP server analyzes developer skills based on GitHub activity using FastMCP.

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure GitHub Token
Create a `.env` file in the project root:
```bash
# .env file (create from .env.example)
GITHUB_TOKEN=your_github_personal_access_token_here
```

**Get GitHub Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` and `user` scopes
3. Copy token to `.env` file

### 3. Claude Desktop Integration
Add this to your Claude Desktop configuration (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "developer-skill-analyzer": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "C:\\path\\to\\your\\Hovedopgave",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\your\\Hovedopgave\\src"
      }
    }
  }
}
```

**Replace `C:\\path\\to\\your\\Hovedopgave` with your actual project path!**

### 4. Available MCP Tools
Once connected, Claude Desktop will have access to these tools:

- **analyze_github_developer**: Comprehensive GitHub profile analysis
  - Programming languages and skill levels (Expert/Advanced/Intermediate/Beginner)
  - Repository count and activity metrics
  - Expertise area categorization (Web Frontend, Backend, Mobile, etc.)

- **get_github_profile**: Quick GitHub profile lookup
  - Basic profile information
  - Top 3 programming languages
  - Repository statistics

- **compare_developers**: Side-by-side developer comparison
  - Language skills comparison
  - Repository and activity differences
  - Individual skill assessments

### 5. Available MCP Resources
- **github://available-languages**: List of all supported programming languages and categories

### 6. Available MCP Prompts
- **analyze-developer-skills**: Template for comprehensive developer skill analysis

### 7. Example Claude Desktop Usage
```
You: Analyze the GitHub developer "octocat"
Claude: I'll analyze octocat's GitHub profile using the developer skill analyzer.
[Uses analyze_github_developer tool with real GitHub API data]

You: Compare developers "torvalds" and "gvanrossum"
Claude: I'll compare their GitHub skill profiles.
[Uses compare_developers tool]

You: Show me available programming languages
Claude: Here are the supported programming languages...
[Uses github://available-languages resource]
```

## 🏗️ Architecture
```
Claude Desktop → MCP Protocol → src/mcp/server.py → GitHubAnalyzer → GitHubService → GitHub API
                                                  ↓
                                            Language Categories (shared)
```

### Project Structure:
```
src/
├── mcp/
│   └── server.py           # FastMCP server with tools/resources/prompts
├── analyzers/
│   ├── github_analyzer.py  # Business logic for GitHub analysis
│   └── jira_analyzer.py    # Business logic for Jira analysis (future)
├── services/
│   ├── github_service.py   # Raw GitHub API data fetching
│   └── jira_service.py     # Raw Jira API data fetching (future)
├── models/
│   ├── analysis.py         # Pydantic models for analysis results
│   └── skills.py           # Skill-related models
└── shared/
    ├── config.py           # Environment configuration
    └── language_categories.py  # Programming language categorization
```

## 🔧 Supported Programming Languages
The system categorizes languages into expertise areas:

- **Programming Languages**: Python, Java, JavaScript, C#, C++, Go, Ruby, PHP, Swift, Kotlin
- **Web Frontend**: HTML, CSS, TypeScript, Vue, React, Angular  
- **Backend/Server**: Node.js, Django, Flask, Spring, ASP.NET
- **Mobile Development**: Swift, Kotlin, Dart, React Native, Flutter
- **Data/Analytics**: R, MATLAB, Jupyter Notebook, SQL

## ✅ Testing Your Setup

### Test 1: Import Check
```powershell
python -c "from src.mcp.server import main; print('✅ Server imports successfully')"
```

### Test 2: Claude Desktop Test
1. Restart Claude Desktop after adding configuration
2. Type: "Analyze the GitHub developer 'octocat'"
3. If working, Claude will use your MCP tools and return analysis

### Test 3: Check Available Tools
In Claude Desktop, ask: "What MCP tools do you have access to?"

## 🚨 Troubleshooting

**"MCP server not available":**
- Check Claude Desktop configuration path is correct
- Ensure virtual environment is activated
- Verify `.env` file exists with valid GitHub token

**"Import errors":**
- Check PYTHONPATH in Claude Desktop config
- Ensure all dependencies are installed

**"GitHub API rate limit":**
- Verify GitHub token is valid
- Check token has correct permissions (repo, user scopes)

Your MCP server is now ready to analyze developer skills directly in Claude Desktop! 🎯
