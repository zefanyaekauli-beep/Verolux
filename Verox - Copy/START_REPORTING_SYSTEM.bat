@echo off
echo 🚀 Starting Verolux Enterprise Reporting System
echo ============================================================
echo 📊 Comprehensive Analytics & Reporting
echo 🎯 Advanced Reports Available
echo ============================================================

echo.
echo 🔧 Starting Backend Reporting API...
cd Backend
start "Reporting Backend" python reporting_system.py

echo.
echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🌐 Starting Frontend Development Server...
cd ..\Frontend
start "Frontend Dev Server" npm run dev

echo.
echo ✅ Reporting System Started!
echo.
echo 📊 Backend API: http://localhost:8001
echo 🌐 Frontend: http://localhost:5173
echo 📈 Reports: Navigate to Reports page in the frontend
echo.
echo Press any key to stop all services...
pause > nul

echo.
echo 🛑 Stopping all services...
taskkill /f /im python.exe /im node.exe 2>nul
echo ✅ All services stopped.
