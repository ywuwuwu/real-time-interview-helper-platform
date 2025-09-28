@echo off
chcp 65001 > nul
echo ========================================
echo Interview Helper - Memory Version
echo ========================================
echo.

echo Starting backend service...
start "Backend" cmd /k "cd backend && python app_memory.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting frontend service...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Services started successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Note: Closing this window will not stop the services
echo.
pause 