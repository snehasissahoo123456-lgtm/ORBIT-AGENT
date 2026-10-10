@echo off
setlocal
cd /d "%~dp0"
title ORBIT Repair and Reinstall

echo ============================================
echo ORBIT - Safe Environment Repair
echo ============================================
echo This rebuilds only the Python virtual environment.
echo It does NOT delete data, workspace files, checkpoints, or .env.
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher not found.
  echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
  echo Enable the Python Launcher during installation, then retry.
  pause
  exit /b 1
)

py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 (
  echo ERROR: Python 3.11 or newer is required.
  pause
  exit /b 1
)

if exist ".venv" (
  echo Removing the existing .venv environment only...
  rmdir /s /q ".venv"
  if exist ".venv" (
    echo ERROR: Could not remove .venv. Close Python/ORBIT terminals and retry.
    pause
    exit /b 1
  )
)

echo Creating a clean virtual environment...
py -3 -m venv .venv
if errorlevel 1 (
  echo ERROR: Could not create .venv.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo ERROR: pip upgrade failed. Check internet access and retry.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Dependency installation failed. Keep this window open and save the error.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m playwright install chromium
if errorlevel 1 (
  echo WARNING: Chromium installation failed. ORBIT may start, but browser page reading may not work.
)

if not exist ".env" (
  if exist ".env.example" (
    copy ".env.example" ".env" >nul
    if errorlevel 1 echo WARNING: Could not create .env from .env.example.
  ) else (
    echo WARNING: .env.example is missing. Configuration may need manual setup.
  )
)
if not exist "workspace" mkdir "workspace"
if not exist "data" mkdir "data"

echo.
echo Running Python syntax checks...
".venv\Scripts\python.exe" -m compileall -q .
if errorlevel 1 (
  echo ERROR: Python syntax check failed. ORBIT was not launched.
  pause
  exit /b 1
)

echo.
echo Starting ORBIT. Keep this window open.
echo Dashboard: http://127.0.0.1:8000
echo If chat/coding reports Ollama unavailable, install Ollama and run:
echo ollama pull qwen2.5:7b
echo Do not expose ORBIT directly to the internet.
".venv\Scripts\python.exe" -c "from config import settings; import uvicorn; uvicorn.run('main:app', host=settings.orbit_host, port=settings.orbit_port)"
if errorlevel 1 (
  echo.
  echo ORBIT stopped with an error. Copy the full traceback above for diagnosis.
  echo Check logs\orbit.log if it exists.
)
pause
