# Developer Skill Analyzer

An MCP (Model Context Protocol) server that analyzes developer skills by examining GitHub and Jira activity. All analysis data is stored in PostgreSQL, enabling historical tracking and skill evolution over time.

## 🚀 What It Does

- **GitHub Analysis** - Analyzes code repositories, contributions, and commit patterns to identify technical skills
- **Jira Analysis** - Extracts insights from ticket history and project involvement
- **Skill Assessment** - Automatically categorizes and quantifies skill proficiency levels
- **PostgreSQL Database** - Persistent storage with comprehensive schema for tracking developer profiles
- **Profile Comparison** - Side-by-side comparison of multiple developers
- **Automatic Updates** - Scheduled profile updates via pgAgent for maintaining current data
- **Rate Limiting** - Intelligent GitHub API rate limit handling
- **MCP Integration** - Seamless integration with Claude Desktop and other MCP-compatible tools

## 📚 Documentation

### Getting Started
- **[Setup Guide](docs/SETUP_GUIDE.md)** - ⭐ **START HERE!** Step-by-step setup instructions
- [Quick Start](#quick-start) - Skip the details if you know what you're doing

### Technical Docs
- **[API Reference](docs/USER_STORY_DATAANALYST_IMPLEMENTATION.md)** - Available MCP tools and how to use them

### Legacy Documentation
<details>
<summary>Click to expand (superseded by Complete Setup Guide)</summary>

- MCP_SETUP.md
- DATABASE_SETUP.md
- CLAUDE_DESKTOP_SETUP.md
- AUTOMATIC_UPDATE_GUIDE.md
- TESTING_QUICKSTART.md
- DATABASE_QUICK_REFERENCE.md
- DATABASE_IMPLEMENTATION_SUMMARY.md

</details>

## 📁 Project Structure

```
Hovedopgave/
├── docs/                          # 📚 Documentation
│   └── (moved to root)
│
├── src/                           # 🐍 Python source code
│   ├── analyzers/                # Analysis engines
│   │   ├── github_analyzer.py    # GitHub API analysis
│   │   ├── jira_analyzer.py      # Jira API analysis
│   │   └── skill_processor.py    # Skill extraction
│   ├── db/                       # Database layer
│   │   ├── schema.sql            # Main database schema
│   │   ├── auto_update_schema.sql # Auto-update schema
│   │   ├── connection.py         # Connection pooling
│   │   └── repository.py         # Data access layer
│   ├── models/                   # Data models
│   ├── services/                 # API services
│   ├── shared/                   # Shared utilities
│   ├── config.py                 # Configuration
│   └── server.py                 # MCP server
│
├── scripts/                       # 🔧 Utility scripts
│   ├── database/                 # Database utilities
│   ├── pgagent/                  # Auto-update scripts
│   └── utilities/
│       └── setup_claude_desktop.py
│
├── tests/                         # 🧪 Test suite (44 tests)
│   ├── test_db_connection.py     # Connection tests (12)
│   ├── test_db_repository.py     # Repository tests (21)
│   └── test_db_integration.py    # Integration tests (11)
│
├── .env                          # 🔐 Environment variables
├── pyproject.toml                # Python dependencies
└── README.md                     # This file
```

## ⚡ Quick Start

> **First time here?** Check out the [Setup Guide](docs/SETUP_GUIDE.md) for step-by-step instructions

### Prerequisites
- PostgreSQL 18.1 or newer
- Python 3.10 or newer
- GitHub Personal Access Token (classic with `repo` and `user` scopes)
- (Optional) Jira API credentials for Jira analysis

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave

# 2. Install dependencies using UV
uv sync

# 3. Configure environment variables
# Copy .env.example to .env and add your credentials
# GITHUB_TOKEN=your_github_token_here
# DATABASE_URL=postgresql://postgres:password@localhost:5432/developer_skills

# 4. Initialize database
python setup_database_complete.py

# 5. Verify everything works
pytest tests/ -v
```

For detailed step-by-step instructions, see [SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

### Using It with Claude Desktop

```bash
# Setup Claude Desktop integration
python scripts/utilities/setup_claude_desktop.py

# Restart Claude Desktop, then ask Claude:
# "Analyze developer username123 from GitHub"
```
Available MCP Tools

### Analysis Tools
- `analyze_github_developer` - Comprehensive GitHub profile analysis with skill extraction
- `analyze_jira_developer` - Analyze Jira activity to extract technical and project skills
- `get_github_profile` - Retrieve basic GitHub user information
- `compare_developers` - Side-by-side comparison of multiple developer profiles

### Database Tools
- `save_analysis_to_database` - Persist analysis results to PostgreSQL
- `get_user_competence_overview` - Retrieve complete developer skill profile
- `get_all_competences` - List all competencies tracked in the system
- `remove_developer` - Remove developer data from database (GDPR-compliant)

### Export Tools
- `export_developer_profile` - Export developer data in JSON format (privacy-safe

### Export Tools
- `export_developer_profile` - Export developer data (GDPR-compliant)
python -m pytest tests/test_db_connection.py -v

# See how much code is covered
python -m pytest tests/ --cov=src --cov-report=html
```

**What we're testing:**
- ✅ Database connections and pooling (15 tests)
- ✅ CRUD operations (27 tests)
- ✅ Stored procedures and triggers (11 tests)
- ✅ GitHub API rate limiting
- ✅ Skill extraction logic
- ✅ Data sanitization (keeping private stuff private)

## 🗄️ Database Schema

### The Main Tables
- `users` - Where we keep developer info (GitHub/Jira usernames)
- `competence` - All the skills we track, organized by category
- `rank` - Skill levels from Beginner to Expert
- `user_competence` - Who knows what, and how well (percentages)
- `analysis_archive` - History of past analyses (keeps last 2 versions)

### Helpful Views
- `user_competence_overview` - Everything about a user's skills in one place
- `competence_categories` - Skills organized by type
- `v_update_status` - Check when auto-updates last ran

Want to see the SQL? Check `src/db/schema.sql`.

## 🔄 Automatic Updates (Optional)

Want profiles to update themselves? Set up pgAgent:

```powershell
# Install pgAgent
.\scripts\pgagent\setup_pgagent.ps1

# Add the update jobs to your database
psql -U postgres -d developer_skills -f src\db\auto_update_schema.sql

# See when updates last ran
psql -U postgres -d developer_skills -c "SELECT * FROM v_update_status;"
```

Need more details? The [Setup Guide](docs/SETUP_GUIDE.md) has you covered.

## 📊 How It Works in Practice

### Using Claude Desktop

Just talk to Claude naturally:

```
You: "Analyze Viggo0205's GitHub profile"

Claude: [Uses analyze_github_developer tool]

Results:
✓ Primary Languages: C# (Expert), Python (Advanced)
✓ 15 repositories analyzed
✓ 3,500+ commits
✓ Specialization: Game Development

💾 Want to save this for later?
Just ask: "Save this analysis to the database"
```

### Using Python Directly

If you want to use it in your own code:

```python
from analyzers.github_analyzer import GitHubAnalyzer
from services.github_service import GitHubService
import asyncio

async def analyze_developer(username):
    service = GitHubService()
    analyzer = GitHubAnalyzer(service)
    result = await analyzer.analyze_developer(username)
    return result

# Run it
result = asyncio.run(analyze_developer('Viggo0205'))
print(result['language_skills'])
```

## 🔐 Privacy & Security

We take this stuff seriously:

- ✅ **No personal info in exports** - GDPR-compliant, we strip out the sensitive bits
- ✅ **API keys in .env only** - Never hardcoded, never committed to Git
- ✅ **Safe SQL queries** - Parameterized to prevent injection attacks
- ✅ **Rate limiting** - We respect API limits and won't spam GitHub
- ✅ **Git-ignored secrets** - Your .env file never gets checked in

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run test suite: `pytest tests/ -v`
5. Commit changes: `git commit -m "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Submit pull request

## 📝 License

This project is part of a thesis on developer skill analysis. See supervisor for usage terms.

## 🐛 When Things Go Wrong

### Database won't connect
MIT License - This project is developed as part of a thesis on developer skill analysis at IT-University of Copenhagen.

## 🎓 Academic Context

This project serves as the implementation component of a master's thesis investigating automated developer skill assessment through activity analysis. The research explores how machine learning and API analysis can provide objective, data-driven insights into developer competencie
# Is PostgreSQL running?
Get-Service postgresql-x64-18

# Check your .env file has the right connection info
DATABASE_URL=postgresql://postgres:password@localhost:5432/developer_skills
```

### MCP server won't start
```powershell
# Try running it directly to see errors
cd e:\Nymappe\Hovedopgave
$env:PYTHONPATH = "e:\Nymappe\Hovedopgave\src"
python -m server

# Make sure Claude Desktop config is right
cat $env:APPDATA\Claude\claude_desktop_config.json
```

### Tests are failing
```powershell
# Start fresh with the test database
psql -U postgres -c "DROP DATABASE IF EXISTS developer_skills_test;"

# Run tests again (they'll recreate it)
pytest tests/ -v
```

Still stuck? Check the [Setup Guide - Troubleshooting](docs/SETUP_GUIDE.md#troubleshooting) section.

### Database connection issues
```powershell
# Check your .env file has correct credentials
cat .env

# Verify PostgreSQL is running
Get-Service postgresql-x64-18
```

### MCP server not connecting
```powershell
# Verify Claude Desktop config
cat $env:APPDATA\Claude\claude_desktop_config.json

# Run setup again
python scripts/utilities/setup_claude_desktop.py
```

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for more solutions.

## 📞 Support

For detailed setup instructions, see:
- **[Setup Guide](docs/SETUP_GUIDE.md)**

For issues, check:
- GitHub Issues: https://github.com/Viggo0205/Hovedopgave/issues
- Thesis supervisor contact information

---

**Made with ❤️ for developer skill analysis**
