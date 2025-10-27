@echo off
echo Starting Simple Video Inference System...

echo Starting Backend Server...
start "Backend" cmd /k "cd /d C:\Users\User\Desktop\Verox\Backend && python simple_video_inference.py"

timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "Frontend" cmd /k "cd /d C:\Users\User\Desktop\Verox\Frontend && npm run dev"

echo.
echo Services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window (services will continue running)
pause >nul

