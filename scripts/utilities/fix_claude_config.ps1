# Quick fix for Claude Desktop config after file reorganization

$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"

Write-Host "Fixing Claude Desktop MCP configuration..." -ForegroundColor Cyan

# Read current config
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Update the path to the moved start_mcp_server.bat
if ($config.mcpServers.'developer-skill-analyzer'.command -like "*start_mcp_server.bat") {
    $config.mcpServers.'developer-skill-analyzer'.command = "E:\Nymappe\Hovedopgave\scripts\start_mcp_server.bat"
    
    # Save updated config
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
    
    Write-Host "✅ Fixed! Updated path to: scripts\start_mcp_server.bat" -ForegroundColor Green
    Write-Host "`n⚠️  Please restart Claude Desktop for changes to take effect" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Config doesn't use start_mcp_server.bat, no changes made" -ForegroundColor Yellow
    Write-Host "Current command:" -ForegroundColor White
    Write-Host $config.mcpServers.'developer-skill-analyzer'.command
}
