@echo off
REM Run pytest for database tests

echo Running database unit tests...
echo.

cd /d E:\Nymappe\Hovedopgave

REM Run tests with verbose output
E:\Nymappe\python\python.exe -m pytest tests/ -v --tb=short

echo.
echo Tests complete!
pause
