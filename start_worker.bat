@echo off
REM ============================================================
REM  Ingestion worker for Axiom.
REM  Parses -> chunks -> embeds -> stores each uploaded document.
REM
REM  Keep this window open while you use the admin panel. If it
REM  is closed, uploads sit in "processing" forever because
REM  nothing drains the ingest queue.
REM
REM  Run it ALONGSIDE the API server (uvicorn), not instead of it.
REM ============================================================
title Axiom - Ingestion Worker

REM cd to this file's own folder so relative data\ paths resolve.
cd /d "%~dp0"

echo Starting ingestion worker...  (press Ctrl+C to stop)
echo.

REM Use the virtual environment Python interpreter
.\venv\Scripts\python.exe ingestion\worker.py

echo.
echo Worker stopped. Review any error message above.
pause
