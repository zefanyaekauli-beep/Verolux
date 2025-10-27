@echo off
echo ============================================================
echo 🚀 Verolux1st - Quick Start
echo ============================================================
echo.
echo This script will quickly start the Verolux1st system
echo with all components running.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo 🔧 Starting all services...
echo.

REM Start Backend
echo Starting Backend Server...
start "Verolux Backend" cmd /k "cd Backend && python backend_server.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Analytics
echo Starting Analytics Backend...
start "Verolux Analytics" cmd /k "cd Backend && python analytics_system.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Reporting
echo Starting Reporting Backend...
start "Verolux Reporting" cmd /k "cd Backend && python reporting_system.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Semantic Search
echo Starting Semantic Search Backend...
start "Verolux Semantic Search" cmd /k "cd Backend && python semantic_search.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Frontend
echo Starting Frontend...
start "Verolux Frontend" cmd /k "cd Frontend && npm run dev"

echo.
echo ✅ All services started!
echo.
echo 🌐 Access URLs:
echo - Main Dashboard: http://localhost:5173
echo - Backend API: http://localhost:8000
echo - Analytics API: http://localhost:8002
echo - Reporting API: http://localhost:8001
echo - Semantic Search API: http://localhost:8003
echo.
echo Press any key to exit...
pause >nul

