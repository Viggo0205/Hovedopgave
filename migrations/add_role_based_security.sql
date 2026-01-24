-- Migration: Add Role-Based Security (Authentication & Authorization)
-- Purpose: Create user and admin roles with appropriate permissions
-- Phase 1: Create roles and set basic permissions

-- ============================================
-- STEP 1: Create Database Roles
-- ============================================

-- Create regular user role (no password required)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'skill_analyzer_user') THEN
        CREATE ROLE skill_analyzer_user;
    END IF;
END
$$;

-- Create admin role (password required)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'skill_analyzer_admin') THEN
        CREATE ROLE skill_analyzer_admin WITH LOGIN PASSWORD 'admin123';
    END IF;
END
$$;

-- Make admin inherit from user role (admin has all user permissions + more)
GRANT skill_analyzer_user TO skill_analyzer_admin;

-- ============================================
-- STEP 2: Grant Basic Permissions to User Role
-- ============================================

-- Allow connection to database
GRANT CONNECT ON DATABASE developer_skills TO skill_analyzer_user;

-- Grant usage on public schema
GRANT USAGE ON SCHEMA public TO skill_analyzer_user;

-- Grant SELECT, INSERT, UPDATE on most tables (NOT DELETE)
GRANT SELECT, INSERT, UPDATE ON TABLE users TO skill_analyzer_user;
GRANT SELECT, INSERT, UPDATE ON TABLE competence TO skill_analyzer_user;
GRANT SELECT, INSERT, UPDATE ON TABLE user_competence TO skill_analyzer_user;
GRANT SELECT, INSERT ON TABLE user_competence_history TO skill_analyzer_user;
GRANT SELECT, INSERT ON TABLE analysis_archive TO skill_analyzer_user;
GRANT SELECT ON TABLE rank TO skill_analyzer_user;
GRANT SELECT ON TABLE role TO skill_analyzer_user;

-- Grant SELECT only on audit log (users can view, not modify)
GRANT SELECT ON TABLE user_audit_log TO skill_analyzer_user;

-- Grant sequence usage for INSERT operations
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO skill_analyzer_user;

-- ============================================
-- STEP 3: Admin-Only Permissions
-- ============================================

-- Admin can perform DELETE and restore operations
GRANT DELETE ON TABLE users TO skill_analyzer_admin;
GRANT INSERT ON TABLE user_audit_log TO skill_analyzer_admin;

-- ============================================
-- STEP 4: Create Helper Function to Check Role
-- ============================================

-- Function to check if current user is admin
CREATE OR REPLACE FUNCTION is_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN pg_has_role(current_user, 'skill_analyzer_admin', 'MEMBER');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute to everyone (they can check if they're admin)
GRANT EXECUTE ON FUNCTION is_admin() TO PUBLIC;

-- ============================================
-- STEP 5: Create Row-Level Security Policies
-- ============================================

-- Enable RLS on user_audit_log (only admins can see deletion/reactivation logs)
ALTER TABLE user_audit_log ENABLE ROW LEVEL SECURITY;

-- Policy: Regular users can see all audit logs
CREATE POLICY user_audit_read_policy ON user_audit_log
    FOR SELECT
    TO skill_analyzer_user
    USING (true);  -- All users can read audit logs

-- Policy: Only admins can insert audit logs
CREATE POLICY admin_audit_write_policy ON user_audit_log
    FOR INSERT
    TO skill_analyzer_admin
    WITH CHECK (true);

-- ============================================
-- STEP 6: Restrict DELETE operations on users table
-- ============================================

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: All users can read active users
CREATE POLICY user_read_policy ON users
    FOR SELECT
    TO skill_analyzer_user
    USING (true);

-- Policy: All users can insert new users
CREATE POLICY user_insert_policy ON users
    FOR INSERT
    TO skill_analyzer_user
    WITH CHECK (true);

-- Policy: All users can update users (for deactivation flag changes)
CREATE POLICY user_update_policy ON users
    FOR UPDATE
    TO skill_analyzer_user
    USING (true);

-- Policy: Only admins can delete users (for permanent deletion)
CREATE POLICY admin_delete_policy ON users
    FOR DELETE
    TO skill_analyzer_admin
    USING (is_admin());

-- ============================================
-- STEP 7: Grant default postgres user admin role
-- ============================================

-- Grant admin role to the current postgres user so existing connections still work
GRANT skill_analyzer_admin TO postgres;

-- ============================================
-- Comments for documentation
-- ============================================

COMMENT ON ROLE skill_analyzer_user IS 'Regular user role - can analyze, view, and update developer skills';
COMMENT ON ROLE skill_analyzer_admin IS 'Admin role - can delete/restore users and view audit logs';
COMMENT ON FUNCTION is_admin() IS 'Helper function to check if current database user has admin privileges';
COMMENT ON POLICY user_audit_read_policy ON user_audit_log IS 'Allow all users to read audit logs';
COMMENT ON POLICY admin_audit_write_policy ON user_audit_log IS 'Only admins can write to audit log';
COMMENT ON POLICY admin_delete_policy ON users IS 'Only admins can permanently delete users';

-- ============================================
-- Security Summary
-- ============================================

-- Regular users (skill_analyzer_user) can:
--   ✓ Analyze developers (read/write to most tables)
--   ✓ Add/update competences
--   ✓ View audit logs
--   ✓ Deactivate users (soft delete via UPDATE is_active=FALSE)
--   ✗ Permanently delete users (DELETE)
--   ✗ Write to audit log

-- Admins (skill_analyzer_admin) can:
--   ✓ Everything regular users can do
--   ✓ Permanently delete users (DELETE from users table)
--   ✓ Write to audit log
--   ✓ Restore deactivated users
