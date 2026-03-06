@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Building Unified Web Application
echo ==========================================
echo.

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo [1/3] Building Frontend...
cd frontend
call npm install --no-fund --no-audit
call npm run build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Frontend build failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Preparing Static Files for Backend...
cd ..
if exist "backend\static" (
    rmdir /s /q "backend\static"
)
mkdir "backend\static"
xcopy /e /i /y "frontend\dist\*" "backend\static\"

echo.
echo [3/3] Starting Unified Server...
echo The application will be available at: http://localhost:8000
echo.
cd backend
python -m uvicorn app.main:app --host :: --port 8000

pause


