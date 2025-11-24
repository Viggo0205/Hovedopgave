@echo off
cd /d "c:\Users\victo\Desktop\Hovedopgave\Hovedopgave"
echo Current directory: %cd%
echo Python version:
python --version
echo.
echo File content check:
python -c "with open('skill_console.py', 'r') as f: content=f.read(); print('✅ Updated menu found' if 'Popular Tech Companies' in content else '❌ Old menu found')"
echo.
echo Starting skill console...
python skill_console.py
pause
