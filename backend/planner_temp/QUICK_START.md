# Quick Start Guide - Interview Helper Memory Version

## Problem Solved
The original version had database issues causing 404 errors. This memory-based version eliminates database dependencies.

## Quick Start

### Method 1: Simple Batch File (Recommended)
```cmd
start_simple.bat
```

### Method 2: Manual Start
```cmd
# Terminal 1 - Backend
cd backend
python app_memory.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### Method 3: PowerShell
```powershell
.\start_memory.ps1
```

## Test the Setup

Run the test script to verify everything works:
```cmd
python test_simple.py
```

## Access URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features Working

✅ Interview Planner (5-step process)
✅ Job Description Upload
✅ Resume Upload
✅ Skill Matching Analysis
✅ Personalized Recommendations
✅ Progress Tracking
✅ Memory Storage (no database needed)

## Troubleshooting

### If you see encoding issues:
- Use the English version scripts
- Avoid Chinese characters in terminal

### If backend won't start:
- Check if port 8000 is free
- Make sure you're running `app_memory.py` not `app.py`

### If frontend won't start:
- Make sure Node.js is installed
- Run `npm install` in frontend directory first

## What's Different

- **No Database**: Uses memory storage instead of SQLite
- **Faster Startup**: No database initialization
- **Simpler Setup**: Just Python and Node.js required
- **Same Features**: All Interview Planner functionality works

## Next Steps

1. Open http://localhost:5173 in your browser
2. Click "Interview Planner" button
3. Follow the 5-step process
4. Test all features

The memory version should work without any database issues! 