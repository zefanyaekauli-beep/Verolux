@echo off
REM Verox - Simple Startup Script
REM Starts Backend (advanced_body_checking.py) and Frontend (React)

echo ============================================
echo   Verox Advanced Body Checking System
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

REM Kill existing processes
echo [1/4] Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Processes stopped
echo.

REM Check for required files
echo [2/4] Checking required files...
if not exist "Backend\advanced_body_checking.py" (
    echo [ERROR] Backend file not found: Backend\advanced_body_checking.py
    pause
    exit /b 1
)
if not exist "weight.pt" (
    echo [WARNING] Model file not found: weight.pt
    echo System may not work without the model file.
)
if not exist "videoplayback.mp4" (
    echo [WARNING] Video file not found: videoplayback.mp4
    echo System will work with webcam only.
)
echo [OK] Required files checked
echo.

REM Start Backend
echo [3/4] Starting Backend Server (Port 8002)...
start "Verox Backend" cmd /k "cd /d %cd%\Backend && python advanced_body_checking.py"
echo [OK] Backend starting...
timeout /t 5 /nobreak >nul
echo.

REM Start Frontend
echo [4/4] Starting Frontend Server (Port 5173)...
start "Verox Frontend" cmd /k "cd /d %cd%\Frontend && npm run dev"
echo [OK] Frontend starting...
timeout /t 5 /nobreak >nul
echo.

echo ============================================
echo   System Started Successfully!
echo ============================================
echo.
echo Access URLs:
echo   Local:    http://localhost:5173
echo   Network:  http://192.168.0.102:5173
echo.
echo Tip: In the app, open the "Inference" page to view Simple/Advanced modes.
echo.
echo Login Credentials:
echo   Admin:  username=admin,  password=admin
echo   Viewer: username=viewer, password=viewer
echo.
echo Two windows are open:
echo   1. Backend  (AI Processing + WebSocket)
echo   2. Frontend (Web Interface)
echo.
echo To stop: Close both windows or run stop.bat
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.




REM Starts Backend (advanced_body_checking.py) and Frontend (React)

echo ============================================
echo   Verox Advanced Body Checking System
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

REM Kill existing processes
echo [1/4] Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Processes stopped
echo.

REM Check for required files
echo [2/4] Checking required files...
if not exist "Backend\advanced_body_checking.py" (
    echo [ERROR] Backend file not found: Backend\advanced_body_checking.py
    pause
    exit /b 1
)
if not exist "weight.pt" (
    echo [WARNING] Model file not found: weight.pt
    echo System may not work without the model file.
)
if not exist "videoplayback.mp4" (
    echo [WARNING] Video file not found: videoplayback.mp4
    echo System will work with webcam only.
)
echo [OK] Required files checked
echo.

REM Start Backend
echo [3/4] Starting Backend Server (Port 8002)...
start "Verox Backend" cmd /k "cd /d %cd%\Backend && python advanced_body_checking.py"
echo [OK] Backend starting...
timeout /t 5 /nobreak >nul
echo.

REM Start Frontend
echo [4/4] Starting Frontend Server (Port 5173)...
start "Verox Frontend" cmd /k "cd /d %cd%\Frontend && npm run dev"
echo [OK] Frontend starting...
timeout /t 5 /nobreak >nul
echo.

echo ============================================
echo   System Started Successfully!
echo ============================================
echo.
echo Access URLs:
echo   Local:    http://localhost:5173
echo   Network:  http://192.168.0.102:5173
echo.
echo Tip: In the app, open the "Inference" page to view Simple/Advanced modes.
echo.
echo Login Credentials:
echo   Admin:  username=admin,  password=admin
echo   Viewer: username=viewer, password=viewer
echo.
echo Two windows are open:
echo   1. Backend  (AI Processing + WebSocket)
echo   2. Frontend (Web Interface)
echo.
echo To stop: Close both windows or run stop.bat
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.



