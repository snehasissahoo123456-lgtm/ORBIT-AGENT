@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ENABLE_ORBIT_STARTUP.ps1"
if errorlevel 1 (
  echo Could not configure ORBIT startup. No system-wide setting was changed.
  pause
  exit /b 1
)
echo Startup is enabled for this Windows user at sign-in.
pause
