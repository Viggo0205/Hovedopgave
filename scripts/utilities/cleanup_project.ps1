# Cleanup Script - Remove unused files and folders

Write-Host "`n🧹 Cleaning up unused files...`n" -ForegroundColor Cyan

$itemsToRemove = @(
    # Nested duplicate folder (old structure)
    @{Path = "Hovedopgave"; Type = "Folder"; Reason = "Old duplicate structure, not used"},
    
    # Outdated config files
    @{Path = "json"; Type = "Folder"; Reason = "Old config files with outdated paths"},
    
    # Log files (can be regenerated)
    @{Path = "auto_update.log"; Type = "File"; Reason = "Old log file"},
    @{Path = "auto_update_worker.log"; Type = "File"; Reason = "Old log file"},
    @{Path = "scheduled_update.log"; Type = "File"; Reason = "Old log file"},
    @{Path = "mcp_server_debug.log"; Type = "File"; Reason = "Old log file"},
    
    # Python cache (regenerated automatically)
    @{Path = ".pytest_cache"; Type = "Folder"; Reason = "Test cache, regenerated on test run"},
    @{Path = ".coverage"; Type = "File"; Reason = "Coverage data, regenerated on test run"}
)

$removed = 0
$skipped = 0

foreach ($item in $itemsToRemove) {
    $fullPath = Join-Path "e:\Nymappe\Hovedopgave" $item.Path
    
    if (Test-Path $fullPath) {
        try {
            if ($item.Type -eq "Folder") {
                Write-Host "🗑️  Removing folder: $($item.Path)" -ForegroundColor Yellow
                Remove-Item -Recurse -Force $fullPath
            } else {
                Write-Host "🗑️  Removing file: $($item.Path)" -ForegroundColor Yellow
                Remove-Item -Force $fullPath
            }
            Write-Host "   ✅ Removed - $($item.Reason)" -ForegroundColor Gray
            $removed++
        } catch {
            Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
            $skipped++
        }
    } else {
        Write-Host "⏭️  Skipping: $($item.Path) (already gone)" -ForegroundColor DarkGray
        $skipped++
    }
}

# Clean all __pycache__ folders
Write-Host "`n🧹 Cleaning Python cache folders..." -ForegroundColor Cyan
$pycacheFolders = Get-ChildItem -Path "e:\Nymappe\Hovedopgave" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
foreach ($folder in $pycacheFolders) {
    try {
        Remove-Item -Recurse -Force $folder.FullName
        Write-Host "   ✅ Removed: $($folder.FullName.Replace('e:\Nymappe\Hovedopgave\', ''))" -ForegroundColor Gray
        $removed++
    } catch {
        Write-Host "   ❌ Failed: $($folder.FullName)" -ForegroundColor Red
    }
}

Write-Host "`n📊 Cleanup Summary:" -ForegroundColor Green
Write-Host "   ✅ Removed: $removed items" -ForegroundColor White
Write-Host "   ⏭️  Skipped: $skipped items" -ForegroundColor White

Write-Host "`n✨ Kept (these are useful):" -ForegroundColor Cyan
Write-Host "   📦 exports/ - GDPR-compliant profile exports" -ForegroundColor White
Write-Host "   📚 docs/ - All documentation" -ForegroundColor White
Write-Host "   🔧 scripts/ - Organized utility scripts" -ForegroundColor White
Write-Host "   🐍 src/ - Source code" -ForegroundColor White
Write-Host "   🧪 tests/ - Test suite" -ForegroundColor White
Write-Host "   📄 .env - Your API keys (never delete this!)" -ForegroundColor White
Write-Host "   📋 pyproject.toml - Python dependencies" -ForegroundColor White
Write-Host "   📖 README.md - Main documentation" -ForegroundColor White

Write-Host "`n✅ Cleanup complete!`n" -ForegroundColor Green
