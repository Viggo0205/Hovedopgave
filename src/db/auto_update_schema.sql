-- Automatic Update Schema Extensions
-- Adds automatic update tracking to existing schema

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

-- View to see update status of all users
CREATE OR REPLACE VIEW v_update_status AS
SELECT 
    u.id,
    u.github_username,
    u.jira_email,
    u.full_name,
    u.last_analyzed_at,
    u.auto_update_enabled,
    CASE 
        WHEN u.last_analyzed_at IS NULL THEN 'Never analyzed'
        WHEN u.last_analyzed_at < NOW() - INTERVAL '5 minutes' THEN 'Needs update'
        ELSE 'Up to date'
    END as update_status,
    EXTRACT(EPOCH FROM (NOW() - u.last_analyzed_at))/60 as minutes_since_update
FROM users u
ORDER BY u.last_analyzed_at NULLS FIRST;
