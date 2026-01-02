# Database Setup Guide

## Prerequisites

1. **PostgreSQL Installation**
   - Download and install PostgreSQL from https://www.postgresql.org/download/
   - Default credentials: `postgres` / `postgres`
   - Default port: `5432`

2. **Python Dependencies**
   ```powershell
   pip install psycopg2-binary
   ```

## Database Setup

### Step 1: Create Database

Open PowerShell and connect to PostgreSQL:

```powershell
# Using psql command line
psql -U postgres

# Create database
CREATE DATABASE developer_skills;

# Connect to the database
\c developer_skills

# Exit
\q
```

### Step 2: Run Schema Script

```powershell
# From project root directory
cd e:\Nymappe\Hovedopgave

# Run the schema file
psql -U postgres -d developer_skills -f src\developer_skill_analyzer\db\schema.sql
```

### Step 3: Configure Environment Variables

Update your `.env` file with database connection string:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/developer_skills
```

Adjust the connection string if you use different credentials:
- Format: `postgresql://username:password@host:port/database`

## Database Schema Overview

### Tables

1. **role** - User roles (Developer, Team Lead, etc.)
2. **users** - Developer information
   - `github_username` - GitHub identifier
   - `jira_email` - Jira identifier
   - `full_name`, `display_name`, `company`, `location`
   - `role_id` - Foreign key to role table

3. **competence** - Skills/competences catalog
   - `name` - Skill name (Python, React, Leadership, etc.)
   - `category` - Skill category
   - `description` - Optional description

4. **rank** - Proficiency levels
   - Beginner (0-24%)
   - Intermediate (25-49%)
   - Advanced (50-74%)
   - Expert (75-100%)

5. **user_competence** - User skill levels
   - Links users to competences with proficiency percentage
   - `procent` - Skill level (0-100)
   - `usage_frequency` - How often the skill is used

6. **analysis_archive** - Historical analysis data
   - Stores up to 2 versions per user
   - Automatically archives old versions
   - Full JSON analysis data

### Views

1. **user_competence_overview** - Combines user, competence, and rank data
2. **competence_categories** - Groups competences by category

### Stored Procedures

1. `add_competence(name, category, description)` - Add new skill
2. `update_user_competence(user_id, competence_id, procent, frequency)` - Update skill level
3. `save_analysis(user_id, analysis_data)` - Save analysis with version control
4. `get_latest_analysis(user_id)` - Get most recent analysis
5. `get_or_create_user(...)` - Get existing or create new user

## Usage with MCP Server

### Available MCP Tools

1. **add_competence_to_database**
   ```python
   # Add a new skill to track
   add_competence_to_database(
       name="Svelte",
       category="frameworks_tools",
       description="Svelte JavaScript framework"
   )
   ```

2. **get_all_competences**
   ```python
   # List all tracked competences
   get_all_competences()
   ```

3. **save_analysis_to_database**
   ```python
   # Analyze and save to database
   save_analysis_to_database(
       github_username="octocat",
       full_name="Octo Cat",
       save_to_db=True
   )
   ```

4. **get_user_competence_overview**
   ```python
   # Get user's competence levels
   get_user_competence_overview(github_username="octocat")
   ```

5. **get_previous_analysis**
   ```python
   # Retrieve analysis history (max 2 versions)
   get_previous_analysis(github_username="octocat")
   ```

### Version Management

The system automatically maintains analysis versions:
- When you run a new analysis, it becomes version 2
- The previous version 2 becomes version 1
- The old version 1 is deleted
- Maximum 2 versions are stored per user

## Testing Database Connection

Create a test script:

```powershell
# Test database connection
python -c "from src.developer_skill_analyzer.db.connection import DatabaseConnection; db = DatabaseConnection(); print('Connected!' if db.execute_query('SELECT 1') else 'Failed')"
```

## Querying the Database

### Get all users with their skills

```sql
SELECT * FROM user_competence_overview;
```

### Get specific user's skills

```sql
SELECT 
    competence_name,
    procent,
    rank_name
FROM user_competence_overview
WHERE github_username = 'octocat'
ORDER BY procent DESC;
```

### Get competences by category

```sql
SELECT category, COUNT(*) as count
FROM competence
GROUP BY category;
```

### Get recent analyses

```sql
SELECT 
    u.github_username,
    a.version_number,
    a.analysis_date,
    jsonb_pretty(a.analysis_data->'summary')
FROM analysis_archive a
JOIN users u ON a.user_id = u.id
ORDER BY a.analysis_date DESC;
```

## Troubleshooting

### Connection Issues

1. **Check PostgreSQL is running**
   ```powershell
   Get-Service postgresql*
   ```

2. **Verify connection string**
   - Check username, password, host, port, database name
   - Ensure no extra spaces in `.env` file

3. **Check firewall**
   - PostgreSQL default port: 5432
   - Allow local connections

### Schema Issues

1. **Reset database**
   ```sql
   DROP DATABASE developer_skills;
   CREATE DATABASE developer_skills;
   ```

2. **Rerun schema**
   ```powershell
   psql -U postgres -d developer_skills -f src\developer_skill_analyzer\db\schema.sql
   ```

## Backup and Restore

### Backup

```powershell
pg_dump -U postgres -d developer_skills -f backup.sql
```

### Restore

```powershell
psql -U postgres -d developer_skills -f backup.sql
```
