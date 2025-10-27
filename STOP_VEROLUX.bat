@echo off
REM Verolux - Stop All Processes
REM Clean shutdown of the Verolux system

echo ============================================
echo Verolux - Stopping All Processes
echo ============================================
echo.

echo [1/3] Stopping Python processes...
taskkill /f /im python.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] No Python processes found
) else (
    echo [OK] Python processes stopped
)

echo.
echo [2/3] Stopping Node.js processes...
taskkill /f /im node.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] No Node.js processes found
) else (
    echo [OK] Node.js processes stopped
)

echo.
echo [3/3] Checking ports...
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo [OK] Port 8000 is free
) else (
    echo [WARNING] Port 8000 still in use
)

netstat -ano | findstr ":5173" >nul
if errorlevel 1 (
    echo [OK] Port 5173 is free
) else (
    echo [WARNING] Port 5173 still in use
)

echo.
echo ============================================
echo Verolux System Stopped!
echo ============================================
echo.
echo All processes have been stopped.
echo To restart, run START_VEROLUX.bat
echo.
pause