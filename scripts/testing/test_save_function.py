"""
Test the save_analysis_to_database function directly.
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from developer_skill_analyzer.server import save_analysis_to_database

print("Testing save_analysis_to_database function")
print("=" * 50)
print(f"Type: {type(save_analysis_to_database)}")
print(f"Callable: {callable(save_analysis_to_database)}")
print(f"Has __call__: {hasattr(save_analysis_to_database, '__call__')}")

# Check if it's a FunctionTool wrapper
if hasattr(save_analysis_to_database, '__class__'):
    print(f"Class: {save_analysis_to_database.__class__}")
    print(f"MRO: {save_analysis_to_database.__class__.__mro__}")
    
# List available attributes/methods
print("\nAvailable attributes:")
for attr in dir(save_analysis_to_database):
    if not attr.startswith('_'):
        print(f"  - {attr}")

# Check if there's a wrapped function
if hasattr(save_analysis_to_database, 'func'):
    print(f"\nWrapped function: {save_analysis_to_database.func}")
    print(f"Wrapped callable: {callable(save_analysis_to_database.func)}")
    
# Try to get the function metadata
if hasattr(save_analysis_to_database, 'name'):
    print(f"\nTool name: {save_analysis_to_database.name}")
if hasattr(save_analysis_to_database, 'description'):
    print(f"Tool description: {save_analysis_to_database.description}")
