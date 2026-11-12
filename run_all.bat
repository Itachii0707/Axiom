@echo off
title Axiom Enterprise RAG - Launcher
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"

echo ============================================================
echo   AXIOM ENTERPRISE RAG PLATFORM
echo ============================================================
echo.

echo [1/4] Checking PostgreSQL...
netstat -ano | findstr 5432 >nul
if %errorlevel% neq 0 (
    echo Starting PostgreSQL 16 server in background...
    start /b "" "d:\tools\pgsql\bin\postgres.exe" -D "d:\tools\pgsql\data"
    timeout /t 3 /nobreak >nul
) else (
    echo PostgreSQL is already running on port 5432.
)

echo [2/4] Checking Ollama...
netstat -ano | findstr 11434 >nul
if %errorlevel% neq 0 (
    echo Starting Ollama server in background...
    start /b "" "d:\tools\ollama\ollama.exe" serve
    timeout /t 3 /nobreak >nul
) else (
    echo Ollama is already running on port 11434.
)

echo [3/4] Starting Ingestion Worker in background window...
start "Axiom - Ingestion Worker" cmd /c ".\venv\Scripts\python.exe ingestion\worker.py"

echo [4/4] Starting FastAPI Web Server...
echo Open your browser at: http://localhost:8000
echo Admin Console at:     http://localhost:8000/admin (admin / ChangeMe!123)
echo.

start "" "http://localhost:8000"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

