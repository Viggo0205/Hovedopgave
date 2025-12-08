-- Developer Skill Analyzer Database Schema
-- DROP TABLES
DROP TABLE IF EXISTS analysis_archive CASCADE;
DROP TABLE IF EXISTS user_competence CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS competence CASCADE;
DROP TABLE IF EXISTS rank CASCADE;
DROP TABLE IF EXISTS role CASCADE;


-- ROLE
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);


-- USERS
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

-- Index for faster lookups
CREATE INDEX idx_users_github ON users(github_username);
CREATE INDEX idx_users_jira ON users(jira_email);


-- COMPETENCE
CREATE TABLE competence (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for category lookups
CREATE INDEX idx_competence_category ON competence(category);


-- RANK
CREATE TABLE rank (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    min_percent INT NOT NULL,
    max_percent INT NOT NULL
);

-- Insert ranks
INSERT INTO rank (id, name, min_percent, max_percent)
VALUES 
    (1, 'Beginner', 0, 24),
    (2, 'Intermediate', 25, 49),
    (3, 'Advanced', 50, 74),
    (4, 'Expert', 75, 100)
ON CONFLICT (id) DO NOTHING;


-- USER_COMPETENCE
CREATE TABLE user_competence (
    user_id INT NOT NULL,
    competence_id INT NOT NULL,
    procent NUMERIC(5,2) NOT NULL CHECK (procent >= 0 AND procent <= 100),
    usage_frequency INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_competence FOREIGN KEY (competence_id) REFERENCES competence(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, competence_id)
);


-- ANALYSIS_ARCHIVE: Stores historical analysis data (max 2 versions per user)
CREATE TABLE analysis_archive (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    analysis_data JSONB NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version_number INT NOT NULL,
    
    CONSTRAINT fk_archive_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_version CHECK (version_number IN (1, 2))
);

-- Index for faster version queries
CREATE INDEX idx_archive_user_version ON analysis_archive(user_id, version_number);


-- VIEW: User Competence Overview
CREATE OR REPLACE VIEW user_competence_overview AS
SELECT 
    u.id AS user_id,
    u.github_username,
    u.jira_email,
    u.full_name,
    u.display_name,
    u.company,
    u.location,
    r.name AS role_name,
    c.id AS competence_id,
    c.name AS competence_name,
    c.category AS competence_category,
    uc.procent,
    uc.usage_frequency,
    rk.name AS rank_name,
    uc.last_updated
FROM user_competence uc
JOIN users u ON uc.user_id = u.id
JOIN competence c ON uc.competence_id = c.id
LEFT JOIN role r ON u.role_id = r.id
JOIN rank rk 
    ON uc.procent BETWEEN rk.min_percent AND rk.max_percent
ORDER BY u.id, c.category, c.name;


-- VIEW: Competence Categories (for skill processor initialization)
CREATE OR REPLACE VIEW competence_categories AS
SELECT 
    category,
    array_agg(name ORDER BY name) AS competences
FROM competence
GROUP BY category
ORDER BY category;


-- STORED PROCEDURE: Add new competence
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


-- STORED PROCEDURE: Update user competence
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


-- STORED PROCEDURE: Save analysis with version management (keep max 2 versions)
CREATE OR REPLACE FUNCTION save_analysis(
    p_user_id INT,
    p_analysis_data JSONB
)
RETURNS INT AS $$
DECLARE
    v_current_count INT;
    v_oldest_id INT;
    v_new_version INT;
BEGIN
    -- Count existing versions for this user
    SELECT COUNT(*) INTO v_current_count
    FROM analysis_archive
    WHERE user_id = p_user_id;
    
    -- If we have 2 versions, remove the oldest (version 1) and shift version 2 to version 1
    IF v_current_count >= 2 THEN
        -- Delete version 1
        DELETE FROM analysis_archive
        WHERE user_id = p_user_id AND version_number = 1;
        
        -- Update version 2 to version 1
        UPDATE analysis_archive
        SET version_number = 1
        WHERE user_id = p_user_id AND version_number = 2;
        
        v_new_version := 2;
    ELSIF v_current_count = 1 THEN
        v_new_version := 2;
    ELSE
        v_new_version := 1;
    END IF;
    
    -- Insert new analysis as the latest version
    INSERT INTO analysis_archive (user_id, analysis_data, version_number)
    VALUES (p_user_id, p_analysis_data, v_new_version);
    
    RETURN v_new_version;
END;
$$ LANGUAGE plpgsql;


-- STORED PROCEDURE: Get latest analysis
CREATE OR REPLACE FUNCTION get_latest_analysis(p_user_id INT)
RETURNS TABLE(
    id INT,
    analysis_data JSONB,
    analysis_date TIMESTAMP,
    version_number INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT a.id, a.analysis_data, a.analysis_date, a.version_number
    FROM analysis_archive a
    WHERE a.user_id = p_user_id
    ORDER BY a.version_number DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;


-- STORED PROCEDURE: Get or create user
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
    WHERE (github_username = p_github_username AND p_github_username IS NOT NULL)
       OR (jira_email = p_jira_email AND p_jira_email IS NOT NULL)
    LIMIT 1;
    
    -- If user exists, update their info
    IF v_user_id IS NOT NULL THEN
        UPDATE users
        SET 
            github_username = COALESCE(p_github_username, github_username),
            jira_email = COALESCE(p_jira_email, jira_email),
            full_name = COALESCE(p_full_name, full_name),
            display_name = COALESCE(p_display_name, display_name),
            company = COALESCE(p_company, company),
            location = COALESCE(p_location, location),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = v_user_id;
    ELSE
        -- Create new user
        INSERT INTO users (github_username, jira_email, full_name, display_name, company, location)
        VALUES (p_github_username, p_jira_email, p_full_name, p_display_name, p_company, p_location)
        RETURNING id INTO v_user_id;
    END IF;
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;


-- Insert default competences
INSERT INTO competence (name, category, description) VALUES
-- Programming Languages
('Python', 'programming_languages', 'Python programming language'),
('JavaScript', 'programming_languages', 'JavaScript programming language'),
('TypeScript', 'programming_languages', 'TypeScript programming language'),
('Java', 'programming_languages', 'Java programming language'),
('C#', 'programming_languages', 'C# programming language'),
('C++', 'programming_languages', 'C++ programming language'),
('Go', 'programming_languages', 'Go programming language'),
('Rust', 'programming_languages', 'Rust programming language'),
('PHP', 'programming_languages', 'PHP programming language'),
('Ruby', 'programming_languages', 'Ruby programming language'),

-- Frameworks
('React', 'frameworks_tools', 'React JavaScript framework'),
('Angular', 'frameworks_tools', 'Angular framework'),
('Vue.js', 'frameworks_tools', 'Vue.js framework'),
('Django', 'frameworks_tools', 'Django Python framework'),
('Flask', 'frameworks_tools', 'Flask Python framework'),
('Spring', 'frameworks_tools', 'Spring Java framework'),
('Express', 'frameworks_tools', 'Express Node.js framework'),
('Node.js', 'frameworks_tools', 'Node.js runtime'),

-- Tools
('Docker', 'frameworks_tools', 'Docker containerization'),
('Kubernetes', 'frameworks_tools', 'Kubernetes orchestration'),
('Git', 'frameworks_tools', 'Git version control'),
('Jenkins', 'frameworks_tools', 'Jenkins CI/CD'),

-- Databases
('PostgreSQL', 'databases', 'PostgreSQL database'),
('MySQL', 'databases', 'MySQL database'),
('MongoDB', 'databases', 'MongoDB database'),
('Redis', 'databases', 'Redis cache'),
('Elasticsearch', 'databases', 'Elasticsearch search engine'),

-- Soft Skills
('Communication', 'soft_skills', 'Written and verbal communication'),
('Leadership', 'soft_skills', 'Team leadership'),
('Problem Solving', 'soft_skills', 'Problem solving ability'),
('Collaboration', 'soft_skills', 'Team collaboration'),
('Documentation', 'soft_skills', 'Documentation skills'),

-- Domain Knowledge
('Web Development', 'domain_knowledge', 'Web development'),
('Mobile Development', 'domain_knowledge', 'Mobile app development'),
('DevOps', 'domain_knowledge', 'DevOps practices'),
('Data Science', 'domain_knowledge', 'Data science'),
('Security', 'domain_knowledge', 'Security practices')
ON CONFLICT (name) DO NOTHING;
