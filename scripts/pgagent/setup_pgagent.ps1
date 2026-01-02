# Configure pgAgent Service - Run as Administrator
# This connects pgAgent to your developer_skills database

Write-Host "Configuring pgAgent service..." -ForegroundColor Cyan
Write-Host ""

# Stop the service
Write-Host "Stopping pgAgent service..." -ForegroundColor Yellow
Stop-Service pgagent-pg18 -ErrorAction SilentlyContinue

# Configure the service with connection string
$connectionString = "hostaddr=127.0.0.1 port=5432 dbname=developer_skills user=postgres password=1234"
$binPath = "`"E:\PostgreSQL\18\bin\pgagent.exe`" RUN pgagent-pg18 $connectionString"

Write-Host "Setting connection string..." -ForegroundColor Yellow
sc.exe config pgagent-pg18 binPath= $binPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Service configured successfully" -ForegroundColor Green
    Write-Host ""
    
    # Start the service
    Write-Host "Starting pgAgent service..." -ForegroundColor Yellow
    Start-Service pgagent-pg18
    
    if ($?) {
        Write-Host "✓ pgAgent is now running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "The job will run automatically every 5 minutes." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Check status in pgAdmin 4:" -ForegroundColor Yellow
        Write-Host "  - Expand developer_skills > pgAgent Jobs" -ForegroundColor White
        Write-Host "  - Right-click your job > Properties > Statistics" -ForegroundColor White
    } else {
        Write-Host "✗ Failed to start service" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Failed to configure service" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
