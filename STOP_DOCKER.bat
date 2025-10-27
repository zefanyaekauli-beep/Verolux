@echo off
REM Verolux Enterprise - Stop Docker Services

echo ============================================
echo Verolux Enterprise - Stopping Docker
echo ============================================
echo.

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml not found
    echo Please run this script from the Verolux root directory
    pause
    exit /b 1
)

echo Step 1: Stopping all services...
docker-compose down

if errorlevel 1 (
    echo [ERROR] Failed to stop services!
    pause
    exit /b 1
)

echo.
echo [OK] All services stopped
echo.

set /p CLEANUP="Remove volumes and data? (Y/N): "
if /i "%CLEANUP%"=="Y" (
    echo.
    echo Removing volumes and data...
    docker-compose down -v
    echo [OK] Volumes removed
)

echo.
echo ============================================
echo Services Stopped Successfully
echo ============================================
echo.
echo To start again, run: START_DOCKER.bat
echo.
pause












