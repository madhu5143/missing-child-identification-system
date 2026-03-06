@echo off
echo ==========================================
echo   Missing Child Identification System
echo ==========================================
echo.

:: Get the directory where this script is located
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

:: Free port 8000 and 5173 if already in use (e.g. previous run)
echo Freeing ports 8000 and 5173 if in use...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }; Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>nul
if errorlevel 1 (
  echo Using fallback to free ports...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%a 2>nul
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%a 2>nul
)
ping -n 3 127.0.0.1 >nul 2>nul
echo Ports cleared.
echo.

echo [1/2] Launching Backend Server...
REM Without --reload to avoid Windows multiprocessing PermissionError in some environments
start "Backend Server (FastAPI)" cmd /k "cd /d "%BASE_DIR%backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo [2/2] Launching Frontend Server...
start "Frontend Server (Vite)" cmd /k "cd /d "%BASE_DIR%frontend" && npm run dev"

echo.
echo ==========================================
echo Servers are launching in separate windows.
echo - Frontend: http://localhost:5173
echo - Backend:  http://localhost:8000
echo ==========================================
echo.
pause
