@echo off
REM Verolux Enterprise - Docker Start Script
REM Starts all services using Docker Compose

echo ============================================
echo Verolux Enterprise - Docker Deployment
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml not found
    echo Please run this script from the Verolux root directory
    pause
    exit /b 1
)

echo Step 1: Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found!
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)
echo [OK] Docker found

echo.
echo Step 2: Checking Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose not found!
    echo Please install Docker Compose
    pause
    exit /b 1
)
echo [OK] Docker Compose found

echo.
echo Step 3: Checking if Docker is running...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo [OK] Docker is running

echo.
echo Step 4: Stopping any existing containers...
docker-compose down 2>nul
echo [OK] Cleaned up existing containers

echo.
echo Step 5: Building Docker images...
echo [INFO] This may take 5-10 minutes on first run...
docker-compose build

if errorlevel 1 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)
echo [OK] Images built successfully

echo.
echo Step 6: Starting all services...
docker-compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start services!
    pause
    exit /b 1
)
echo [OK] Services started

echo.
echo Step 7: Waiting for services to initialize...
echo [INFO] Please wait 15 seconds...
timeout /t 15 /nobreak

echo.
echo Step 8: Checking service health...
docker-compose ps

echo.
echo ============================================
echo [OK] Verolux System Started!
echo ============================================
echo.
echo Services running:
echo   Backend     - http://localhost:8000
echo   Analytics   - http://localhost:8002
echo   Reporting   - http://localhost:8001
echo   Semantic    - http://localhost:8003
echo   Incident    - http://localhost:8004
echo   Config      - http://localhost:8005
echo   Frontend    - http://localhost:3000
echo.
echo ============================================
echo Access your system:
echo   Dashboard:  http://localhost:3000
echo   API Docs:   http://localhost:8000/docs
echo   Health:     http://localhost:8000/health
echo ============================================
echo.

echo Useful commands:
echo   View logs:       docker-compose logs -f
echo   View specific:   docker-compose logs -f [service-name]
echo   Stop services:   docker-compose down
echo   Restart:         docker-compose restart
echo   Rebuild:         docker-compose up -d --build
echo.

echo Press any key to open dashboard in browser...
pause >nul

start http://localhost:3000

echo.
echo System is running in Docker!
echo.
echo To view logs in real-time:
echo   docker-compose logs -f
echo.
echo To stop all services:
echo   docker-compose down
echo.
echo This window can be closed. Services run in background.
echo.
pause












