# Code Intelligence Agent - Start All Services
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Code Intelligence Agent" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend
Write-Host "[1/2] Starting Backend Server..." -ForegroundColor Yellow
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Normal

# Wait for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend Server..." -ForegroundColor Yellow
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Both servers are running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers..." -ForegroundColor Yellow

# Wait for user to press Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Red
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "All servers stopped." -ForegroundColor Red
}
