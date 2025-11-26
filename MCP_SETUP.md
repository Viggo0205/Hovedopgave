# MCP Integration Setup Guide

## 🚀 Quick Start - MCP Server Integration

Your system is now configured for proper MCP integration! Here's how to use it:

### 1. Test the MCP Server
```powershell
# Test the server functionality
python test_mcp_server.py
```

### 2. Run the MCP Client (Direct Mode)
```powershell
# Run the client with MCP server integration
python mcp_client.py
```

### 3. Claude Desktop Integration

#### Option A: Copy Configuration to Claude Desktop
```powershell
# Copy the configuration to Claude Desktop's config location
# Location: %APPDATA%\Claude\claude_desktop_config.json
cp json\claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

#### Option B: Manual Configuration
Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "developer-skill-analyzer": {
      "command": "python", 
      "args": [
        "c:\\Users\\victo\\Desktop\\Hovedopgave\\run_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "c:\\Users\\victo\\Desktop\\Hovedopgave\\src",
        "MOCK_MODE": "false",
        "GITHUB_TOKEN": "loaded-from-env-file"
      }
    }
  }
}
```

### 4. Configure GitHub Token

**Important**: Create a `.env` file in the project root directory:

```bash
# .env file (create this in the project root)
GITHUB_TOKEN=your_actual_github_personal_access_token_here
MOCK_MODE=false
```

**Security Notes**:
- The `.env` file is already in `.gitignore` and won't be committed to version control
- All configuration files will automatically load the token from this file
- Never hardcode tokens directly in configuration files

### 5. Available MCP Tools

Once connected, Claude Desktop will have access to these tools:

- **analyze_github_developer**: Real GitHub profile analysis
- **analyze_jira_developer**: Jira activity analysis  
- **get_skill_summary**: Combined GitHub + Jira skills
- **compare_developers**: Developer skill comparison
- **get_all_employees**: Team member discovery
- **get_technical_stack**: Organization tech stack

### 5. Example Claude Desktop Usage

```
You: Analyze Viggo0205's GitHub profile

Claude: I'll analyze Viggo0205's GitHub profile using the developer skill analyzer.
[Uses analyze_github_developer tool with real GitHub data]

You: Compare two developers' skills

Claude: I'll compare their skill profiles.
[Uses compare_developers tool]

You: What's our team's technical stack?

Claude: Let me get the current technical stack.
[Uses get_technical_stack tool]
```

## 🔧 Configuration Options

### Environment Variables (.env):
- `USE_REAL_MCP=true` - Enable MCP server integration
- `MOCK_MODE=false` - Use real GitHub data
- `DEFAULT_AI_MODE=claude` - Default to Claude AI
- `GITHUB_TOKEN=your_token` - GitHub API access

### Server Configuration:
- Real GitHub API integration via PyGithub
- FastMCP server with proper tool definitions
- Automatic fallback to mock data if APIs fail
- Comprehensive error handling and logging

## 🎯 Architecture

```
Claude Desktop → MCP Protocol → run_mcp_server.py → server.py → GitHub API
                                                              → Jira API
                                                              → AI Analyzers
                                                              → Skill Processing
```

## ✅ Verification Checklist

1. ✅ MCP server starts without errors: `python run_mcp_server.py`
2. ✅ Test script passes: `python test_mcp_server.py`
3. ✅ Client connects: `python mcp_client.py`
4. ✅ Claude Desktop shows tools: Check Claude Desktop after config
5. ✅ Real data flows: GitHub token works, MOCK_MODE=false

Your system is now a proper MCP server that Claude Desktop can connect to for real developer skill analysis!