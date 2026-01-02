@echo off
echo Configuring pgAgent service to connect to developer_skills database...
echo.

REM Stop the service first
net stop pgagent-pg18

REM Get the current service configuration
for /f "tokens=2*" %%a in ('sc qc pgagent-pg18 ^| find "BINARY_PATH_NAME"') do set SERVICE_PATH=%%b

echo Current service path: %SERVICE_PATH%
echo.

REM Set the new service path with connection string
sc config pgagent-pg18 binPath= "\"E:\PostgreSQL\18\bin\pgagent.exe\" RUN pgagent-pg18 hostaddr=127.0.0.1 port=5432 dbname=developer_skills user=postgres password=1234"

if %ERRORLEVEL% EQU 0 (
    echo Service configured successfully
    echo Starting pgAgent service...
    net start pgagent-pg18
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✓ pgAgent is now running and connected to developer_skills!
        echo.
        echo The job will now run automatically every 5 minutes.
    ) else (
        echo ✗ Failed to start pgAgent service
    )
) else (
    echo ✗ Failed to configure service
)

pause
