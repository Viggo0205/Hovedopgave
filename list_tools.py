import sys
sys.path.insert(0, 'src')

from developer_skill_analyzer.server import mcp

tools = mcp.get_tools()
print(f"Total tools registered: {len(tools)}\n")

for tool in sorted(tools, key=lambda x: x.name):
    print(f"  - {tool.name}")

# Check if save_analysis_to_database is in the list
save_tool = [t for t in tools if 'save_analysis' in t.name]
if save_tool:
    print(f"\n✓ save_analysis_to_database IS registered")
    print(f"  Type: {type(save_tool[0])}")
    print(f"  Callable: {callable(save_tool[0])}")
else:
    print(f"\n✗ save_analysis_to_database NOT found in tools")
