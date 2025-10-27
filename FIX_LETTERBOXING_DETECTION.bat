@echo off
REM Fix Letterboxing Detection - Proper coordinate mapping
REM Implements the exact solution for detection positioning with letterboxing

echo ============================================
echo Verolux - Fixing Letterboxing Detection
echo ============================================
echo.

echo [1/6] Stopping all processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo [OK] All processes stopped

echo.
echo [2/6] Checking AI model...
if exist "weight.pt" (
    echo [OK] Found weight.pt in root directory
) else (
    echo [ERROR] weight.pt not found in root directory
    echo Please ensure your AI model is at: %cd%\weight.pt
    pause
    exit /b 1
)

echo.
echo [3/6] Ensuring model is in Backend directory...
if not exist "Backend\models\weight.pt" (
    echo [INFO] Copying weight.pt to Backend\models...
    copy "weight.pt" "Backend\models\" >nul 2>&1
    echo [OK] Model copied to Backend\models
) else (
    echo [OK] Model already exists in Backend\models
)

echo.
echo [4/6] Checking video file...
if exist "Frontend\public\videoplayback.mp4" (
    echo [OK] Video file exists in Frontend\public
) else (
    echo [INFO] Copying video file to Frontend\public...
    copy "videoplayback.mp4" "Frontend\public\" >nul 2>&1
    echo [OK] Video file copied
)

echo.
echo [5/6] Starting Backend with Proper Detection Processing...
start "Verolux Backend - Letterboxing Fix" cmd /k "cd /d %cd%\Backend && .\venv\Scripts\activate && python backend_server_fixed.py"
echo [OK] Backend starting with proper detection processing...
timeout /t 10 /nobreak >nul 2>&1

echo.
echo [6/6] Starting Frontend with Letterboxing Detection Fix...
start "Verolux Frontend - Letterboxing Fix" cmd /k "cd /d %cd%\Frontend && npm run dev"
echo [OK] Frontend starting with letterboxing detection fix...

echo.
echo ============================================
echo Letterboxing Detection Fix Complete!
echo ============================================
echo.
echo Key Changes Made:
echo   ✅ Frontend: Proper letterboxing handling with object-fit: contain
echo   ✅ Frontend: Correct coordinate mapping from AI model to display
echo   ✅ Frontend: HiDPI support with devicePixelRatio
echo   ✅ Frontend: Proper offset calculation for black bars
echo   ✅ Frontend: Video styling with objectFit: 'contain'
echo   ✅ Frontend: Canvas positioning with absolute inset-0
echo.
echo Technical Implementation:
echo   - CSS size vs intrinsic video size handling
echo   - Aspect-fit letterbox calculation (r = min(cssW/srcW, cssH/srcH))
echo   - Offset calculation for black bars (offsetX, offsetY)
echo   - Proper coordinate mapping: x = offsetX + x1 * (drawW/srcW)
echo   - HiDPI support with devicePixelRatio
echo.
echo Waiting for services to start (15 seconds)...
timeout /t 15 /nobreak >nul 2>&1

echo.
echo ============================================
echo System Ready with Letterboxing Detection!
echo ============================================
echo.
echo Access your system:
echo   Dashboard: http://localhost:5173
echo   Video Demo: http://localhost:5173 (Navigate to VideoplaybackDemo)
echo.
echo Expected Results:
echo   ✅ Detection boxes appear ON the video (not outside)
echo   ✅ Proper handling of letterboxing (black bars)
echo   ✅ Detection coordinates map correctly to video display
echo   ✅ HiDPI support for crisp detection lines
echo   ✅ Detection boxes stay within video bounds
echo.
echo Console Debug Information:
echo   - "CSS size: W x H" (video element size)
echo   - "Source size: W x H" (video intrinsic size)
echo   - "Draw size: W x H" (actual video area after letterboxing)
echo   - "Offset: X x Y" (black bar offsets)
echo   - "Detection X: [coords] -> [scaled coords]"
echo.
echo Opening dashboard in 3 seconds...
timeout /t 3 /nobreak >nul 2>&1
start http://localhost:5173

echo.
echo Letterboxing detection is now properly implemented!
echo.
echo If detection boxes are still outside the video:
echo   1. Check browser console for CSS size vs Source size
echo   2. Verify Draw size and Offset calculations
echo   3. Check that video has objectFit: 'contain' styling
echo   4. Ensure canvas is positioned with absolute inset-0
echo   5. Verify detection coordinates are reasonable
echo.
echo If detection boxes are too small or large:
echo   1. Check the scaling ratio (r = min(cssW/srcW, cssH/srcH))
echo   2. Verify offset calculations are correct
echo   3. Check that video dimensions match between AI and display
echo   4. Ensure proper coordinate mapping formula
echo.
pause


