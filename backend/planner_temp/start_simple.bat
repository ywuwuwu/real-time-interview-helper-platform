@echo off
echo Starting Interview Helper Memory Version...
echo.

echo Starting Backend...
cd backend
start "Backend" cmd /k "python app_memory.py"

echo Starting Frontend...
cd ..\frontend
start "Frontend" cmd /k "npm run dev"

echo.
echo Services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause 