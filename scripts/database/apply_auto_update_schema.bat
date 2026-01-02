@echo off
cd /d E:\Nymappe\Hovedopgave

echo Applying automatic update schema to database...
echo.

set PGPASSWORD=1234
"E:\PostgreSQL\18\bin\psql.exe" -U postgres -d developer_skills -f "src\db\auto_update_schema.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Schema applied successfully!
    echo.
    echo You can now run: python auto_update_worker.py
) else (
    echo.
    echo ✗ Error applying schema
)

pause
