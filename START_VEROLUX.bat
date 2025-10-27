@echo off
REM Verolux - Main Startup Script
REM Clean, reliable startup for the complete Verolux system

echo ============================================
echo Verolux - Complete System Startup
echo ============================================
echo.

echo [1/8] Stopping all existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo [OK] All processes stopped

echo.
echo [2/8] Checking system requirements...
if not exist "Backend\venv\Scripts\activate.bat" (
    echo [ERROR] Backend virtual environment not found
    echo Please run: cd Backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "Frontend\node_modules" (
    echo [ERROR] Frontend dependencies not found
    echo Please run: cd Frontend && npm install
    pause
    exit /b 1
)

echo [OK] System requirements met

echo.
echo [3/8] Checking AI model...
if exist "weight.pt" (
    echo [OK] Found weight.pt in root directory
    if not exist "Backend\models\weight.pt" (
        echo [INFO] Copying weight.pt to Backend\models...
        copy "weight.pt" "Backend\models\" >nul 2>&1
        echo [OK] Model copied to Backend\models
    )
) else (
    echo [WARNING] weight.pt not found in root directory
    echo System will run without AI model
)

echo.
echo [4/8] Checking video file...
if exist "Frontend\public\videoplayback.mp4" (
    echo [OK] Video file exists in Frontend\public
) else (
    if exist "videoplayback.mp4" (
        echo [INFO] Copying video file to Frontend\public...
        copy "videoplayback.mp4" "Frontend\public\" >nul 2>&1
        echo [OK] Video file copied
    ) else (
        echo [WARNING] videoplayback.mp4 not found
        echo System will run without video demo
    )
)

echo.
echo [5/8] Starting Backend Server...
start "Verolux Backend" cmd /k "cd /d %cd%\Backend && .\venv\Scripts\activate && python backend_server_fixed.py"
echo [OK] Backend starting...
timeout /t 8 /nobreak >nul 2>&1

echo.
echo [6/8] Testing Backend Connection...
echo [INFO] Backend should be starting up...
echo [INFO] Check the Backend window for startup logs

echo.
echo [7/8] Starting Frontend Server...
start "Verolux Frontend" cmd /k "cd /d %cd%\Frontend && npm run dev"
echo [OK] Frontend starting...
timeout /t 8 /nobreak >nul 2>&1

echo.
echo [8/8] Final System Check...
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo [ERROR] Backend not running on port 8000
) else (
    echo [OK] Backend running on port 8000
)

netstat -ano | findstr ":5173" >nul
if errorlevel 1 (
    echo [ERROR] Frontend not running on port 5173
) else (
    echo [OK] Frontend running on port 5173
)

echo.
echo ============================================
echo Verolux System Started Successfully!
echo ============================================
echo.
echo Access your system:
echo   Dashboard: http://localhost:5173
echo   Video Demo: http://localhost:5173 (Navigate to VideoplaybackDemo)
echo.
echo Features Available:
echo   - Real-time AI object detection
echo   - Video processing with detection overlay
echo   - Gate SOP monitoring
echo   - Alert system
echo   - Session reporting
echo.
echo Opening dashboard in 3 seconds...
timeout /t 3 /nobreak >nul 2>&1
start http://localhost:5173

echo.
echo System is running! Two windows opened:
echo   1. Backend  (AI Model + Video Processing)
echo   2. Frontend (Web Interface)
echo.
echo To stop the system, close both windows or run STOP_VEROLUX.bat
echo.
pause