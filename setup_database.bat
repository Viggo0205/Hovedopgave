@echo off
REM Database initialization script for Developer Skill Analyzer
REM This script sets up the PostgreSQL database with schema and initial data

echo ========================================
echo Developer Skill Analyzer - Database Setup
echo ========================================
echo.

REM Check if PostgreSQL is installed
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PostgreSQL is not installed or not in PATH
    echo Please install PostgreSQL from https://www.postgresql.org/download/
    pause
    exit /b 1
)

echo [1/4] PostgreSQL found
echo.

REM Set variables
set PGUSER=postgres
set PGPASSWORD=1234
set DBNAME=
set SCHEMA_FILE=src\developer_skill_analyzer\db\schema.sql

REM Check if schema file exists
if not exist "%SCHEMA_FILE%" (
    echo ERROR: Schema file not found: %SCHEMA_FILE%
    echo Please ensure you're running this from the project root directory
    pause
    exit /b 1
)

echo [2/4] Schema file found
echo.

REM Create database (ignore errors if already exists)
echo [3/4] Creating database '%DBNAME%'...
psql -U %PGUSER% -c "CREATE DATABASE %DBNAME%;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Database created successfully
) else (
    echo Database already exists, continuing...
)
echo.

REM Run schema file
echo [4/4] Initializing schema and data...
psql -U %PGUSER% -d %DBNAME% -f "%SCHEMA_FILE%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to initialize database schema
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database setup completed successfully!
echo ========================================
echo.
echo Database: %DBNAME%
echo User: %PGUSER%
echo Connection string: postgresql://%PGUSER%:%PGPASSWORD%@localhost:5432/%DBNAME%
echo.
echo Next steps:
echo 1. Update your .env file with the DATABASE_URL
echo 2. Start the MCP server
echo 3. Use database tools to manage competences and analyses
echo.
pause
