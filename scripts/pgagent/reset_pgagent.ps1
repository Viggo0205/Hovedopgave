# Reset pgAgent Service
# Run this as Administrator

Write-Host "Stopping pgAgent service..." -ForegroundColor Yellow
Stop-Service pgagent-pg18 -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Killing any stuck pgAgent processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like '*pgagent*'} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Reconfiguring service account to LocalSystem..." -ForegroundColor Yellow
sc.exe config pgagent-pg18 obj= "LocalSystem" password= ""
Start-Sleep -Seconds 1

Write-Host "Starting service..." -ForegroundColor Yellow
sc.exe start pgagent-pg18
Start-Sleep -Seconds 5

Write-Host "`nService Status:" -ForegroundColor Green
Get-Service pgagent-pg18 | Format-List Name, Status, StartType

Write-Host "`nIf status is Running, wait 5 minutes then check job execution with:" -ForegroundColor Cyan
Write-Host '$env:PGPASSWORD = "1234"; & "E:\PostgreSQL\18\bin\psql.exe" -U postgres -d developer_skills -c "SELECT jobname, jlgstatus, jlgstart FROM pgagent.pga_joblog ORDER BY jlgstart DESC LIMIT 3;"' -ForegroundColor White
