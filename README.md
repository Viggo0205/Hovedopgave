# Developer Skill Analyzer

This is an MCP server that figures out what developers are good at by looking at their GitHub and Jira activity. Everything gets stored in PostgreSQL so you can track how skills evolve over time.

## 🚀 What It Does

- **GitHub Analysis** - Looks at your code, repos, and contributions to see what you're working with
- **Jira Analysis** - Pulls insights from your tickets and project work
- **Skill Assessment** - Automatically categorizes skills and figures out how good you are at them
- **Database Storage** - Keeps everything in PostgreSQL so nothing gets lost
- **Profile Comparison** - Compare different developers side-by-side
- **Automatic Updates** - Set it and forget it - profiles update themselves via pgAgent
- **Rate Limiting** - Plays nice with GitHub's API limits
- **MCP Integration** - Works with Claude Desktop and other MCP tools right out of the box

## 📚 Documentation

### Getting Started
- **[Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md)** - ⭐ **START HERE!** Everything you need to get running
- [Quick Start](#quick-start) - Skip the handholding if you've done this before

### Technical Docs
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - All the SQL and database stuff
- **[Database Testing](docs/DATABASE_TESTING.md)** - How to run the tests (53 of them!)
- **[Rate Limiting](docs/RATE_LIMITING.md)** - How we handle API rate limits
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
│   ├── COMPLETE_SETUP_GUIDE.md   # ⭐ Main setup guide
│   ├── DATABASE_SCHEMA.md         # Database reference
│   ├── DATABASE_TESTING.md        # Testing guide
│   └── RATE_LIMITING.md           # Rate limiting details
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
│   ├── database/                 # Database setup scripts
│   │   ├── setup_database.bat
│   │   └── apply_auto_update_schema.bat
│   ├── pgagent/                  # Auto-update scripts
│   │   ├── setup_pgagent.ps1
│   │   ├── reset_pgagent.ps1
│   │   └── configure_pgagent.bat
│   └── testing/                  # Test utilities
│       ├── run_tests.bat
│       └── test_*.py
│
├── tests/                         # 🧪 Test suite (53 tests)
│   ├── test_db_connection.py     # Connection tests (15)
│   ├── test_db_repository.py     # Repository tests (27)
│   └── test_db_integration.py    # Integration tests (11)
│
├── .env                          # 🔐 Environment variables
├── pyproject.toml                # Python dependencies
└── README.md                     # This file
```

## ⚡ Quick Start

> **First time here?** Check out the [Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md) for step-by-step instructions

### What You'll Need
- PostgreSQL 18.1 or newer
- Python 3.11 or newer
- A GitHub Personal Access Token (we'll help you get one)

### Getting It Running

```powershell
# 1. Grab the code
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave

# 2. Set up the database
.\scripts\database\setup_database.bat

# 3. Install Python stuff
pip install -r requirements.txt

# 4. Add your API keys
cp .env.example .env
# Open .env and add your GitHub token

# 5. Make sure everything works
.\scripts\testing\run_tests.bat
```

### Using It with Claude Desktop

```powershell
# Connect to Claude Desktop
python setup_claude_desktop.py

# Restart Claude Desktop
# Then just ask: "Analyze my GitHub profile"
```

### Running It Manually

```powershell
# Fire up the server
.\start_mcp_server.bat

# Check what tools are available
python list_tools.py
```

## 🔧 What This Thing Can Do

### Analysis Tools
- `analyze_github_developer` - Deep dive into someone's GitHub profile
- `analyze_jira_developer` - Figure out skills from Jira tickets
- `get_github_profile` - Just the basics about a GitHub user
- `compare_developers` - See how two developers stack up

### Database Tools
- `save_analysis_to_database` - Save results so you don't lose them
- `get_user_competence_overview` - Pull up someone's skill profile
- `get_previous_analysis` - Check out older analyses
- `get_all_competences` - See every skill we track

### Other Handy Tools
- `export_developer_profile` - Export data (GDPR-friendly JSON)
- `get_skill_categories` - See how we organize skills

## 🧪 Testing

```powershell
# Run everything (all 53 tests)
.\scripts\testing\run_tests.bat

# Just run one test file
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

Want the full SQL? Check out the [Database Schema](docs/DATABASE_SCHEMA.md) doc.

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

Need more details? The [Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md#automatic-updates-optional) has you covered.

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
4. Run test suite: `.\scripts\testing\run_tests.bat`
5. Commit changes: `git commit -m "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Submit pull request

## 📝 License

This project is part of a thesis on developer skill analysis. See supervisor for usage terms.

## 🐛 When Things Go Wrong

### Database won't connect
```powershell
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
.\scripts\testing\run_tests.bat
```

Still stuck? Check the [Complete Setup Guide - Troubleshooting](docs/COMPLETE_SETUP_GUIDE.md#troubleshooting) section.
DATABASE_URL=postgresql://postgres:password@localhost:5432/developer_skills
```

**MCP server not connecting:**
```powershell
# Test server locally
cd e:\Nymappe\Hovedopgave
$env:PYTHONPATH = "e:\Nymappe\Hovedopgave\src"
python -m server

# Check Claude config
cat $env:APPDATA\Claude\claude_desktop_config.json
```

**Tests failing:**
```powershell
# Clean test database
psql -U postgres -c "DROP DATABASE IF EXISTS developer_skills_test;"

# Re-run tests (creates fresh DB)
.\scripts\testing\run_tests.bat
```

See [Complete Setup Guide - Troubleshooting](docs/COMPLETE_SETUP_GUIDE.md#troubleshooting) for more solutions.

## 📞 Support

For detailed setup instructions, see:
- **[Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md)**
- **[Database Schema](docs/DATABASE_SCHEMA.md)**
- **[Database Testing](docs/DATABASE_TESTING.md)**

For issues, check:
- GitHub Issues: https://github.com/Viggo0205/Hovedopgave/issues
- Thesis supervisor contact information

---

**Made with ❤️ for developer skill analysis**
