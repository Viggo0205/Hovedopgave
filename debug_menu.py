#!/usr/bin/env python3
"""Debug script to test menu content"""

# Test what's in the skill_console.py file
with open('skill_console.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== CHECKING FILE CONTENT ===")
if 'Popular Tech Companies' in content:
    print("✅ Updated menu found in skill_console.py")
else:
    print("❌ Old menu in skill_console.py")

if 'Get All Collaborators' in content:
    print("⚠️  Old menu text also found")

print("\n=== MENU LINES ===")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'print("1.' in line:
        print(f"Line {i+1}: {line.strip()}")

print("\n=== TRYING TO IMPORT AND RUN ===")
try:
    from skill_console import SkillConsole
    console = SkillConsole()
    print("✅ Successfully imported SkillConsole")
    
    # Directly call the menu method to see what it prints
    print("\n=== DIRECT MENU CALL ===")
    console.menu()
    
except Exception as e:
    print(f"❌ Import/execution failed: {e}")
    import traceback
    traceback.print_exc()
