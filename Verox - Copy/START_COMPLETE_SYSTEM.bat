@echo off
echo 🚀 Starting Verolux Enterprise Complete System
echo ============================================================
echo 📊 Comprehensive Analytics & Reporting
echo 🎯 Real-time Object Detection with YOLO
echo 📈 Advanced Analytics Dashboard
echo ============================================================

echo.
echo 🔧 Starting Backend Reporting API...
cd Backend
start "Reporting Backend" python reporting_system.py

echo.
echo ⏳ Waiting for reporting backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🔧 Starting Main Detection Backend...
start "Detection Backend" python realtime_backend.py

echo.
echo ⏳ Waiting for detection backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🌐 Starting Frontend Development Server...
cd ..\Frontend
start "Frontend Dev Server" npm run dev

echo.
echo ✅ Complete System Started!
echo.
echo 📊 Reporting API: http://localhost:8001
echo 🎯 Detection API: http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo 📈 Reports: Navigate to Reports page in the frontend
echo.
echo 🎯 Available Features:
echo   • Real-time Object Detection (Person, Vehicle, etc.)
echo   • Comprehensive Analytics Dashboard
echo   • Zone Occupancy & Utilization Reports
echo   • Line Crossing Analytics
echo   • Loitering Detection & Tracking
echo   • Intrusion Detection & Alerts
echo   • Hazard & Safety Event Monitoring
echo   • Anomaly Detection & Analysis
echo   • PPE Compliance Tracking
echo   • Traffic Pattern Analysis
echo   • Shift-based Analytics
echo   • Export Tools (CSV, Excel, PDF, JSON)
echo.
echo Press any key to stop all services...
pause > nul

echo.
echo 🛑 Stopping all services...
taskkill /f /im python.exe /im node.exe 2>nul
echo ✅ All services stopped.
