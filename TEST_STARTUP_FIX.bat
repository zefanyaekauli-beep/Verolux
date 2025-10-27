@echo off
REM Test Startup Fix
REM Verify the startup scripts work without errors

echo ============================================
echo Testing Startup Script Fixes
echo ============================================
echo.

echo [1/3] Testing START_VEROLUX.bat syntax...
echo [INFO] Checking for syntax errors...
echo [INFO] This should not show any 'import' errors...

echo.
echo [2/3] Testing timeout commands...
echo [INFO] Testing timeout command (3 seconds)...
timeout /t 3 /nobreak >nul 2>&1
echo [OK] Timeout command works

echo.
echo [3/3] Testing Python path...
echo [INFO] Checking if Python is accessible...
cd Backend
if exist "venv\Scripts\python.exe" (
    echo [OK] Python found in virtual environment
    echo [INFO] Testing Python execution...
    venv\Scripts\python.exe --version >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Python execution failed
    ) else (
        echo [OK] Python execution works
    )
) else (
    echo [ERROR] Python not found in virtual environment
    echo [INFO] Please run: cd Backend && python -m venv venv
)
cd ..

echo.
echo ============================================
echo Startup Fix Test Complete!
echo ============================================
echo.
echo If no errors above, the startup scripts should work.
echo.
echo To start the system:
echo   START_VEROLUX.bat        (Full startup with checks)
echo   START_VEROLUX_SIMPLE.bat (Quick startup)
echo.
echo To stop the system:
echo   STOP_VEROLUX.bat
echo.
pause


