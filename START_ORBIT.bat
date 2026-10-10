@echo off
setlocal
cd /d "%~dp0"
title ORBIT Founder Agent
if not exist ".venv\Scripts\python.exe" (
  echo ORBIT is not installed yet. Run INSTALL_AND_RUN.bat once first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import uvicorn, fastapi, pydantic_settings" >nul 2>nul
if errorlevel 1 (
  echo ORBIT dependencies are incomplete. Run INSTALL_AND_RUN.bat to repair the environment.
  pause
  exit /b 1
)
if not exist ".env" copy ".env.example" ".env" >nul
if not exist "workspace" mkdir "workspace"
if not exist "data" mkdir "data"
".venv\Scripts\python.exe" -c "from config import settings; import uvicorn; uvicorn.run('main:app', host=settings.orbit_host, port=settings.orbit_port)"
if errorlevel 1 echo ORBIT stopped unexpectedly. Check logs\orbit.log and the console output.
pause
