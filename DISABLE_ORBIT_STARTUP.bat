@echo off
setlocal
set "ORBIT_STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ORBIT Agent.lnk"
if exist "%ORBIT_STARTUP%" (
  del "%ORBIT_STARTUP%"
  echo ORBIT automatic startup has been disabled.
) else (
  echo No ORBIT startup shortcut was found.
)
pause
