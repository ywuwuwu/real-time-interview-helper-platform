# Manual Start Guide - Interview Helper Memory Version

## Problem Analysis
The issues you're experiencing are:
1. **Port 8000 is already in use** - Another service is running on port 8000
2. **PowerShell syntax error** - `&&` is not valid in PowerShell
3. **Wrong directory** - Need to be in the correct directory

## Solution Steps

### Step 1: Kill Existing Processes
Open Command Prompt as Administrator and run:
```cmd
taskkill /f /im python.exe
```

### Step 2: Check Port 8000
```cmd
netstat -ano | findstr :8000
```
If you see any processes, kill them:
```cmd
taskkill /f /pid [PID_NUMBER]
```

### Step 3: Navigate to Correct Directory
```cmd
cd C:\Users\18246\OneDrive\VSCode\xiaocong\code\beebeeai\Track-B\interview-helper
```

### Step 4: Start Backend (Terminal 1)
```cmd
cd backend
python app_memory.py
```

### Step 5: Start Frontend (Terminal 2)
Open a new Command Prompt:
```cmd
cd C:\Users\18246\OneDrive\VSCode\xiaocong\code\beebeeai\Track-B\interview-helper\frontend
npm run dev
```

## Alternative: Use Batch Files

### Option 1: Clean and Start
```cmd
clean_and_start.bat
```

### Option 2: Simple Start
```cmd
start_easy.bat
```

## Verify It's Working

1. **Check Backend**: Open http://localhost:8000/api/health
2. **Check Frontend**: Open http://localhost:5173
3. **Test API**: Run `python test_simple.py`

## Common Issues and Solutions

### Issue: "Port already in use"
**Solution**: 
```cmd
netstat -ano | findstr :8000
taskkill /f /pid [PID_NUMBER]
```

### Issue: "File not found"
**Solution**: Make sure you're in the correct directory:
```cmd
cd C:\Users\18246\OneDrive\VSCode\xiaocong\code\beebeeai\Track-B\interview-helper
```

### Issue: PowerShell syntax error
**Solution**: Use Command Prompt (cmd) instead of PowerShell, or use the batch files.

### Issue: Frontend won't start
**Solution**: 
```cmd
cd frontend
npm install
npm run dev
```

## Quick Commands

```cmd
# Kill all Python processes
taskkill /f /im python.exe

# Navigate to project
cd C:\Users\18246\OneDrive\VSCode\xiaocong\code\beebeeai\Track-B\interview-helper

# Start backend
cd backend && python app_memory.py

# Start frontend (in new terminal)
cd frontend && npm run dev
```

## Expected Output

**Backend should show:**
```
>>> This is the actual app_memory.py being loaded
>>> Memory storage initialized
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Frontend should show:**
```
VITE v4.x.x ready in xxx ms
Local: http://localhost:5173/
```

## Test URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health 