# Database Integration - Quick Reference

## Setup Steps

### 1. Install PostgreSQL
```powershell
# Download from: https://www.postgresql.org/download/
# Default: postgres/postgres on port 5432
```

### 2. Install Python Package
```powershell
pip install psycopg2-binary
```

### 3. Run Setup Script
```powershell
.\setup_database.bat
```

### 4. Test Connection
```powershell
python test_database.py
```

## MCP Tools Added

### 1. `add_competence_to_database`
Add new skills to track:
```
{
  "name": "Vue.js",
  "category": "frameworks_tools",
  "description": "Progressive JavaScript framework"
}
```

**Categories:**
- `programming_languages` - Python, Java, JavaScript, etc.
- `frameworks_tools` - React, Docker, Git, etc.
- `databases` - PostgreSQL, MongoDB, etc.
- `soft_skills` - Communication, Leadership, etc.
- `domain_knowledge` - Web Dev, DevOps, etc.

### 2. `get_all_competences`
List all tracked skills/competences.

### 3. `save_analysis_to_database`
Analyze developer and save to database:
```
{
  "github_username": "octocat",
  "jira_email": "octo@example.com",
  "full_name": "Octo Cat",
  "save_to_db": true
}
```

**What it does:**
- Runs GitHub/Jira analysis
- Creates/updates user record
- Saves full analysis as JSON (keeps 2 versions)
- Extracts skills and saves percentages
- Archives old version automatically

### 4. `get_user_competence_overview`
View user's competence levels with ranks:
```
{
  "github_username": "octocat"
}
```

**Returns:**
- All competences with percentages (0-100)
- Rank for each: Beginner/Intermediate/Advanced/Expert
- Usage frequency
- Last updated timestamp

### 5. `get_previous_analysis`
Retrieve analysis history (max 2 versions):
```
{
  "github_username": "octocat"
}
```

## Version Management

**Automatic Archiving:**
1. First analysis → Saved as version 1
2. Second analysis → Saved as version 2
3. Third analysis → Version 1 deleted, version 2 becomes version 1, new becomes version 2

**Always maintains 2 versions maximum**

## Database Structure

```
users (id, github_username, jira_email, full_name, ...)
  ↓
user_competence (user_id, competence_id, procent, usage_frequency)
  ↓
competence (id, name, category, description)
  ↓
rank (Beginner 0-24%, Intermediate 25-49%, Advanced 50-74%, Expert 75-100%)

analysis_archive (user_id, analysis_data JSONB, version_number 1 or 2)
```

## Example Workflow

### Analyze Everyone and Save

```python
# In Claude Desktop, use MCP tools:

# 1. Get all employees
employees = get_all_employees(source="github", include_metadata=True)

# 2. For each employee, analyze and save
for employee in employees['github_employees']:
    save_analysis_to_database(
        github_username=employee['username'],
        full_name=employee.get('name', ''),
        save_to_db=True
    )

# 3. View someone's competences
get_user_competence_overview(github_username="octocat")

# 4. Check their analysis history
get_previous_analysis(github_username="octocat")
```

### Add Custom Competences

```python
# Add company-specific skills
add_competence_to_database(
    name="Internal Framework X",
    category="frameworks_tools",
    description="Company proprietary framework"
)

# Add business domain knowledge
add_competence_to_database(
    name="Financial Services Domain",
    category="domain_knowledge",
    description="Banking and finance industry knowledge"
)
```

## SQL Queries

### Get all users with Expert skills
```sql
SELECT DISTINCT github_username, competence_name, procent
FROM user_competence_overview
WHERE rank_name = 'Expert'
ORDER BY github_username, procent DESC;
```

### Find skill gaps across team
```sql
SELECT 
    competence_name,
    COUNT(*) as team_members,
    AVG(procent) as avg_proficiency,
    MAX(procent) as max_proficiency
FROM user_competence_overview
GROUP BY competence_name
HAVING AVG(procent) < 50
ORDER BY avg_proficiency ASC;
```

### Compare two analyses
```sql
SELECT 
    version_number,
    analysis_date,
    analysis_data->'summary'->'total_skills' as total_skills,
    analysis_data->'summary'->'primary_specialization' as specialization
FROM analysis_archive
WHERE user_id = 1
ORDER BY version_number DESC;
```

## Troubleshooting

**"Import psycopg2 could not be resolved"**
```powershell
pip install psycopg2-binary
```

**"Connection refused"**
- Start PostgreSQL service
- Check port 5432 is not blocked
- Verify DATABASE_URL in .env

**"Database does not exist"**
```powershell
.\setup_database.bat
```

**"No competences found"**
```powershell
# Rerun schema to load default competences
psql -U postgres -d developer_skills -f src\developer_skill_analyzer\db\schema.sql
```

## Configuration

**.env file:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills
```

**Custom database:**
```env
DATABASE_URL=postgresql://myuser:mypassword@192.168.1.100:5432/mydb
```
