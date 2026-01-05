-- Migration: Add audit log and admin tracking for user deletions/deactivations
-- Purpose: Track who performed administrative actions and when (GDPR compliance)

-- Create audit log table
CREATE TABLE IF NOT EXISTS user_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'deactivate', 'reactivate', 'delete_permanently'
    performed_by VARCHAR(100),     -- Admin identifier (GitHub username or email)
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,                   -- Optional reason for the action
    additional_data JSONB          -- Any additional context
);

-- Index for faster lookups
CREATE INDEX idx_audit_user ON user_audit_log(user_id);
CREATE INDEX idx_audit_action ON user_audit_log(action);
CREATE INDEX idx_audit_performed_at ON user_audit_log(performed_at);

-- Add deactivated_by field to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS deactivated_by VARCHAR(100);

-- Add comment
COMMENT ON TABLE user_audit_log IS 'Audit log for tracking administrative actions on user accounts';
COMMENT ON COLUMN users.deactivated_by IS 'Administrator who deactivated this user';
