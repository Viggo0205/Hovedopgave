"""
Automatic Claude Desktop MCP Server Setup Script

This script automatically configures Claude Desktop to use the Developer Skill Analyzer MCP server.
It handles:
- Finding Claude Desktop config location
- Backing up existing config
- Installing uv if needed
- Updating MCP server configuration
- Loading environment variables
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path


def get_claude_config_path():
    """Get the Claude Desktop config file path based on OS."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise Exception("APPDATA environment variable not found")
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def check_uv_installed():
    """Check if uv is installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_uv_path():
    """Get the full path to uv executable."""
    if sys.platform == "win32":
        uv_path = Path.home() / ".local" / "bin" / "uv.exe"
        if uv_path.exists():
            return str(uv_path)
        # Try system PATH
        result = subprocess.run(["where", "uv"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    else:
        result = subprocess.run(["which", "uv"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    return "uv"  # Fallback to just "uv" in PATH


def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


def create_mcp_config(project_dir, env_vars):
    """
    Create MCP server configuration.
    
    Note: Environment variables are NOT included in the config file.
    The server automatically reads from .env file in the project directory.
    This keeps secrets out of the config and git repository.
    """
    uv_path = get_uv_path()
    
    config = {
        "mcpServers": {
            "developer-skill-analyzer": {
                "command": uv_path,
                "args": [
                    "--directory",
                    str(project_dir),
                    "run",
                    "src/server.py"
                ]
            }
        }
    }
    
    return config


def backup_existing_config(config_path):
    """Backup existing Claude config if it exists."""
    if config_path.exists():
        backup_path = config_path.parent / f"claude_desktop_config.backup.json"
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backed up existing config to: {backup_path}")
        return True
    return False


def merge_configs(existing_config, new_server_config):
    """Merge new MCP server into existing config."""
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Add or update our server
    existing_config["mcpServers"]["developer-skill-analyzer"] = new_server_config["mcpServers"]["developer-skill-analyzer"]
    
    return existing_config


def setup_claude_desktop():
    """Main setup function."""
    print("=" * 60)
    print("Claude Desktop MCP Server Setup")
    print("Developer Skill Analyzer")
    print("=" * 60)
    print()
    
    # Get project directory
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 Project directory: {project_dir}")
    
    # Check uv installation
    print("\n🔍 Checking uv installation...")
    if not check_uv_installed():
        print("❌ uv is not installed!")
        print("\nTo install uv:")
        if sys.platform == "win32":
            print("   powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        else:
            print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("\nPlease install uv and run this script again.")
        return False
    else:
        uv_path = get_uv_path()
        print(f"✅ uv found at: {uv_path}")
    
    # Load environment variables
    print("\n🔍 Loading environment variables...")
    env_vars = load_env_file()
    if "GITHUB_TOKEN" in env_vars:
        print(f"✅ GITHUB_TOKEN found ({env_vars['GITHUB_TOKEN'][:10]}...)")
    else:
        print("⚠️  GITHUB_TOKEN not found in .env file")
    
    # Get Claude config path
    try:
        claude_config_path = get_claude_config_path()
        print(f"\n📍 Claude config path: {claude_config_path}")
    except Exception as e:
        print(f"❌ Error finding Claude config: {e}")
        return False
    
    # Create config directory if it doesn't exist
    claude_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing config
    print("\n💾 Checking for existing config...")
    had_backup = backup_existing_config(claude_config_path)
    
    # Load existing config or create new
    existing_config = {}
    if claude_config_path.exists():
        with open(claude_config_path, 'r', encoding='utf-8') as f:
            existing_config = json.load(f)
        print("✅ Loaded existing config")
    else:
        print("📝 Creating new config")
    
    # Create new MCP server config
    new_config = create_mcp_config(project_dir, env_vars)
    
    # Merge configs
    final_config = merge_configs(existing_config, new_config)
    
    # Write config
    print("\n✍️  Writing configuration...")
    with open(claude_config_path, 'w', encoding='utf-8') as f:
        json.dump(final_config, f, indent=2)
    
    # Also save a local copy
    local_config_path = project_dir / "json" / "claude_desktop_config.json"
    local_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_config_path, 'w', encoding='utf-8') as f:
        json.dump(final_config, f, indent=2)
    
    print(f"✅ Config written to: {claude_config_path}")
    print(f"✅ Local copy saved to: {local_config_path}")
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Claude Desktop")
    print("2. Look for 🔌 developer-skill-analyzer connection")
    print("3. Test with: 'Which MCP tools do you have?'")
    print("\nAvailable tools:")
    print("  - analyze_github_developer")
    print("  - export_developer_profile")
    print("  - get_github_profile")
    print("  - compare_developers")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = setup_claude_desktop()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
