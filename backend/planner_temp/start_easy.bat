@echo off
echo Starting Interview Helper Memory Version...
echo.

echo Step 1: Starting Backend...
cd backend
start "Backend" cmd /k "python app_memory.py"

echo Step 2: Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo Step 3: Starting Frontend...
cd ..\frontend
start "Frontend" cmd /k "npm run dev"

echo.
echo Services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window (services will keep running)
pause 