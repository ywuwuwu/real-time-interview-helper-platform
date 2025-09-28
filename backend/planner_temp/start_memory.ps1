# Interview Helper - Memory-based Version Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Interview Helper - Memory Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting backend service..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd 'C:\Users\18246\OneDrive\VSCode\xiaocong\code\beebeeai\Track-B\interview-helper\backend'; python app_memory.py" -WindowStyle Normal

Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting frontend service..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd 'C:\Users\18246\OneDrive\VSCode\xiaocong\code\beebeeai\Track-B\interview-helper\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "Services started successfully!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Blue
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Note: Closing this window will not stop the services" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press any key to exit" 