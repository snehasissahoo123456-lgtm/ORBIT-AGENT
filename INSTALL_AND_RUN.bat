@echo off
setlocal
cd /d "%~dp0"
echo =====================================
echo ORBIT - Founder Agent
echo =====================================
where py >nul 2>nul
if errorlevel 1 (echo Python launcher not found. Install Python 3.12+ and enable Add to PATH.& pause & exit /b 1)
py -3 -m venv .venv
if errorlevel 1 (echo Could not create virtual environment.& pause & exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed.& pause & exit /b 1)
python -m playwright install chromium
if errorlevel 1 echo Browser automation is optional; Chromium installation did not finish.
if not exist .env copy .env.example .env >nul
if not exist workspace mkdir workspace
if not exist data mkdir data
echo.
echo ORBIT is ready to launch locally at http://127.0.0.1:8000
echo Keep this window open while ORBIT is working.
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
