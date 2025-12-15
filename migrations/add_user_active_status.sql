-- Migration: Add is_active and deactivated_at columns to users table
-- Date: 2025-12-14
-- Description: Implements soft delete functionality for US-25

-- Add columns if they don't exist
DO $$ 
BEGIN
    -- Add is_active column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='is_active') THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
        RAISE NOTICE 'Added is_active column';
    END IF;

    -- Add deactivated_at column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='deactivated_at') THEN
        ALTER TABLE users ADD COLUMN deactivated_at TIMESTAMP;
        RAISE NOTICE 'Added deactivated_at column';
    END IF;
END $$;

-- Create index on is_active for faster queries
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Set all existing users as active
UPDATE users SET is_active = TRUE WHERE is_active IS NULL;

-- Display results
SELECT 'Migration completed successfully. Total users:' as message, COUNT(*) as count FROM users;
SELECT 'Active users:' as message, COUNT(*) as count FROM users WHERE is_active = TRUE;
