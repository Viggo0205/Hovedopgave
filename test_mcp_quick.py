import sys
import os
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

from developer_skill_analyzer.config import Config

def test_mcp_config():
    print("Testing MCP Configuration...")
    config = Config()
    print(f"Mock mode: {config.mock_mode}")
    print(f"GitHub token configured: {'Yes' if config.github_token else 'No'}")
    if config.github_token:
        print(f"Token: {config.github_token[:10]}...")
    return config.github_token is not None

if __name__ == "__main__":
    success = test_mcp_config()
    print(f"Result: {'? Ready' if success else '? Token missing'}")
