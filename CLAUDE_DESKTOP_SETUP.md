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
   - ✅ `repo` (Access repositories)
   - ✅ `read:user` (Read user profile data)
5. Click "Generate token" and **copy the token immediately** (you won't see it again)

## Setup Steps
### Step 1: Clone the Repository
```powershell
# Clone the repository
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave

# Create virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### Step 2: Install Dependencies
```powershell
# Install required Python packages
pip install fastmcp PyGithub python-dotenv
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
```
**Important**: Never commit the `.env` file to version control!

### Step 4: Test the MCP Server
```powershell
# Test that the server imports correctly
python -c "from src.mcp.server import main; print('✅ Server imports successfully')"
```

### Step 5: Configure Claude Desktop
Create or edit your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

Add this configuration (**update the path to match your setup**):
```json
{
  "mcpServers": {
    "developer-skill-analyzer": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "C:\\path\\to\\your\\Hovedopgave",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\your\\Hovedopgave\\src"
      }
    }
  }
}
```

**Replace `C:\\path\\to\\your\\Hovedopgave` with your actual project path!**
### Step 6: Restart Claude Desktop
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
- `analyze_github_developer`
- `get_github_profile` 
- `compare_developers`

### Test 2: Analyze a GitHub Profile
```
Can you analyze the GitHub developer "octocat"?
```

### Test 3: Analyze Your Own Profile
```
Can you analyze my GitHub profile? My username is [your-github-username]
```

### Test 4: Compare Developers
```
Compare GitHub developers "torvalds" and "gvanrossum"
```

### Test 5: Check Available Languages
```
Show me what programming languages you can analyze
```

## Troubleshooting
### Problem: No MCP tools available
**Solution**: 
1. Check that Claude Desktop config file is in the correct location
2. Verify the paths in the config are correct (use forward slashes or double backslashes)
3. Restart Claude Desktop completely
4. Check that virtual environment is activated if using one

### Problem: "GitHub token not found" error
**Solution**:
1. Verify your `.env` file exists and contains `GITHUB_TOKEN=your_token`
2. Make sure the token has the correct permissions (`repo` and `read:user` scopes)
3. Test the token at: https://api.github.com/user (add `?access_token=your_token` to URL)

### Problem: "403 Forbidden" or "401 Unauthorized" 
**Solution**:
1. Your GitHub token may be expired or invalid
2. Generate a new token with the correct scopes
3. Update your `.env` file

### Problem: Import/Module errors
**Solution**:
1. Make sure you're in the correct directory (`cwd` in config)
2. Verify PYTHONPATH is set correctly in Claude Desktop config
3. Ensure all dependencies are installed: `pip install fastmcp PyGithub python-dotenv`

### Problem: Server won't start
**Solution**:
1. Test the import: `python -c "from src.mcp.server import main; print('OK')"`
2. Check that `.env` file exists with valid GitHub token
3. Verify virtual environment is activated if using one

## Available MCP Features
Once set up, your MCP server provides:

### Tools:
- **analyze_github_developer**: Complete skill analysis with language levels (Expert/Advanced/Intermediate/Beginner)
- **get_github_profile**: Quick profile lookup with top languages  
- **compare_developers**: Side-by-side developer comparison

### Resources:
- **github://available-languages**: List of all supported programming languages

### Prompts:
- **analyze-developer-skills**: Template for comprehensive skill analysis

## What You Can Do
Once set up, you can ask Claude Desktop to:
- **Analyze any GitHub profile**: "Analyze the GitHub developer 'username'"
- **Compare developers**: "Compare the skills of user1 vs user2"
- **Get language info**: "What programming languages can you analyze?"
- **Quick profiles**: "Get basic GitHub profile info for 'username'"

The MCP server will fetch real data from GitHub API and provide detailed analysis of:
- Programming languages and skill levels
- Repository statistics  
- Expertise area categorization (Web Frontend, Backend, Mobile, Data Science, etc.)

## Security Notes
- ✅ Your `.env` file is in `.gitignore` and won't be committed to Git
- ✅ Never share your GitHub Personal Access Token
- ✅ The MCP server only runs locally on your machine
- ✅ Claude Desktop connects to the local MCP server, not external services

## Need Help?
1. Check the main `README.md` for more details
2. Review the `MCP_SETUP.md` for technical details  
3. Make sure all file paths in your config match your system
4. Restart Claude Desktop after any configuration changes

for at finde uv skriv i powershell "Get-Command uv" først tjek om den kan finde det uden fuld path så skriv "where uv"

Happy analyzing! 🚀
