# Developer Skill Analyzer - Setup Guide

How to set up the system on a new computer.

## What You Need

- **Python 3.11 or newer**
- **PostgreSQL 18 or newer** (must be running)
- **uv** (`pip install uv`)
- **Git**

## Step 1: Get the Code

```bash
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave
```

## Step 2: Install Python Packages

```bash
uv sync
```

This fetches all dependencies from `pyproject.toml`.

## Step 3: Create Your `.env` File

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# GitHub Token (REQUIRED - see below)
GITHUB_TOKEN=ghp_yourTokenHere
GITHUB_ACCESS_TOKEN=ghp_yourTokenHere

# Database (change password to your own)
DATABASE_URL=postgresql://postgres:YourPassword@localhost:5432/developer_skills

# Rest can stay as is
MOCK_MODE=false
LOG_LEVEL=INFO
```

### How to Get a GitHub Token?

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name, e.g. "Developer Skill Analyzer"
4. Select these permissions:
   - ✓ `public_repo`
   - ✓ `read:user`
   - ✓ `read:org`
5. Click "Generate token"
6. Copy the token (you can NOT see it again!)
7. Paste into both `GITHUB_TOKEN` and `GITHUB_ACCESS_TOKEN` fields

**Important:** 
- NEVER commit `.env` to git!
- The token is like a password - don't share it!

## Step 4: Setup Database

**Important:** Open `scripts/database/setup_database_complete.py` and change the database password on line 25:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '1234',  # <--- CHANGE THIS to your PostgreSQL password
    'database': 'developer_skills'
}
```

Then run the setup script:

```bash
python scripts/database/setup_database_complete.py
```

The script does the following automatically:
1. Creates database `developer_skills`
2. Loads schema (tables, functions, views)
3. Adds audit log functionality
4. Adds auto-update columns
5. Verifies everything works

You'll get output showing what's happening:
```
Developer Skill Analyzer - Complete Database Setup
[OK] Database 'developer_skills' created
[OK] Main schema (schema.sql) completed
[OK] Migration: add_audit_log_and_admin_tracking.sql completed
[OK] Migration: add_auto_update_columns.sql completed
[OK] Found 12 tables
[OK] Found 17 stored functions
[OK] Database setup completed successfully!
```

## Step 5: Test That It Works

### Run All Tests

```bash
pytest tests/ -v
```

If everything is good you'll see:
```
44 passed in 10.03s
```

### Run Specific Tests

```bash
# Only database connection tests
pytest tests/test_db_connection.py -v

# Only repository tests  
pytest tests/test_db_repository.py -v

# Only integration tests
pytest tests/test_db_integration.py -v

# One specific test
pytest tests/test_db_connection.py::TestDatabaseConnection::test_health_check_healthy -v
```

### Test Structure

```
tests/
├── test_db_connection.py      # DatabaseConnection tests (12 tests)
├── test_db_repository.py      # DatabaseRepository tests (21 tests)
├── test_db_integration.py     # Stored procedures + triggers (11 tests)
├── test_remove_developer.py   # Remove developer tool test
└── test_language_tool.py      # Language extraction test
```

**Note:** Tests use a separate `developer_skills_test` database that's created automatically.

## Step 6: Connect Claude Desktop

Run the setup script:

```bash
python scripts/utilities/setup_claude_desktop.py
```

This script automatically finds Claude Desktop's config file (works on Windows, Mac, and Linux), backs up your existing config, and adds the Developer Skill Analyzer server.

You'll get output like:
```
✅ Found uv at: C:\Users\...\uv.exe
✅ Backed up existing config
✅ Claude Desktop config updated
🎉 Setup complete! Restart Claude Desktop.
```

## Step 7: Start the Server

### Windows:
```bash
scripts\start_mcp_server.bat
```

### Linux/Mac:
```bash
uv run src/server.py
```

Now you can use MCP tools from Claude Desktop!

---

## Extra Tool Tests

The project has two additional test files for testing specific functions:

```bash
python tests/test_remove_developer.py  # Test remove developer tool
python tests/test_language_tool.py     # Test language extraction
```

---

## What Does the Claude Desktop Setup Script Do?

After refactoring, the system needed to be set up on another computer, so a setup script was created to make it easier.

### How Does It Work?

**1. OS Detection**

The script automatically finds where Claude Desktop stores its config:

```python
def get_claude_config_path():
    if sys.platform == "win32":
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
```

This means the script works on all platforms.

**2. UV Dependency Manager**

The script uses `uv` to start the server because it:
- Automatically handles virtual environments
- Loads dependencies based on `pyproject.toml`
- Makes the startup process simple

The alternative would be to hardcode Python paths and manually activate virtual environments, which is more complicated.

**3. Backup and Merge**

The script backs up your existing config and merges the new server without deleting other MCP servers you might have:

```python
def merge_configs(existing_config, new_server_config):
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["developer-skill-analyzer"] = 
        new_server_config["mcpServers"]["developer-skill-analyzer"]
    
    return existing_config
```

**Note:** Environment variables are **not** included in the config file. The MCP server loads credentials from the `.env` file itself, keeping secrets out of git and configuration files.

---

## File Structure

```
Hovedopgave/
├── docs/
│   └── SETUP_GUIDE.md          # This guide
├── pyproject.toml               # Dependencies
├── .env                         # Your credentials (create yourself)
│
├── src/                         # Source code
│   ├── server.py                # MCP server entry point
│   ├── config.py                # Configuration
│   ├── analyzers/               # GitHub/Jira analyzers
│   ├── services/                # API services
│   ├── db/                      # Database layer
│   │   ├── schema.sql          # Main schema
│   │   ├── connection.py       # Connection pool
│   │   └── repository.py       # Data access
│   ├── models/                  # Data models
│   └── shared/                  # Utilities
│
├── tests/                       # 44 pytest tests
│   ├── test_db_connection.py
│   ├── test_db_integration.py
│   ├── test_db_repository.py
│   ├── test_remove_developer.py # Tool test
│   └── test_language_tool.py    # Tool test
│
├── scripts/                     # Utility scripts
│   ├── start_mcp_server.bat    # Start server (Windows)
│   ├── database/
│   │   └── setup_database_complete.py  # Database setup
│   ├── pgagent/                # Scheduled updates
│   └── utilities/
│       └── setup_claude_desktop.py
│
└── migrations/                  # Database migrations
    ├── add_audit_log_and_admin_tracking.sql
    └── add_auto_update_columns.sql
```

---

## Useful Database Queries

If you want to see data directly in the database:

### See all users and their skills
```sql
SELECT * FROM user_competence_overview;
```

### See a user's latest analysis
```sql
SELECT * FROM get_latest_analysis(user_id);
-- Example: SELECT * FROM get_latest_analysis(1);
```

### See all competences by category
```sql
SELECT category, name, description 
FROM competence 
ORDER BY category, name;
```

### Backup database
```powershell
# Full backup
pg_dump -U postgres developer_skills > backup.sql

# Restore backup
psql -U postgres -d developer_skills < backup.sql
```

---

## Troubleshooting

### Database won't connect
```bash
# Check PostgreSQL is running
Get-Service postgresql-x64-18

# Test connection
psql -U postgres -d developer_skills -c "SELECT version();"
```

### MCP server won't start
```bash
# Check uv
uv --version

# Reinstall dependencies
uv sync

# Check .env file exists
type .env
```

### Tests fail
```bash
# See which tests fail
pytest tests/ -v

# Run one test at a time
pytest tests/test_db_connection.py -v
```

---

## Done!

After setup you can:

- ✅ Run `pytest tests/` without errors
- ✅ Start MCP server
- ✅ See the server in Claude Desktop
- ✅ Call tools from Claude (e.g. `analyze_github_developer`)
- ✅ See data in PostgreSQL

Enjoy! 🎉
