### This guide explains how to create an automatic job that runs every 5 minutes to update all users in the database by analyzing their GitHub and Jira accounts.
## How the Current System Works

### the first step 1. Analysis Flow
### User Request then Analyzer then Service then API and finaly Database

**For GitHub:**
1. `GitHubService.get_user_profile(username)` - Gets profile from GitHub API
2. `GitHubService.get_user_repositories(username)` - Gets repos
3. `GitHubService.get_language_data(repos)` - Analyzes languages
4. `GitHubAnalyzer.analyze_developer(username)` - Processes data
5. `DatabaseRepository.save_analysis(user_id, data)` - Saves to database

**For Jira:**
1. `JiraService.get_user_profile(email)` - Gets profile from Jira API
2. `JiraService.get_user_issues(email)` - Gets issues
3. `JiraAnalyzer.analyze_developer(email)` - Processes data
4. `DatabaseRepository.save_analysis(user_id, data)` - Saves to database

### 2. **Database Structure**
```
users table:
- id (primary key)
- github_username (can be NULL)
- jira_email (can be NULL)
- full_name, display_name, company, location
- created_at, updated_at

analysis_archive table:
- id, user_id (foreign key)
- analysis_data (JSONB - stores full analysis)
- analysis_date, version_number (1 or 2 max)
```

### 3. **Key Functions**
- `get_or_create_user()` - Creates user or returns existing ID
- `save_analysis()` - Saves analysis with version management (max 2 versions)
- `analyze_developer()` - Performs GitHub/Jira analysis
- `update_user_competence()` - Updates skill percentages

## Step-by-Step Implementation

### Step 1: Add Tracking Column to Database

We need to track when each user was last analyzed to know who needs updating.

**File:** `src/db/auto_update_schema.sql`

```sql
-- Add column to track last analysis time
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_analyzed_at TIMESTAMP;

-- Add column to enable/disable auto-updates per user
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS auto_update_enabled BOOLEAN DEFAULT TRUE;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_last_analyzed 
ON users(last_analyzed_at) WHERE auto_update_enabled = TRUE;

-- Trigger to automatically update last_analyzed_at when analysis is saved
CREATE OR REPLACE FUNCTION update_user_last_analyzed()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET last_analyzed_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_last_analyzed ON analysis_archive;
CREATE TRIGGER trg_update_last_analyzed
AFTER INSERT ON analysis_archive
FOR EACH ROW
EXECUTE FUNCTION update_user_last_analyzed();

-- Function to get users that need updating
CREATE OR REPLACE FUNCTION get_users_for_update(
    minutes_threshold INT DEFAULT 5
)
RETURNS TABLE(
    user_id INT,
    github_username VARCHAR(50),
    jira_email VARCHAR(50),
    last_analyzed_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.github_username,
        u.jira_email,
        u.last_analyzed_at
    FROM users u
    WHERE u.auto_update_enabled = TRUE
      AND (
          u.last_analyzed_at IS NULL 
          OR u.last_analyzed_at < NOW() - (minutes_threshold || ' minutes')::INTERVAL
      )
      AND (u.github_username IS NOT NULL OR u.jira_email IS NOT NULL);
END;
$$ LANGUAGE plpgsql;
```

### Step 2: Create Python Worker Script

This script will run continuously and check for users needing updates every 5 minutes.

**File:** `auto_update_worker.py`

```python
"""
Automatic Update Worker
Runs every 5 minutes to analyze and update all users in the database.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from db.repository import DatabaseRepository
from db.connection import DatabaseConnection
from services.github_service import GitHubService
from services.jira_service import JiraService
from analyzers.github_analyzer import GitHubAnalyzer
from analyzers.jira_analyzer import JiraAnalyzer
from analyzers.skill_processor import SkillProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoUpdateWorker:
    """Worker that automatically updates user analyses."""
    
    def __init__(self, update_interval_minutes: int = 5):
        """
        Initialize the worker.
        
        Args:
            update_interval_minutes: How often to check for updates (default 5 minutes)
        """
        self.update_interval_minutes = update_interval_minutes
        self.db_repo = DatabaseRepository()
        self.skill_processor = SkillProcessor(self.db_repo)
        
        # Initialize services
        try:
            self.github_service = GitHubService()
            self.github_analyzer = GitHubAnalyzer(self.github_service)
            logger.info("✓ GitHub service initialized")
        except Exception as e:
            logger.warning(f"GitHub service not available: {e}")
            self.github_service = None
            self.github_analyzer = None
        
        try:
            self.jira_service = JiraService()
            self.jira_analyzer = JiraAnalyzer(self.jira_service)
            logger.info("✓ Jira service initialized")
        except Exception as e:
            logger.warning(f"Jira service not available: {e}")
            self.jira_service = None
            self.jira_analyzer = None
    
    def get_users_needing_update(self) -> List[Dict[str, Any]]:
        """Get list of users that need updating."""
        try:
            query = "SELECT * FROM get_users_for_update(%s)"
            results = self.db_repo.db.execute_query(
                query, 
                (self.update_interval_minutes,)
            )
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting users for update: {e}")
            return []
    
    async def analyze_and_save_github(self, user_id: int, github_username: str) -> bool:
        """
        Analyze GitHub account and save to database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.github_analyzer:
            logger.warning(f"GitHub analyzer not available for {github_username}")
            return False
        
        try:
            logger.info(f"Analyzing GitHub: {github_username}")
            
            # Perform analysis
            analysis_result = await self.github_analyzer.analyze_developer(github_username)
            
            # Extract skill assessment
            skill_assessment = {
                "language_skills": analysis_result.get("language_skills", {}),
                "expertise_areas": analysis_result.get("expertise_areas", {})
            }
            
            # Combine and process skills
            combined = self.skill_processor.combine_assessments({
                "github": skill_assessment
            })
            
            # Update competences
            for skill_name, skill_data in combined.get("skills", {}).items():
                proficiency = skill_data.get("proficiency_percent", 0)
                self.db_repo.update_user_competence(
                    user_id=user_id,
                    competence_name=skill_name,
                    procent=proficiency
                )
            
            # Save full analysis
            version = self.db_repo.save_analysis(
                user_id=user_id,
                analysis_data=analysis_result
            )
            
            skills_count = len(combined.get("skills", {}))
            logger.info(f"✓ {github_username}: v{version}, {skills_count} skills saved")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error analyzing {github_username}: {e}")
            return False
    
    async def analyze_and_save_jira(self, user_id: int, jira_email: str) -> bool:
        """
        Analyze Jira account and save to database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.jira_analyzer:
            logger.warning(f"Jira analyzer not available for {jira_email}")
            return False
        
        try:
            logger.info(f"Analyzing Jira: {jira_email}")
            
            # Perform analysis
            analysis_result = await self.jira_analyzer.analyze_developer(jira_email)
            
            # Extract skill assessment
            skill_assessment = {
                "language_skills": analysis_result.get("language_skills", {}),
                "expertise_areas": analysis_result.get("expertise_areas", {})
            }
            
            # Combine and process skills
            combined = self.skill_processor.combine_assessments({
                "jira": skill_assessment
            })
            
            # Update competences
            for skill_name, skill_data in combined.get("skills", {}).items():
                proficiency = skill_data.get("proficiency_percent", 0)
                self.db_repo.update_user_competence(
                    user_id=user_id,
                    competence_name=skill_name,
                    procent=proficiency
                )
            
            # Save full analysis
            version = self.db_repo.save_analysis(
                user_id=user_id,
                analysis_data=analysis_result
            )
            
            skills_count = len(combined.get("skills", {}))
            logger.info(f"✓ {jira_email}: v{version}, {skills_count} skills saved")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error analyzing {jira_email}: {e}")
            return False
    
    async def process_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single user (analyze GitHub and/or Jira).
        
        Args:
            user: User dictionary with id, github_username, jira_email
            
        Returns:
            Result dictionary
        """
        user_id = user['user_id']
        github_username = user.get('github_username')
        jira_email = user.get('jira_email')
        
        results = {
            'user_id': user_id,
            'github_username': github_username,
            'jira_email': jira_email,
            'github_success': False,
            'jira_success': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Analyze GitHub if available
        if github_username:
            results['github_success'] = await self.analyze_and_save_github(
                user_id, github_username
            )
        
        # Analyze Jira if available
        if jira_email:
            results['jira_success'] = await self.analyze_and_save_jira(
                user_id, jira_email
            )
        
        return results
    
    async def run_update_cycle(self):
        """Run one complete update cycle."""
        logger.info("=" * 60)
        logger.info(f"Starting update cycle at {datetime.now()}")
        logger.info("=" * 60)
        
        # Get users needing update
        users = self.get_users_needing_update()
        
        if not users:
            logger.info("No users need updating at this time")
            return
        
        logger.info(f"Found {len(users)} user(s) needing update")
        
        # Process each user
        results = []
        for user in users:
            result = await self.process_user(user)
            results.append(result)
            # Small delay between users to avoid rate limiting
            await asyncio.sleep(2)
        
        # Summary
        github_success = sum(1 for r in results if r['github_success'])
        jira_success = sum(1 for r in results if r['jira_success'])
        
        logger.info("=" * 60)
        logger.info(f"Update cycle complete:")
        logger.info(f"  - Users processed: {len(results)}")
        logger.info(f"  - GitHub updates: {github_success}")
        logger.info(f"  - Jira updates: {jira_success}")
        logger.info("=" * 60)
    
    async def run(self):
        """Run the worker continuously."""
        logger.info("🚀 Auto-update worker started")
        logger.info(f"Update interval: {self.update_interval_minutes} minutes")
        logger.info(f"GitHub available: {self.github_analyzer is not None}")
        logger.info(f"Jira available: {self.jira_analyzer is not None}")
        
        while True:
            try:
                await self.run_update_cycle()
            except Exception as e:
                logger.error(f"Error in update cycle: {e}")
            
            # Wait for next cycle
            wait_seconds = self.update_interval_minutes * 60
            logger.info(f"Waiting {self.update_interval_minutes} minutes until next cycle...")
            await asyncio.sleep(wait_seconds)


async def main():
    """Main entry point."""
    # You can change the interval here (in minutes)
    worker = AutoUpdateWorker(update_interval_minutes=5)
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
```

### Step 3: Apply Database Schema

Run this in PowerShell:

```powershell
cd E:\Nymappe\Hovedopgave

$env:PGPASSWORD = '1234'
& 'E:\PostgreSQL\18\bin\psql.exe' -U postgres -d developer_skills -f 'src\db\auto_update_schema.sql'
```

### Step 4: Test the System

#### 4.1 Check which users need updating:

```powershell
$env:PGPASSWORD = '1234'
& 'E:\PostgreSQL\18\bin\psql.exe' -U postgres -d developer_skills -c "SELECT * FROM get_users_for_update(5);"
```

#### 4.2 Run the worker once:

```powershell
cd E:\Nymappe\Hovedopgave
python auto_update_worker.py
```

You should see output like:
```
2025-12-14 10:00:00 - __main__ - INFO - 🚀 Auto-update worker started
2025-12-14 10:00:00 - __main__ - INFO - Update interval: 5 minutes
2025-12-14 10:00:00 - __main__ - INFO - ========================================
2025-12-14 10:00:00 - __main__ - INFO - Starting update cycle
2025-12-14 10:00:00 - __main__ - INFO - Found 2 user(s) needing update
2025-12-14 10:00:01 - __main__ - INFO - Analyzing GitHub: jonasosa
2025-12-14 10:00:05 - __main__ - INFO - ✓ jonasosa: v1, 4 skills saved
2025-12-14 10:00:10 - __main__ - INFO - Update cycle complete: 2 users, 2 success
```

### Step 5: Run as Windows Service

Create a batch file to run the worker:

**File:** `start_auto_update_worker.bat`

```batch
@echo off
cd /d E:\Nymappe\Hovedopgave
E:\Nymappe\python\python.exe auto_update_worker.py
pause
```

#### Option A: Run manually
Double-click `start_auto_update_worker.bat`

#### Option B: Run as Windows Scheduled Task (Recommended)

```powershell
$taskName = "DeveloperSkillAutoUpdate"
$scriptPath = "E:\Nymappe\Hovedopgave\start_auto_update_worker.bat"

$action = New-ScheduledTaskAction -Execute $scriptPath
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force

# Start it now
Start-ScheduledTask -TaskName $taskName
```

### Step 6: Monitoring

#### View logs:
```powershell
Get-Content auto_update.log -Tail 50 -Wait
```

#### Check when users were last analyzed:
```powershell
$env:PGPASSWORD = '1234'
& 'E:\PostgreSQL\18\bin\psql.exe' -U postgres -d developer_skills -c "
SELECT 
    id,
    github_username,
    jira_email,
    last_analyzed_at,
    auto_update_enabled
FROM users
ORDER BY last_analyzed_at DESC NULLS LAST;
"
```

#### Check analysis history:
```powershell
& 'E:\PostgreSQL\18\bin\psql.exe' -U postgres -d developer_skills -c "
SELECT 
    u.github_username,
    a.version_number,
    a.analysis_date,
    jsonb_array_length(a.analysis_data->'language_skills') as skills_count
FROM analysis_archive a
JOIN users u ON a.user_id = u.id
ORDER BY a.analysis_date DESC
LIMIT 10;
"
```

### Step 7: Configuration Options

#### Change update interval:
Edit `auto_update_worker.py` line 258:
```python
worker = AutoUpdateWorker(update_interval_minutes=10)  # Change to 10 minutes
```

#### Disable auto-update for specific user:
```sql
UPDATE users SET auto_update_enabled = FALSE WHERE github_username = 'someuser';
```

#### Re-enable:
```sql
UPDATE users SET auto_update_enabled = TRUE WHERE github_username = 'someuser';
```

#### Force immediate update for all users:
```sql
UPDATE users SET last_analyzed_at = NULL WHERE auto_update_enabled = TRUE;
```

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│  Windows Scheduled Task (starts at system boot)        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  auto_update_worker.py (runs continuously)              │
│  - Checks every 5 minutes                               │
│  - Queries: get_users_for_update(5)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  For each user:                                         │
│  1. GitHubAnalyzer.analyze_developer(username)          │
│  2. JiraAnalyzer.analyze_developer(email)               │
│  3. SkillProcessor.combine_assessments(...)             │
│  4. DatabaseRepository.save_analysis(...)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL Database                                    │
│  - analysis_archive (stores JSONB analysis)             │
│  - user_competence (stores skill percentages)           │
│  - Trigger updates last_analyzed_at automatically       │
└─────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Worker not starting?
```powershell
# Check Python path
Get-Command python

# Test imports
python -c "from src.config import Config; print('OK')"
```

### No users being updated?
```sql
-- Check if users exist
SELECT * FROM users;

-- Check if they need updating
SELECT * FROM get_users_for_update(5);

-- Check auto_update_enabled
SELECT github_username, auto_update_enabled, last_analyzed_at FROM users;
```

### GitHub/Jira API errors?
Check your `.env` file has correct tokens:
```
GITHUB_TOKEN=your_github_token
JIRA_URL=your_jira_url
JIRA_EMAIL=your_email
JIRA_API_TOKEN=your_jira_token
```

## Complete!

Your database will now automatically analyze and update all users every 5 minutes! 🎉
