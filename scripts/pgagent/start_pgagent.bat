@echo off
echo Starting pgAgent service...
net stop pgagent-pg18
sc config pgagent-pg18 start= auto
net start pgagent-pg18

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ pgAgent service is running!
    echo.
    echo Next steps:
    echo 1. Close and reopen pgAdmin 4
    echo 2. Right-click your database and select "Refresh"
    echo 3. You should now see "pgAgent Jobs" in the tree
) else (
    echo.
    echo ✗ Error starting pgAgent service
)

pause
