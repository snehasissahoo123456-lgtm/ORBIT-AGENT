@echo off
setlocal
cd /d "%~dp0"
title ORBIT Founder Agent
echo ==========================================
echo ORBIT - Founder-Controlled AI Agent
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
 echo Python launcher not found. Install Python 3.11 or newer from python.org.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 py -3 -m venv .venv
 if errorlevel 1 (echo Virtual environment creation failed.& pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (echo pip upgrade failed.& pause & exit /b 1)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed. Check internet and Python.& pause & exit /b 1)
if not exist ".env" copy ".env.example" ".env" >nul
if not exist "workspace" mkdir "workspace"
echo.
echo ORBIT will be available at http://127.0.0.1:8000
echo Keep this terminal open. Press Ctrl+C to stop the server.
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
