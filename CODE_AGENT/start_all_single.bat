@echo off
echo ========================================
echo Starting Code Intelligence Agent
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C to stop all servers
echo ========================================
echo.

REM Run both in parallel using start /B (background in same window)
start /B cmd /c "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
start /B cmd /c "cd frontend && npm run dev"

REM Keep the window open
pause
