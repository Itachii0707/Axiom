# Axiom Enterprise RAG - 1-Click PowerShell Launcher
Set-Location -Path $PSScriptRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   AXIOM ENTERPRISE AGENTIC RAG PLATFORM - 1-CLICK RUN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. PostgreSQL Check
Write-Host "[1/4] Checking PostgreSQL 16..." -ForegroundColor Yellow
$pgRunning = Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue
if (-not $pgRunning) {
    Write-Host "Starting PostgreSQL in background..." -ForegroundColor Green
    Start-Process -FilePath "d:\tools\pgsql\bin\postgres.exe" -ArgumentList "-D", "d:\tools\pgsql\data" -WindowStyle Hidden
    Start-Sleep -Seconds 3
} else {
    Write-Host "PostgreSQL is already active on port 5432." -ForegroundColor Green
}

# 2. Ollama Check
Write-Host "[2/4] Checking Ollama AI Runtime..." -ForegroundColor Yellow
$ollamaRunning = Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue
if (-not $ollamaRunning) {
    Write-Host "Starting Ollama server in background..." -ForegroundColor Green
    Start-Process -FilePath "d:\tools\ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
} else {
    Write-Host "Ollama is already active on port 11434." -ForegroundColor Green
}

# 3. Worker Process
Write-Host "[3/4] Launching Ingestion Worker..." -ForegroundColor Yellow
$env:PYTHONPATH = $PSScriptRoot
Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "ingestion\worker.py" -WindowStyle Minimized

# 4. Web Server
Write-Host "[4/4] Launching FastAPI Web Application..." -ForegroundColor Yellow
Write-Host "Opening browser at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Admin Portal: http://localhost:8000/admin (admin / ChangeMe!123)" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:8000"
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

