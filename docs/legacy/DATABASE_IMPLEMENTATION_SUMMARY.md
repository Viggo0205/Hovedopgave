# Database Integration Summary

## ✅ What Was Implemented

### 1. Database Schema (`src/developer_skill_analyzer/db/schema.sql`)
- **Tables:**
  - `role` - User roles
  - `users` - Developer profiles (GitHub, Jira identifiers)
  - `competence` - Skills catalog with categories
  - `rank` - Proficiency levels (Beginner/Intermediate/Advanced/Expert)
  - `user_competence` - User skill levels with percentages
  - `analysis_archive` - Historical analysis data (max 2 versions per user)

- **Views:**
  - `user_competence_overview` - Combined user/skill/rank data
  - `competence_categories` - Skills grouped by category

- **Stored Procedures:**
  - `add_competence()` - Add/update skills
  - `update_user_competence()` - Update user skill levels
  - `save_analysis()` - Save analysis with automatic version management
  - `get_latest_analysis()` - Retrieve most recent analysis
  - `get_or_create_user()` - Create or update user profiles

### 2. Database Connection Layer (`src/developer_skill_analyzer/db/`)
- `connection.py` - PostgreSQL connection pooling
- `repository.py` - High-level database operations
- `__init__.py` - Package initialization

### 3. Modified Skill Processor
**Updated:** `src/developer_skill_analyzer/analyzers/skill_processor.py`

**Changes:**
- Now loads skill categories from database instead of hardcoded values
- Falls back to defaults if database unavailable
- Accepts `DatabaseRepository` instance for database integration

**Before:**
```python
def __init__(self):
    self.skill_categories = self._initialize_skill_categories()
```

**After:**
```python
def __init__(self, db_repository: Optional[DatabaseRepository] = None):
    self.db_repo = db_repository or DatabaseRepository()
    self.skill_categories = self._initialize_skill_categories()
```

### 4. New MCP Tools (in `server.py`)

#### `add_competence_to_database(name, category, description)`
Add new skills to the tracking system dynamically.

#### `get_all_competences()`
List all competences in the database, organized by category.

#### `save_analysis_to_database(github_username, jira_email, full_name, save_to_db)`
**Main tool for analysis + storage:**
- Performs GitHub/Jira analysis
- Creates/updates user record
- Saves full analysis as JSON
- Extracts skills and saves as competences
- **Automatic version management** - keeps max 2 versions

#### `get_user_competence_overview(github_username, jira_email)`
Retrieve user's competence levels with ranks.

#### `get_previous_analysis(github_username, jira_email)`
Get analysis history (both current and previous version).

### 5. Setup Scripts

- `setup_database.bat` - Automated PostgreSQL database setup
- `test_database.py` - Comprehensive database testing
- `DATABASE_SETUP.md` - Detailed setup instructions
- `DATABASE_QUICK_REFERENCE.md` - Quick usage guide

### 6. Environment Configuration

**Added to `.env`:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills
```

**Added to `pyproject.toml`:**
```toml
"psycopg2-binary>=2.9.0"
```

## 🎯 Key Features

### Version Management (Automatic)
1. **First analysis** → Saved as version 1
2. **Second analysis** → Saved as version 2  
3. **Third analysis** → Version 1 deleted, version 2 → version 1, new → version 2

**Always keeps maximum 2 versions per user**

### Dynamic Skill Categories
- Skills loaded from database (not hardcoded)
- Add new skills via MCP tool
- Fallback to defaults if database unavailable

### Complete Analysis Pipeline
```
Analyze Developer
    ↓
Extract Skills
    ↓
Save to Database
    ↓
  ┌─────────────┬──────────────┐
  ↓             ↓              ↓
Users Table  Competences   Archive
             (with %)      (JSON)
```

## 📋 Setup Instructions

### Quick Setup

1. **Install PostgreSQL**
   ```powershell
   # Download from postgresql.org
   # Use default: postgres/postgres, port 5432
   ```

2. **Install Python Package**
   ```powershell
   pip install psycopg2-binary
   ```

3. **Setup Database**
   ```powershell
   .\setup_database.bat
   ```

4. **Test Everything**
   ```powershell
   python test_database.py
   ```

5. **Update .env**
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills
   ```

### Manual Setup

```powershell
# Create database
psql -U postgres -c "CREATE DATABASE developer_skills;"

# Run schema
psql -U postgres -d developer_skills -f src\developer_skill_analyzer\db\schema.sql

# Test connection
python -c "from src.developer_skill_analyzer.db.connection import DatabaseConnection; print('OK' if DatabaseConnection().execute_query('SELECT 1') else 'FAIL')"
```

## 🚀 Usage Examples

### Analyze and Save to Database

```python
# Analyze developer and save everything
save_analysis_to_database(
    github_username="octocat",
    full_name="Octo Cat",
    save_to_db=True
)
```

### View Competences

```python
# Get all competences
get_all_competences()

# Get user's competences with ranks
get_user_competence_overview(github_username="octocat")
```

### Check History

```python
# Get both versions of analyses
get_previous_analysis(github_username="octocat")
```

### Add Custom Skills

```python
# Add company-specific framework
add_competence_to_database(
    name="Internal API Framework",
    category="frameworks_tools",
    description="Company proprietary API framework"
)
```

## 🔍 Database Queries

### All users with Expert skills
```sql
SELECT github_username, competence_name, procent
FROM user_competence_overview
WHERE rank_name = 'Expert';
```

### Team skill gaps
```sql
SELECT 
    competence_name,
    AVG(procent) as avg_level
FROM user_competence_overview
GROUP BY competence_name
HAVING AVG(procent) < 50
ORDER BY avg_level;
```

### Analysis comparison
```sql
SELECT 
    u.github_username,
    a.version_number,
    a.analysis_date,
    a.analysis_data->'summary'->'total_skills' as skills
FROM analysis_archive a
JOIN users u ON a.user_id = u.id
ORDER BY u.id, a.version_number DESC;
```

## 📁 File Structure

```
e:\Nymappe\Hovedopgave\
├── src\developer_skill_analyzer\
│   ├── db\
│   │   ├── __init__.py                    # NEW
│   │   ├── connection.py                  # NEW - DB connection
│   │   ├── repository.py                  # NEW - DB operations
│   │   └── schema.sql                     # NEW - Database schema
│   ├── analyzers\
│   │   └── skill_processor.py             # MODIFIED - Uses DB
│   └── server.py                          # MODIFIED - 5 new tools
├── .env                                   # MODIFIED - Added DATABASE_URL
├── pyproject.toml                         # MODIFIED - Added psycopg2
├── setup_database.bat                     # NEW - Setup script
├── test_database.py                       # NEW - Test script
├── DATABASE_SETUP.md                      # NEW - Setup guide
└── DATABASE_QUICK_REFERENCE.md            # NEW - Quick reference
```

## ⚙️ Configuration

### Connection String Format
```
postgresql://username:password@host:port/database
```

### Examples
```env
# Local development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills

# Remote server
DATABASE_URL=postgresql://user:pass@192.168.1.100:5432/skills_db

# Cloud (e.g., Heroku)
DATABASE_URL=postgresql://user:pass@host.com:5432/db?sslmode=require
```

## ✨ Benefits

1. **Persistent Storage** - All analyses saved in database
2. **Version Control** - Compare current vs previous analysis
3. **Dynamic Skills** - Add new competences without code changes
4. **Centralized Data** - Single source of truth for all developer data
5. **SQL Queries** - Powerful analytics via SQL
6. **Automatic Archiving** - Old versions managed automatically
7. **Scalable** - PostgreSQL handles large teams efficiently

## 🐛 Troubleshooting

**Connection Error:**
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Test connection
psql -U postgres -c "SELECT 1"
```

**Schema Not Found:**
```powershell
# Rerun schema
.\setup_database.bat
```

**Import Error:**
```powershell
# Install package
pip install psycopg2-binary
```

## 📚 Next Steps

1. **Setup PostgreSQL** if not already installed
2. **Run setup script:** `.\setup_database.bat`
3. **Test connection:** `python test_database.py`
4. **Update .env** with DATABASE_URL
5. **Restart MCP server** in Claude Desktop
6. **Test new tools** via Claude interface

## 🎓 Learning Resources

- PostgreSQL Docs: https://www.postgresql.org/docs/
- psycopg2 Guide: https://www.psycopg.org/docs/
- SQL Tutorial: https://www.postgresql.org/docs/current/tutorial.html

---

**You're all set!** The system now:
- ✅ Loads skills from database
- ✅ Saves analyses with version control
- ✅ Tracks user competences with ranks
- ✅ Allows dynamic skill addition
- ✅ Maintains analysis history (2 versions max)
