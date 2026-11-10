@echo off
REM ============================================================
REM  One-click startup: Ollama + Backend + ngrok
REM  Just double-click this file whenever you want to run the project.
REM  (Edit run-ngrok.bat once if you ever change your ngrok domain.)
REM ============================================================

echo Starting Ollama...
start "Ollama" cmd /k "ollama serve"

timeout /t 3 /nobreak >nul

echo Starting Backend (FastAPI)...
start "Backend" cmd /k "%~dp0run-backend.bat"

timeout /t 5 /nobreak >nul

echo Starting ngrok tunnel...
start "ngrok" cmd /k "%~dp0run-ngrok.bat"

echo.
echo ============================================================
echo All three services are starting in separate windows:
echo   1. Ollama   - the local LLM (ignore "port already in use"
echo                 if Ollama is already running in the background)
echo   2. Backend  - FastAPI on http://localhost:8000
echo   3. ngrok    - public tunnel forwarding to it
echo.
echo Once the Backend window shows "Uvicorn running on ..." and the
echo ngrok window shows "Forwarding ...", open your Vercel URL.
echo ============================================================
pause