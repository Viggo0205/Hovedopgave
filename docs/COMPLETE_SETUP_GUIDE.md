# Developer Skill Analyzer - Complete Setup Guide

Everything you need to get this thing up and running, all in one place. No jumping between different docs!

## What's in Here
1. [What You Need First](#prerequisites)
2. [Setting Up the Database](#database-setup)
3. [Getting Python Ready](#python-environment-setup)
4. [Starting the MCP Server](#mcp-server-setup)
5. [Hooking Up Claude Desktop](#claude-desktop-integration)
6. [Auto-Updates (if you want them)](#automatic-updates-optional)
7. [Running Tests](#testing)
8. [Fixing Common Problems](#troubleshooting)

---

## Prerequisites

### Software You'll Need
- **PostgreSQL 18.1** - Download from https://www.postgresql.org/download/
- **Python 3.11 or newer** - Get it at https://www.python.org/downloads/
- **Git** - Grab it from https://git-scm.com/downloads/
- **Claude Desktop** - Available at https://claude.ai/download

### API Keys to Get Ready
- **GitHub Personal Access Token** - Make one at https://github.com/settings/tokens
  - You'll need these permissions: `repo`, `read:user`, `read:org`
- **Jira API Token** (optional, didn't get to test it yet) - Create at https://id.atlassian.com/manage-profile/security/api-tokens

---

## Database Setup

### Step 1: Get PostgreSQL Installed

1. Download PostgreSQL 18.1 from https://www.postgresql.org/download/
2. Run the installer - the defaults are fine
3. Pick a password for the postgres user (write it down!)
4. It'll use port `5432` by default

### Step 2: Create Your Database

Open PowerShell:

```powershell
# Connect to PostgreSQL
psql -U postgres

# Make the database
CREATE DATABASE developer_skills;

# Get out
\q

# Or if you prefer a GUI, use pgAdmin 4 - it's more visual
```

### Step 3: Load the Schema

From the project folder:

```powershell
cd e:\Nymappe\Hovedopgave

# Load the main tables and stuff
psql -U postgres -d developer_skills -f src\db\schema.sql

# Add auto-update tables (optional, but cool)
psql -U postgres -d developer_skills -f src\db\auto_update_schema.sql
```

**Or just run the setup script:**

```powershell
.\scripts\database\setup_database.bat
```

### Step 4: Check Everything's There

```powershell
# Jump into the database
psql -U postgres -d developer_skills

# List tables
\dt

# List views
\dv

# List functions
\df

# Leave
\q
```

You should see these tables:
- `role`
- `users`
- `competence`
- `rank`
- `user_competence`
- `analysis_archive`

(pgAdmin 4 also shows all this if you prefer clicking around)
---

## Python Environment Setup

### Step 1: Get the Code

```powershell
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave
```

### Step 2: Set Up a Virtual Environment

```powershell
# Create it
python -m venv venv

# Turn it on
.\venv\Scripts\Activate.ps1

# Or if Python's installed somewhere specific
E:\Nymappe\python\python.exe -m venv venv
```

### Step 3: Install Everything

```powershell
# Install all the Python packages
pip install -r requirements.txt

# Or if you're using uv
uv pip install -e .
```

**What gets installed:**
- `fastmcp` - The MCP server framework
- `psycopg2-binary` - Talks to PostgreSQL
- `PyGithub` - GitHub API wrapper
- `atlassian-python-api` - Jira API wrapper
- `pytest` - For running tests
- `asyncio-throttle` - Keeps us from hitting rate limits

### Step 4: Add Your API Keys

Create a `.env` file in the project root:

```env
# Database stuff
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills

# GitHub credentials
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username

# Jira stuff (optional)
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token_here

# Rate limiting (these are good defaults)
GITHUB_REQUESTS_PER_MINUTE=60
GITHUB_MAX_FAILURES=3
GITHUB_DEGRADED_DURATION=300

# Pro tip: copy .env.example and fill it in
```

**Important:** Don't commit your `.env` file! It has secrets in it.

---

## MCP Server Setup

### Step 1: Make Sure It Runs

```powershell
# Go to the project folder
cd e:\Nymappe\Hovedopgave

# Tell Python where to find stuff
$env:PYTHONPATH = "e:\Nymappe\Hovedopgave\src"

# Fire it up
E:\Nymappe\python\python.exe -m server
```

If it works, you'll see: "MCP server running..."

### Step 2: Check What Tools Are Available

```powershell
# See all the tools
E:\Nymappe\python\python.exe list_tools.py
```

Expected tools:
- `analyze_github_developer`
- `get_github_profile`
- `compare_developers`
- `save_analysis_to_database`
- `get_user_competence_overview`
- `export_developer_profile`

### Step 3: Create Startup Script

Already created at `scripts\start_mcp_server.bat`:

```batch
@echo off
cd /d e:\Nymappe\Hovedopgave
set PYTHONPATH=e:\Nymappe\Hovedopgave\src
E:\Nymappe\python\python.exe -m server
```

---

## Claude Desktop Integration

### Step 1: Locate Claude Config

Claude Desktop config location:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add MCP Server Configuration

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "developer-skill-analyzer": {
      "command": "E:\\Nymappe\\python\\python.exe",
      "args": ["-m", "server"],
      "cwd": "e:\\Nymappe\\Hovedopgave\\src",
      "env": {
        "PYTHONPATH": "e:\\Nymappe\\Hovedopgave\\src"
      }
    }
  }
}
```

**Or use the setup script:**

```powershell
E:\Nymappe\python\python.exe setup_claude_desktop.py
```

### Step 3: Restart Claude Desktop

1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. Check for MCP server connection (hammer icon in UI)

### Step 4: Test in Claude

Ask Claude:
```
Can you analyze my GitHub profile?
```

Claude should use the `analyze_github_developer` tool.

---

## Automatic Updates (Optional)

### Overview

Automatic updates keep developer profiles synchronized with latest GitHub/Jira data.

### Step 1: Install pgAgent

pgAgent is included with PostgreSQL installation. Verify:

```powershell
# Check pgAgent executable
Test-Path "E:\PostgreSQL\18\bin\pgagent.exe"
```

### Step 2: Enable pgAgent Extension

```powershell
psql -U postgres -d developer_skills -c "CREATE EXTENSION IF NOT EXISTS pgagent;"
```

### Step 3: Configure pgAgent Service

**Option A - Use Setup Script:**

```powershell
.\scripts\pgagent\setup_pgagent.ps1
```

**Option B - Manual Setup:**

```powershell
# Install service
sc.exe create pgAgent binPath= "E:\PostgreSQL\18\bin\pgagent.exe RUN postgres postgres 127.0.0.1 developer_skills" start= auto

# Start service
sc.exe start pgAgent
```

### Step 4: Create Update Job

```powershell
# Apply auto-update schema (creates jobs)
psql -U postgres -d developer_skills -f src\db\auto_update_schema.sql
```

### Step 5: Configure Update Worker

The `auto_update_worker.py` script handles the actual updates:

```python
# Already configured to:
# - Run every 24 hours
# - Update all users in database
# - Log to auto_update_worker.log
```

### Step 6: Verify Automatic Updates

```sql
-- Check last update status
SELECT * FROM v_update_status ORDER BY last_updated DESC;

-- Check scheduled jobs
SELECT * FROM pgagent.pga_job;
```

---

## Testing

### Run All Tests

```powershell
# Run all tests
E:\Nymappe\python\python.exe -m pytest tests/ -v

# Run specific test file
E:\Nymappe\python\python.exe -m pytest tests/test_db_connection.py -v

# Run with coverage
E:\Nymappe\python\python.exe -m pytest tests/ --cov=src --cov-report=html
```

**Or use test script:**

```powershell
.\scripts\run_tests.bat
```

### Test Categories

**Database Tests (53 total):**
- `test_db_connection.py` - Connection pooling, queries, transactions (15 tests)
- `test_db_repository.py` - CRUD operations, user management (27 tests)
- `test_db_integration.py` - Stored procedures, triggers, views (11 tests)

**API Tests:**
- `test_sanitization.py` - Data sanitization
- `test_skill_extraction.py` - Skill processing
- `test_save_function.py` - Database save operations

### Test Database

Tests use separate database: `developer_skills_test`

- Created automatically before test session
- Dropped automatically after test session
- Isolated from production data

---

## Troubleshooting

### Database Connection Issues

**Error: "could not connect to server"**

```powershell
# Check PostgreSQL service
Get-Service -Name postgresql*

# Start service if stopped
Start-Service -Name postgresql-x64-18
```

**Error: "password authentication failed"**

```powershell
# Reset password in .env file
# Default: postgres/postgres

# Or reset PostgreSQL password
psql -U postgres
\password postgres
```

### MCP Server Not Connecting

**Check server runs locally:**

```powershell
cd e:\Nymappe\Hovedopgave
$env:PYTHONPATH = "e:\Nymappe\Hovedopgave\src"
E:\Nymappe\python\python.exe -m server
```

**Check Claude config:**

```powershell
# View config
cat $env:APPDATA\Claude\claude_desktop_config.json

# Validate JSON syntax
E:\Nymappe\python\python.exe -m json.tool $env:APPDATA\Claude\claude_desktop_config.json
```

**Check logs:**

```powershell
# MCP server log
cat mcp_server_debug.log

# Claude Desktop logs (Windows)
cat "$env:APPDATA\Claude\logs\mcp*.log"
```

### GitHub API Rate Limiting

**Error: "API rate limit exceeded"**

The system includes automatic rate limiting (60 requests/min) with:
- Exponential backoff (5s → 10s → 20s)
- Circuit breaker (3 failures → 5min degraded mode)
- Automatic recovery

**Check rate limit status:**

```python
from services.github_service import GitHubService
service = GitHubService()
# Rate limiting is automatic
```

### Python Import Errors

**Error: "ModuleNotFoundError"**

```powershell
# Ensure PYTHONPATH is set
$env:PYTHONPATH = "e:\Nymappe\Hovedopgave\src"

# Reinstall dependencies
pip install -r requirements.txt

# Or use absolute imports
cd e:\Nymappe\Hovedopgave\src
```

### Test Failures

**Database tests failing:**

```powershell
# Ensure test database doesn't exist
psql -U postgres -c "DROP DATABASE IF EXISTS developer_skills_test;"

# Re-run tests (will create fresh DB)
E:\Nymappe\python\python.exe -m pytest tests/ -v
```

**Skills not saving to database:**

Check the skill extraction is working:

```powershell
E:\Nymappe\python\python.exe test_skill_extraction.py
```

Expected output:
```
Technical skills found: 3
  - C#: SkillLevel.EXPERT (confidence: 1.00, usage: 60791)
  - HTML: SkillLevel.INTERMEDIATE (confidence: 0.30, usage: 4298)
  - CSS: SkillLevel.BEGINNER (confidence: 0.30, usage: 33)
```

---

## Quick Reference Commands

### Database
```powershell
# Connect to database
psql -U postgres -d developer_skills

# Run schema
psql -U postgres -d developer_skills -f src\db\schema.sql

# Backup database
pg_dump -U postgres developer_skills > backup.sql

# Restore database
psql -U postgres -d developer_skills < backup.sql
```

### Server
```powershell
# Start MCP server
.\scripts\start_mcp_server.bat

# Test server tools
E:\Nymappe\python\python.exe list_tools.py
```

### Testing
```powershell
# Run all tests
.\scripts\run_tests.bat

# Run specific test
E:\Nymappe\python\python.exe -m pytest tests/test_db_connection.py -v
```

### Maintenance
```powershell
# View update status
psql -U postgres -d developer_skills -c "SELECT * FROM v_update_status;"

# Manual update
E:\Nymappe\python\python.exe auto_update_worker.py

# Check pgAgent service
Get-Service pgAgent
```

---

## Next Steps

1. ✅ Complete database setup
2. ✅ Configure environment variables
3. ✅ Test MCP server locally
4. ✅ Integrate with Claude Desktop
5. ✅ Run test suite
6. ⚡ Configure automatic updates (optional)
7. 📊 Start analyzing developers!

For more detailed information, see:
- [Database Schema Documentation](DATABASE_SCHEMA.md)
- [API Reference](API_REFERENCE.md)
- [Testing Guide](DATABASE_TESTING.md)
- [Rate Limiting Details](RATE_LIMITING.md)
