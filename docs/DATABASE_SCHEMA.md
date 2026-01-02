# Database Schema and Scripts Reference

All the database stuff in one place - tables, views, functions, and the SQL you'll actually use.

## What's Here
1. [Main Schema](#main-schema) - The core tables and views
2. [Auto-Update Schema](#auto-update-schema) - For scheduled updates
3. [Useful Queries](#database-queries) - Copy-paste ready SQL
4. [Setup Scripts](#setup-scripts) - How to initialize everything

---

## Main Schema

**Where to find it:** `src/db/schema.sql`

### The Tables

#### role
Keeps track of what kind of developer someone is (Frontend, Backend, etc.):

```sql
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
```

#### users
Where we store info about developers:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    github_username VARCHAR(50) UNIQUE,
    jira_email VARCHAR(50) UNIQUE,
    full_name VARCHAR(50),
    display_name VARCHAR(50),
    company VARCHAR(50),
    location VARCHAR(50),
    role_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE SET NULL
);

-- These make lookups faster
CREATE INDEX idx_users_github ON users(github_username);
CREATE INDEX idx_users_jira ON users(jira_email);
```

#### competence
All the skills we track:

```sql
CREATE TABLE competence (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_competence_category ON competence(category);
```

#### rank
Skill levels (Beginner to Expert):

```sql
CREATE TABLE rank (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    min_percent INT NOT NULL,
    max_percent INT NOT NULL
);

-- Load the default ranks
INSERT INTO rank (id, name, min_percent, max_percent)
VALUES 
    (1, 'Beginner', 0, 24),
    (2, 'Intermediate', 25, 49),
    (3, 'Advanced', 50, 74),
    (4, 'Expert', 75, 100)
ON CONFLICT (id) DO NOTHING;
```
    user_id INT NOT NULL,
    competence_id INT NOT NULL,
    procent NUMERIC(5,2) NOT NULL CHECK (procent >= 0 AND procent <= 100),
    usage_frequency INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_competence FOREIGN KEY (competence_id) REFERENCES competence(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, competence_id)
);
```

#### analysis_archive
```sql
CREATE TABLE analysis_archive (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    analysis_data JSONB NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version_number INT NOT NULL,
    
    CONSTRAINT fk_archive_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_version CHECK (version_number IN (1, 2))
);

CREATE INDEX idx_archive_user_version ON analysis_archive(user_id, version_number);
```

### Views

#### user_competence_overview
```sql
CREATE OR REPLACE VIEW user_competence_overview AS
SELECT 
    u.id,
    u.github_username,
    u.jira_email,
    u.full_name,
    u.display_name,
    u.company,
    u.location,
    r.name AS role_name,
    c.name AS competence_name,
    c.category AS competence_category,
    uc.procent,
    uc.usage_frequency,
    uc.last_updated,
    rk.name AS rank_name
FROM user_competence uc
JOIN users u ON uc.user_id = u.id
JOIN competence c ON uc.competence_id = c.id
LEFT JOIN role r ON u.role_id = r.id
JOIN rank rk ON uc.procent BETWEEN rk.min_percent AND rk.max_percent
ORDER BY u.id, c.category, c.name;
```

#### competence_categories
```sql
CREATE OR REPLACE VIEW competence_categories AS
SELECT 
    category,
    array_agg(name ORDER BY name) AS competences
FROM competence
GROUP BY category
ORDER BY category;
```

### Stored Procedures

#### add_competence
```sql
CREATE OR REPLACE FUNCTION add_competence(
    p_name VARCHAR(100),
    p_category VARCHAR(50),
    p_description TEXT DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    v_competence_id INT;
BEGIN
    INSERT INTO competence (name, category, description)
    VALUES (p_name, p_category, p_description)
    ON CONFLICT (name) DO UPDATE
        SET category = EXCLUDED.category,
            description = EXCLUDED.description
    RETURNING id INTO v_competence_id;
    
    RETURN v_competence_id;
END;
$$ LANGUAGE plpgsql;
```

#### update_user_competence
```sql
CREATE OR REPLACE FUNCTION update_user_competence(
    p_user_id INT,
    p_competence_id INT,
    p_procent NUMERIC(5,2),
    p_usage_frequency INT DEFAULT 0
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO user_competence (user_id, competence_id, procent, usage_frequency, last_updated)
    VALUES (p_user_id, p_competence_id, p_procent, p_usage_frequency, CURRENT_TIMESTAMP)
    ON CONFLICT (user_id, competence_id) DO UPDATE
        SET procent = EXCLUDED.procent,
            usage_frequency = EXCLUDED.usage_frequency,
            last_updated = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;
```

#### save_analysis
```sql
CREATE OR REPLACE FUNCTION save_analysis(
    p_user_id INT,
    p_analysis_data JSONB
)
RETURNS INT AS $$
DECLARE
    v_version_number INT;
BEGIN
    -- Determine next version (cycles between 1 and 2)
    SELECT COALESCE(
        CASE 
            WHEN MAX(version_number) = 1 THEN 2
            ELSE 1
        END, 
        1
    ) INTO v_version_number
    FROM analysis_archive
    WHERE user_id = p_user_id;
    
    -- Delete old version if exists
    DELETE FROM analysis_archive 
    WHERE user_id = p_user_id 
    AND version_number = v_version_number;
    
    -- Insert new version
    INSERT INTO analysis_archive (user_id, analysis_data, version_number)
    VALUES (p_user_id, p_analysis_data, v_version_number);
    
    RETURN v_version_number;
END;
$$ LANGUAGE plpgsql;
```

#### get_or_create_user
```sql
CREATE OR REPLACE FUNCTION get_or_create_user(
    p_github_username VARCHAR(50) DEFAULT NULL,
    p_jira_email VARCHAR(50) DEFAULT NULL,
    p_full_name VARCHAR(50) DEFAULT NULL,
    p_display_name VARCHAR(50) DEFAULT NULL,
    p_company VARCHAR(50) DEFAULT NULL,
    p_location VARCHAR(50) DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    v_user_id INT;
BEGIN
    -- Try to find existing user
    SELECT id INTO v_user_id
    FROM users
    WHERE (p_github_username IS NOT NULL AND github_username = p_github_username)
       OR (p_jira_email IS NOT NULL AND jira_email = p_jira_email)
    LIMIT 1;
    
    -- Create new user if not found
    IF v_user_id IS NULL THEN
        INSERT INTO users (github_username, jira_email, full_name, display_name, company, location)
        VALUES (p_github_username, p_jira_email, p_full_name, p_display_name, p_company, p_location)
        RETURNING id INTO v_user_id;
    ELSE
        -- Update existing user
        UPDATE users
        SET github_username = COALESCE(p_github_username, github_username),
            jira_email = COALESCE(p_jira_email, jira_email),
            full_name = COALESCE(p_full_name, full_name),
            display_name = COALESCE(p_display_name, display_name),
            company = COALESCE(p_company, company),
            location = COALESCE(p_location, location),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = v_user_id;
    END IF;
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;
```

#### get_latest_analysis
```sql
CREATE OR REPLACE FUNCTION get_latest_analysis(p_user_id INT)
RETURNS TABLE (
    id INT,
    analysis_data JSONB,
    analysis_date TIMESTAMP,
    version_number INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT aa.id, aa.analysis_data, aa.analysis_date, aa.version_number
    FROM analysis_archive aa
    WHERE aa.user_id = p_user_id
    ORDER BY aa.analysis_date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### Triggers

#### update_updated_at
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Auto-Update Schema

**Location:** `src/db/auto_update_schema.sql`

### Additional Tables

#### update_schedule
```sql
CREATE TABLE update_schedule (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    update_frequency_hours INT DEFAULT 24,
    last_updated TIMESTAMP,
    next_update TIMESTAMP,
    enabled BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_schedule_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Additional Views

#### v_update_status
```sql
CREATE OR REPLACE VIEW v_update_status AS
SELECT 
    us.id,
    u.github_username,
    u.jira_email,
    us.update_frequency_hours,
    us.last_updated,
    us.next_update,
    us.enabled,
    CASE 
        WHEN us.next_update < CURRENT_TIMESTAMP THEN 'Overdue'
        WHEN us.next_update < CURRENT_TIMESTAMP + INTERVAL '1 hour' THEN 'Due Soon'
        ELSE 'Scheduled'
    END AS status
FROM update_schedule us
JOIN users u ON us.user_id = u.id
ORDER BY us.next_update;
```

### Additional Functions

#### schedule_user_update
```sql
CREATE OR REPLACE FUNCTION schedule_user_update(
    p_user_id INT,
    p_frequency_hours INT DEFAULT 24
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO update_schedule (user_id, update_frequency_hours, next_update)
    VALUES (p_user_id, p_frequency_hours, CURRENT_TIMESTAMP + (p_frequency_hours || ' hours')::INTERVAL)
    ON CONFLICT (user_id) DO UPDATE
        SET update_frequency_hours = EXCLUDED.update_frequency_hours,
            next_update = CURRENT_TIMESTAMP + (p_frequency_hours || ' hours')::INTERVAL,
            enabled = TRUE;
END;
$$ LANGUAGE plpgsql;
```

---

## Database Queries

### Common Queries

#### Get All Users
```sql
SELECT id, github_username, jira_email, full_name, created_at 
FROM users 
ORDER BY created_at DESC;
```

#### Get User with Competences
```sql
SELECT * FROM user_competence_overview 
WHERE github_username = 'username'
ORDER BY procent DESC;
```

#### Get All Competences by Category
```sql
SELECT category, name, description 
FROM competence 
ORDER BY category, name;
```

#### Get User's Latest Analysis
```sql
SELECT * FROM get_latest_analysis(user_id);
```

#### Get Users Due for Update
```sql
SELECT * FROM v_update_status 
WHERE enabled = TRUE 
AND next_update < CURRENT_TIMESTAMP;
```

### Maintenance Queries

#### Clean Old Analyses
```sql
-- Archive keeps max 2 versions per user automatically
-- To manually clean old data:
DELETE FROM analysis_archive 
WHERE analysis_date < CURRENT_TIMESTAMP - INTERVAL '90 days';
```

#### Update All User Timestamps
```sql
UPDATE users SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
```

#### Rebuild Indexes
```sql
REINDEX TABLE users;
REINDEX TABLE competence;
REINDEX TABLE user_competence;
REINDEX TABLE analysis_archive;
```

---

## Setup Scripts

### Database Setup
**Location:** `scripts/database/setup_database.bat`

```batch
@echo off
echo Setting up Developer Skills Database...

psql -U postgres -c "CREATE DATABASE developer_skills;"
psql -U postgres -d developer_skills -f src\db\schema.sql

echo Database setup complete!
pause
```

### Apply Auto-Update Schema
**Location:** `scripts/database/apply_auto_update_schema.bat`

```batch
@echo off
echo Applying auto-update schema...

psql -U postgres -d developer_skills -f src\db\auto_update_schema.sql

echo Auto-update schema applied!
pause
```

### Quick Setup (All-in-One)
```powershell
# Run from project root
cd e:\Nymappe\Hovedopgave

# Create database
psql -U postgres -c "CREATE DATABASE developer_skills;"

# Apply main schema
psql -U postgres -d developer_skills -f src\db\schema.sql

# Apply auto-update schema (optional)
psql -U postgres -d developer_skills -f src\db\auto_update_schema.sql

# Enable pgAgent extension
psql -U postgres -d developer_skills -c "CREATE EXTENSION IF NOT EXISTS pgagent;"

echo "Database setup complete!"
```

---

## Backup and Restore

### Backup Database
```powershell
# Full backup
pg_dump -U postgres developer_skills > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Schema only
pg_dump -U postgres --schema-only developer_skills > schema_backup.sql

# Data only
pg_dump -U postgres --data-only developer_skills > data_backup.sql

# Specific table
pg_dump -U postgres -t user_competence developer_skills > user_competence_backup.sql
```

### Restore Database
```powershell
# Restore full backup
psql -U postgres -d developer_skills < backup.sql

# Restore schema only
psql -U postgres -d developer_skills < schema_backup.sql

# Restore data only
psql -U postgres -d developer_skills < data_backup.sql
```

---

## Performance Tuning

### Analyze Tables
```sql
ANALYZE users;
ANALYZE competence;
ANALYZE user_competence;
ANALYZE analysis_archive;
```

### View Index Usage
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Check Table Sizes
```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Security Best Practices

1. **Never commit passwords** - Use `.env` file
2. **Use prepared statements** - Prevents SQL injection
3. **Limit user privileges** - Grant only necessary permissions
4. **Regular backups** - Schedule daily backups
5. **Audit logs** - Monitor database access
6. **SSL connections** - Use encrypted connections in production

For more information, see the [Complete Setup Guide](COMPLETE_SETUP_GUIDE.md).
