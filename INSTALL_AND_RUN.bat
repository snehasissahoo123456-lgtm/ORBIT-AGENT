@echo off
setlocal
cd /d "%~dp0"
echo =====================================
echo ORBIT - Founder Agent
echo =====================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.11 or newer and enable the Python Launcher.
  pause
  exit /b 1
)
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 (
  echo Python 3.11 or newer is required.
  pause
  exit /b 1
)
if not exist .venv (
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Could not create the virtual environment.
    pause
    exit /b 1
  )
)
call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo Could not activate the virtual environment.
  pause
  exit /b 1
)
python -m pip install --upgrade pip
if errorlevel 1 (
  echo pip upgrade failed. Check internet access and try again.
  pause
  exit /b 1
)
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Fix the displayed error before retrying.
  pause
  exit /b 1
)
python -m playwright install chromium
if errorlevel 1 echo WARNING: Chromium installation failed. Browser reading may not work; other features can still start.
if not exist .env copy .env.example .env >nul
if not exist workspace mkdir workspace
if not exist data mkdir data
echo.
echo ORBIT will start on the configured local address. Keep this window open.
echo If chat or coding says Ollama is unavailable, install Ollama and run: ollama pull qwen2.5:7b
echo Do not expose ORBIT directly to the internet.
python -c "from config import settings; import uvicorn; uvicorn.run('main:app', host=settings.orbit_host, port=settings.orbit_port)"
if errorlevel 1 (
  echo ORBIT stopped with an error. Read the traceback above and logs\orbit.log.
)
pause
