@echo off
REM Verox - Cleanup Script
REM Removes old/unused files to clean up the project

echo ============================================
echo   Verox - Cleanup Old Files
echo ============================================
echo.
echo This will remove old/duplicate batch files and unused scripts.
echo The main system files will NOT be deleted.
echo.
pause

REM Remove old batch files (keep only start.bat and stop.bat)
echo [1/3] Removing old batch files...
del /q "start_system.bat" >nul 2>&1
del /q "start_simple_final.bat" >nul 2>&1
del /q "start_simple_system.bat" >nul 2>&1
del /q "start_simple.bat" >nul 2>&1
del /q "START_VEROLUX_SIMPLE.bat" >nul 2>&1
del /q "START_VEROLUX.bat" >nul 2>&1
del /q "STOP_VEROLUX.bat" >nul 2>&1
del /q "start_with_alerts.bat" >nul 2>&1
del /q "FIX_LETTERBOXING_DETECTION.bat" >nul 2>&1
del /q "FIX_DETECTION_POSITIONING.bat" >nul 2>&1
del /q "TEST_STARTUP_FIX.bat" >nul 2>&1
del /q "START_DOCKER.bat" >nul 2>&1
del /q "START_DOCKER_GCP.bat" >nul 2>&1
del /q "STOP_DOCKER.bat" >nul 2>&1
del /q "start-production.bat" >nul 2>&1
del /q "Backend\quick_start.bat" >nul 2>&1
del /q "Backend\quick_test.bat" >nul 2>&1
del /q "Backend\restart_with_gate.bat" >nul 2>&1
del /q "Backend\start_gate_demo.bat" >nul 2>&1
echo [OK] Old batch files removed
echo.

REM Remove old backend files (obsolete servers)
echo [2/3] Removing old backend server files...
del /q "Backend\simple_video_inference.py" >nul 2>&1
del /q "Backend\backend_server_fixed.py" >nul 2>&1
del /q "Backend\backend_server.py" >nul 2>&1
del /q "Backend\simple_backend.py" >nul 2>&1
del /q "Backend\server.py" >nul 2>&1
del /q "Backend\simple_test.py" >nul 2>&1
del /q "Backend\simple_webcam_test.py" >nul 2>&1
del /q "Backend\test_websocket_client.py" >nul 2>&1
del /q "Backend\test_websocket_server.py" >nul 2>&1
del /q "start_simple_inference.py" >nul 2>&1
echo [OK] Old backend files removed
echo.

REM Remove duplicate/old Python files at root
echo [3/3] Cleaning up root directory...
del /q "START_VEROLUX.sh" >nul 2>&1
del /q "STOP_VEROLUX.sh" >nul 2>&1
del /q "start-production.sh" >nul 2>&1
echo [OK] Root directory cleaned
echo.

echo ============================================
echo   Cleanup Complete!
echo ============================================
echo.
echo Removed:
echo   - Old batch files (kept start.bat and stop.bat)
echo   - Obsolete backend server files
echo   - Old test files
echo.
echo Active files kept:
echo   - Backend\advanced_body_checking.py (main backend)
echo   - Frontend\ (React app)
echo   - start.bat (new startup script)
echo   - stop.bat (new stop script)
echo.
pause






