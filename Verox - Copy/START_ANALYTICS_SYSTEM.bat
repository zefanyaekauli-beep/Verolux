@echo off
echo 🚀 Starting Verolux Enterprise Analytics System
echo ============================================================
echo 📊 Comprehensive Advanced Analytics
echo 🎯 Traffic Flow, Behavior, PPE, Anomaly Detection
echo 📈 Advanced Analytics Dashboard
echo ============================================================

echo.
echo 🔧 Starting Analytics Backend API...
cd Backend
start "Analytics Backend" python analytics_system.py

echo.
echo ⏳ Waiting for analytics backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🔧 Starting Reporting Backend API...
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
echo ✅ Complete Analytics System Started!
echo.
echo 📊 Analytics API: http://localhost:8002
echo 📈 Reporting API: http://localhost:8001
echo 🎯 Detection API: http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo 📊 Analytics: Navigate to Analytics page in the frontend
echo.
echo 🎯 Available Analytics Features:
echo   • Traffic Flow Analytics (Directional counts, flow paths)
echo   • Zone Utilization Analytics (Occupancy, efficiency metrics)
echo   • Behavior Analysis (Loitering, intrusion, safety patterns)
echo   • PPE Compliance Analytics (Safety gear compliance tracking)
echo   • Anomaly Detection Analytics (Unusual activity identification)
echo   • System Health Analytics (Camera and system performance)
echo   • Operational Efficiency Analytics (Resource usage optimization)
echo   • Heatmap Analytics (Visual activity intensity maps)
echo.
echo Press any key to stop all services...
pause > nul

echo.
echo 🛑 Stopping all services...
taskkill /f /im python.exe /im node.exe 2>nul
echo ✅ All services stopped.
