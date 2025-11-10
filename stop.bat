@echo off
REM Verox - Stop Script
REM Stops all Verox processes

echo ============================================
echo   Stopping Verox System
echo ============================================
echo.

echo Stopping Python processes (Backend)...
taskkill /f /im python.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] No Python processes found
) else (
    echo [OK] Python processes stopped
)

echo.
echo Stopping Node.js processes (Frontend)...
taskkill /f /im node.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] No Node.js processes found
) else (
    echo [OK] Node.js processes stopped
)

echo.
echo ============================================
echo   System Stopped
echo ============================================
echo.
timeout /t 2 /nobreak >nul






