@echo off
echo Cleaning up and starting Interview Helper...
echo.

echo Step 1: Checking for processes on port 8000...
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo Found processes on port 8000, killing them...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /f /pid %%a 2>nul
    )
) else (
    echo Port 8000 is free.
)

echo Step 2: Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo Step 3: Starting Backend...
cd backend
start "Backend" cmd /k "python app_memory.py"

echo Step 4: Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo Step 5: Starting Frontend...
cd ..\frontend
start "Frontend" cmd /k "npm run dev"

echo.
echo Services should be running now!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause 