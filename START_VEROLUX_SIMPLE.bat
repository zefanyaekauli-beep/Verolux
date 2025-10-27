@echo off
REM Verolux - Simple Startup Script
REM Quick startup without extensive checks

echo ============================================
echo Verolux - Simple Startup
echo ============================================
echo.

echo [1/4] Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo [OK] Processes stopped

echo.
echo [2/4] Starting Backend...
start "Verolux Backend" cmd /k "cd /d %cd%\Backend && .\venv\Scripts\activate && python backend_server_fixed.py"
echo [OK] Backend starting...
timeout /t 5 /nobreak >nul 2>&1

echo.
echo [3/4] Starting Frontend...
start "Verolux Frontend" cmd /k "cd /d %cd%\Frontend && npm run dev"
echo [OK] Frontend starting...
timeout /t 5 /nobreak >nul 2>&1

echo.
echo [4/4] Opening Dashboard...
timeout /t 3 /nobreak >nul 2>&1
start http://localhost:5173

echo.
echo ============================================
echo Verolux Started!
echo ============================================
echo.
echo Access: http://localhost:5173
echo.
echo Two windows opened:
echo   1. Backend  (AI + Video)
echo   2. Frontend (Web Interface)
echo.
echo To stop: Close both windows or run STOP_VEROLUX.bat
echo.
pause


