@echo off
setlocal
cd /d "%~dp0"
title ORBITA Setup and Launcher

echo ==========================================
echo          ORBITA - FIRST TIME SETUP
echo ==========================================
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  echo Please install Python and select "Add Python to PATH".
  pause
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo Creating the virtual environment...
  python -m venv venv
  if errorlevel 1 goto error
)

echo.
echo Installing required Python packages...
"venv\Scripts\python.exe" -m pip install --upgrade pip
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Starting ORBITA API...
start "ORBITA API" cmd /k ""%~dp0venv\Scripts\python.exe" -m uvicorn backend.main:app --reload"

echo Waiting a few seconds for the API...
timeout /t 4 /nobreak >nul

echo Starting ORBITA website...
start "ORBITA Website" cmd /k "cd /d "%~dp0frontend" && "%~dp0venv\Scripts\python.exe" -m http.server 5500"

echo.
echo ORBITA is starting.
echo Website: http://127.0.0.1:5500
echo API docs: http://127.0.0.1:8000/docs
echo Keep both black terminal windows open while using ORBITA.
timeout /t 3 >nul
start "" "http://127.0.0.1:5500"
exit /b 0

:error
echo.
echo Something went wrong during setup.
echo Take a screenshot of this window and send it for help.
pause
exit /b 1
