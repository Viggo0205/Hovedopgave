# Claude Desktop MCP Setup Guide

This guide will help you set up the Developer Skill Analyzer MCP server with Claude Desktop from scratch.

## Prerequisites

### 1. Install Claude Desktop
- Download and install Claude Desktop from: https://claude.ai/download
- Launch the app and sign in with your Anthropic account
- **Important**: You do NOT need an API key for Claude Desktop

### 2. Install Python
- Install Python 3.8+ from: https://www.python.org/downloads/
- Make sure Python is added to your PATH during installation
- Verify installation: Open PowerShell and run `python --version`

### 3. Get a GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Set expiration (recommend 90 days or no expiration for development)
4. Select these scopes:
   - ✅ `public_repo` (Access public repositories)
   - ✅ `read:user` (Read user profile data)
   - ✅ `read:org` (Read organization membership)
5. Click "Generate token" and **copy the token immediately** (you won't see it again)

## Setup Steps

### Step 1: Clone the Repository
```powershell
# Clone the repository
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave
```

### Step 2: Install Dependencies
```powershell
# Install required Python packages
pip install fastmcp PyGithub python-dotenv atlassian-python-api pandas scikit-learn
```

### Step 3: Configure Environment Variables
```powershell
# Copy the example environment file
copy .env.example .env

# Edit the .env file with your favorite text editor
notepad .env
```

In the `.env` file, replace `your_github_personal_access_token_here` with your actual token:
```bash
GITHUB_TOKEN=ghp_your_actual_token_here
MOCK_MODE=false
```

**Important**: Never commit the `.env` file to version control!

### Step 4: Test the MCP Server
```powershell
# Test that the server starts correctly
python -m src.developer_skill_analyzer.server
```

You should see output like:
```
INFO: MCP Server starting...
INFO: GitHub token configured: Yes
INFO: Mock mode: False
```

Press Ctrl+C to stop the test.

### Step 5: Configure Claude Desktop

#### Option A: Copy Our Configuration (Recommended)
1. Copy the `claude_desktop_config.json` file from the `json/` folder in this repository
2. Paste it to your Claude Desktop config location:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

3. **Important**: Update the paths in the config file to match your setup:
   ```json
   {
     "mcpServers": {
       "developer-skill-analyzer": {
         "command": "C:\\path\\to\\your\\Hovedopgave\\start_mcp_server.bat",
         "env": {
           "GITHUB_TOKEN": "loaded-from-env-file",
           "MOCK_MODE": "false"
         }
       }
     }
   }
   ```

#### Option B: Manual Configuration
1. Create or edit your Claude Desktop config file at the location above
2. Add this configuration (update the path):
   ```json
   {
     "mcpServers": {
       "developer-skill-analyzer": {
         "command": "C:\\path\\to\\your\\Hovedopgave\\start_mcp_server.bat",
         "env": {
           "GITHUB_TOKEN": "loaded-from-env-file",
           "MOCK_MODE": "false"
         }
       }
     }
   }
   ```

### Step 6: Update the Batch File Path
Edit `start_mcp_server.bat` and update the paths to match your setup:
```batch
cd /d "C:\path\to\your\Hovedopgave"
set PYTHONPATH=C:\path\to\your\Hovedopgave\src
```

### Step 7: Restart Claude Desktop
1. Completely close Claude Desktop
2. Reopen Claude Desktop
3. Look for the 🔨 hammer icon in a new conversation - this indicates MCP tools are loaded

## Testing the Setup

### Test 1: Check MCP Tools Available
In Claude Desktop, start a new conversation and type:
```
What MCP tools do you have available?
```

You should see tools like:
- `analyze_github_profile`
- `analyze_github_repository` 
- `get_skill_summary`

### Test 2: Analyze a GitHub Profile
```
Can you analyze the GitHub profile for "octocat"?
```

### Test 3: Analyze Your Own Profile
```
Can you analyze my GitHub profile? My username is [your-github-username]
```

## Troubleshooting

### Problem: No MCP tools available
**Solution**: 
1. Check that Claude Desktop config file is in the correct location
2. Verify the path to `start_mcp_server.bat` is correct
3. Restart Claude Desktop completely

### Problem: "GitHub token not found" error
**Solution**:
1. Verify your `.env` file exists and contains `GITHUB_TOKEN=your_token`
2. Make sure the token has the correct permissions
3. Test the token at: https://api.github.com/user (paste in browser with `?access_token=your_token`)

### Problem: "403 Forbidden" or "401 Unauthorized" 
**Solution**:
1. Your GitHub token may be expired or invalid
2. Generate a new token with the correct scopes
3. Update your `.env` file

### Problem: Python path issues
**Solution**:
1. Make sure Python is installed and in your PATH
2. Try using the full path to python.exe in the batch file
3. Install packages globally: `pip install fastmcp PyGithub python-dotenv`

### Problem: Batch file doesn't work
**Solution**:
1. Right-click `start_mcp_server.bat` → "Edit"
2. Update all paths to match your system
3. Test by double-clicking the batch file - it should show loading messages

## Security Notes

- ✅ Your `.env` file is in `.gitignore` and won't be committed to Git
- ✅ Never share your GitHub Personal Access Token
- ✅ The MCP server only runs locally on your machine
- ✅ Claude Desktop connects to the local MCP server, not external services

## What You Can Do

Once set up, you can ask Claude Desktop to:

- **Analyze any GitHub profile**: "Analyze the skills of [username]"
- **Analyze repositories**: "What technologies are used in [repo-url]?"
- **Compare developers**: "Compare the skills of user1 vs user2"
- **Get skill summaries**: "What are the top Python developers you can find?"
- **Analyze organizations**: "Analyze the team skills at [organization]"

The MCP server will fetch real data from GitHub and provide detailed analysis of programming languages, frameworks, activity patterns, and skill levels.

## Need Help?

1. Check the main `README.md` for more details
2. Review the `MCP_SETUP.md` for technical details  
3. Make sure all file paths in your config match your system
4. Restart Claude Desktop after any configuration changes

Happy analyzing! 🚀