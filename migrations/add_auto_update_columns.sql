-- Migration: Add auto-update columns for scheduled jobs
-- Purpose: Support automated skill analysis updates via pgAgent

-- Add last_analyzed_at to track when a user was last analyzed
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_analyzed_at TIMESTAMP;

-- Add auto_update_enabled to allow users to opt-out of automatic updates
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS auto_update_enabled BOOLEAN DEFAULT TRUE;

-- Add comments
COMMENT ON COLUMN users.last_analyzed_at IS 'Timestamp of last automated skill analysis';
COMMENT ON COLUMN users.auto_update_enabled IS 'Whether to include user in automated updates (default: TRUE)';
