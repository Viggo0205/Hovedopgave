# Fix pgAgent Service Account and Start Service
# Run as Administrator

Write-Host "Fixing pgAgent service configuration..." -ForegroundColor Cyan
Write-Host ""

# Stop the service if running
Write-Host "Stopping service..." -ForegroundColor Yellow
Stop-Service pgagent-pg18 -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Reconfigure service to run as LocalSystem (has more permissions)
Write-Host "Configuring service account..." -ForegroundColor Yellow
sc.exe config pgagent-pg18 obj= "LocalSystem" password= ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Service account configured" -ForegroundColor Green
    Write-Host ""
    
    # Start the service
    Write-Host "Starting pgAgent service..." -ForegroundColor Yellow
    sc.exe start pgagent-pg18
    
    Start-Sleep -Seconds 5
    
    $service = Get-Service pgagent-pg18
    if ($service.Status -eq "Running") {
        Write-Host "✓ pgAgent is running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Verification:" -ForegroundColor Cyan
        Write-Host "  - Service Status: Running" -ForegroundColor Green
        Write-Host "  - Connection: developer_skills database" -ForegroundColor Green
        Write-Host "  - Jobs will execute every 5 minutes" -ForegroundColor Green
        Write-Host ""
        Write-Host "Wait 5 minutes, then check in pgAdmin 4:" -ForegroundColor Yellow
        Write-Host "  Right-click job > Properties > Statistics tab" -ForegroundColor White
    } else {
        Write-Host "Service Status: $($service.Status)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "If still not running, check:" -ForegroundColor Yellow
        Write-Host "  1. PostgreSQL service is running" -ForegroundColor White
        Write-Host "  2. Connection string is correct" -ForegroundColor White
        Write-Host "  3. Database 'developer_skills' exists" -ForegroundColor White
    }
} else {
    Write-Host "✗ Failed to configure service" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
