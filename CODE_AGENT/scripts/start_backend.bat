@echo off
echo ========================================
echo Starting Code Intelligence Agent Backend
echo ========================================
echo.
echo NOTE: First startup will take 10-30 seconds while loading the model.
echo The model download (if needed) happens automatically.
echo.
echo Keep this window open!
echo.
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
