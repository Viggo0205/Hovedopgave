@echo off
REM Scheduled Update Batch File
REM This runs the Python update script once and exits

cd /d E:\Nymappe\Hovedopgave
E:\Nymappe\python\python.exe scheduled_update.py

REM Exit with the same code as Python script
exit /b %ERRORLEVEL%
