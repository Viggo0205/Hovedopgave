@echo off
REM MCP Server Launcher for Claude Desktop
REM This wrapper ensures proper environment setup for the MCP server

cd /d "E:\Nymappe\Hovedopgave"
set PYTHONPATH=E:\Nymappe\Hovedopgave\src

REM Load environment variables from .env file
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if "%%a"=="GITHUB_TOKEN" set GITHUB_TOKEN=%%b
        if "%%a"=="MOCK_MODE" set MOCK_MODE=%%b
    )
)

REM Default to real mode if not specified
if not defined MOCK_MODE set MOCK_MODE=false
if not defined GITHUB_TOKEN exit /b 1

REM Set additional aliases for compatibility
set GITHUB_ACCESS_TOKEN=%GITHUB_TOKEN%

REM Create a log file for debugging (redirect to file, not console)
echo %date% %time% - Starting MCP Server >> mcp_server_debug.log 2>&1
echo MOCK_MODE: %MOCK_MODE% >> mcp_server_debug.log 2>&1
echo GITHUB_TOKEN: %GITHUB_TOKEN:~0,10%... >> mcp_server_debug.log 2>&1
echo WORKING_DIR: %CD% >> mcp_server_debug.log 2>&1

REM Start the MCP server - NO console output allowed

REM Start the MCP server
python -m src.developer_skill_analyzer.server