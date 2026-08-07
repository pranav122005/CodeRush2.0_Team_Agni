# NEXUS x402 - Start All Services
Write-Host "Starting Netflix x402 + NEXUS Mesh..." -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start NEXUS Mesh (port 8001)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\nexus-mesh'; ..\backend\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" -WindowStyle Normal

# Start Backend (port 8000)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; .\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "All services launched!" -ForegroundColor Green
Write-Host "  Frontend  -> http://localhost:5173" -ForegroundColor Yellow
Write-Host "  Backend   -> http://localhost:8000" -ForegroundColor Yellow
Write-Host "  NEXUS Mesh-> http://localhost:8001" -ForegroundColor Yellow
