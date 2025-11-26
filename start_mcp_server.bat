@echo off
REM MCP Server Launcher for Claude Desktop
REM This wrapper ensures proper environment setup for the MCP server

cd /d "c:\Users\victo\Desktop\Hovedopgave"
set PYTHONPATH=c:\Users\victo\Desktop\Hovedopgave\src

REM Load environment variables from .env file
if exist ".env" (
    echo Loading configuration from .env file...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if "%%a"=="GITHUB_TOKEN" set GITHUB_TOKEN=%%b
        if "%%a"=="MOCK_MODE" set MOCK_MODE=%%b
    )
) else (
    echo Warning: .env file not found. Please create it with GITHUB_TOKEN=your_token_here
    echo Using environment variables if available...
)

REM Default to real mode if not specified
if not defined MOCK_MODE set MOCK_MODE=false
if not defined GITHUB_TOKEN (
    echo ERROR: GITHUB_TOKEN not found in .env file or environment
    pause
    exit /b 1
)

REM Set additional aliases for compatibility
set GITHUB_ACCESS_TOKEN=%GITHUB_TOKEN%

REM Create a log file for debugging (silent)
echo %date% %time% - Starting MCP Server >> mcp_server_debug.log
echo MOCK_MODE: %MOCK_MODE% >> mcp_server_debug.log
echo GITHUB_TOKEN: %GITHUB_TOKEN:~0,10%... >> mcp_server_debug.log
echo WORKING_DIR: %CD% >> mcp_server_debug.log

REM No console output - Claude Desktop expects clean JSON from MCP server

REM Start the MCP server
python -m src.developer_skill_analyzer.server