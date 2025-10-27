@echo off
echo Starting Simple Video Inference System with Popup Alerts...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd Backend && python simple_video_inference.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd Frontend && npm run dev"

echo.
echo Services are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:5176 (or next available port)
echo.
echo Both services will open in separate windows.
echo The backend will stay running and connected.
echo Close this window when done.
pause

