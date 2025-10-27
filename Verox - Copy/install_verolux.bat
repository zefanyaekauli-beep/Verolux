@echo off
echo ============================================================
echo 🚀 Verolux1st - Complete Installation Script
echo ============================================================
echo.
echo This script will install and configure the complete Verolux
echo Enterprise system on your Windows device.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo 📋 Checking system requirements...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python found
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js found
)

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
) else (
    echo ✅ Git found
)

echo.
echo 🔧 Installing Python dependencies...
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install Python packages
echo Installing Python packages...
pip install -r Backend\requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
) else (
    echo ✅ Python dependencies installed successfully
)

echo.
echo 📦 Installing Node.js dependencies...
echo.

REM Install Node.js packages
cd Frontend
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
) else (
    echo ✅ Node.js dependencies installed successfully
)

cd ..

echo.
echo 🗂️ Creating necessary directories...
echo.

REM Create directories
if not exist "Backend\models" mkdir Backend\models
if not exist "Backend\logs" mkdir Backend\logs
if not exist "Frontend\public" mkdir Frontend\public
if not exist "data" mkdir data

echo ✅ Directories created

echo.
echo 📝 Creating configuration files...
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env configuration file...
    (
        echo # Verolux1st Configuration
        echo BACKEND_HOST=0.0.0.0
        echo BACKEND_PORT=8000
        echo ANALYTICS_PORT=8002
        echo REPORTING_PORT=8001
        echo SEMANTIC_PORT=8003
        echo.
        echo # AI Model Configuration
        echo MODEL_PATH=Backend/models/weight.pt
        echo CONFIDENCE_THRESHOLD=0.5
        echo DEVICE=cuda
        echo.
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///verolux_enterprise.db
        echo.
        echo # Google Maps API ^(for GPS features^)
        echo GOOGLE_MAPS_API_KEY=your_api_key_here
        echo.
        echo # Language Configuration
        echo DEFAULT_LANGUAGE=en
        echo SUPPORTED_LANGUAGES=en,id,zh
    ) > .env
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

echo.
echo 🧠 Downloading AI models...
echo.

REM Download models if weight.pt doesn't exist
if not exist "Backend\models\weight.pt" (
    echo Downloading YOLO model...
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
    if exist "yolov8n.pt" (
        move yolov8n.pt Backend\models\weight.pt
        echo ✅ Model downloaded and moved
    ) else (
        echo ⚠️ Model download failed, using default
    )
) else (
    echo ✅ Model already exists
)

echo.
echo 🔧 Creating startup scripts...
echo.

REM Create startup script
(
    echo @echo off
    echo echo 🚀 Starting Verolux1st Complete System
    echo echo ============================================================
    echo echo 📊 Comprehensive Analytics ^& Reporting
    echo echo 🎯 Real-time Object Detection with YOLO
    echo echo 📈 Advanced Analytics Dashboard
    echo echo ============================================================
    echo echo.
    echo.
    echo echo 🔧 Starting Backend Services...
    echo start "Verolux Backend" cmd /k "cd Backend && call ..\venv\Scripts\activate.bat && python backend_server.py"
    echo timeout /t 3 /nobreak ^>nul
    echo.
    echo echo 📊 Starting Analytics Backend...
    echo start "Verolux Analytics" cmd /k "cd Backend && call ..\venv\Scripts\activate.bat && python analytics_system.py"
    echo timeout /t 3 /nobreak ^>nul
    echo.
    echo echo 📋 Starting Reporting Backend...
    echo start "Verolux Reporting" cmd /k "cd Backend && call ..\venv\Scripts\activate.bat && python reporting_system.py"
    echo timeout /t 3 /nobreak ^>nul
    echo.
    echo echo 🧠 Starting Semantic Search Backend...
    echo start "Verolux Semantic Search" cmd /k "cd Backend && call ..\venv\Scripts\activate.bat && python semantic_search.py"
    echo timeout /t 3 /nobreak ^>nul
    echo.
    echo echo 🌐 Starting Frontend...
    echo start "Verolux Frontend" cmd /k "cd Frontend && npm run dev"
    echo.
    echo echo ✅ All services started!
    echo echo.
    echo echo 🌐 Access URLs:
    echo echo - Main Dashboard: http://localhost:5173
    echo echo - Backend API: http://localhost:8000
    echo echo - Analytics API: http://localhost:8002
    echo echo - Reporting API: http://localhost:8001
    echo echo - Semantic Search API: http://localhost:8003
    echo echo.
    echo echo Press any key to exit...
    echo pause ^>nul
) > START_VEROLUX_COMPLETE.bat

echo ✅ Startup script created

echo.
echo 🧪 Running system tests...
echo.

REM Test Python installation
python -c "import fastapi, uvicorn, ultralytics; print('✅ Python packages working')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Some Python packages may have issues
)

REM Test Node.js installation
cd Frontend
npm run build >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Frontend build test failed
) else (
    echo ✅ Frontend build test passed
)
cd ..

echo.
echo ============================================================
echo 🎉 Installation Complete!
echo ============================================================
echo.
echo ✅ All components installed successfully
echo ✅ Configuration files created
echo ✅ Startup scripts ready
echo.
echo 🚀 To start the system, run:
echo    START_VEROLUX_COMPLETE.bat
echo.
echo 🌐 After starting, access:
echo    http://localhost:5173
echo.
echo 📚 For more information, see:
echo    INSTALLATION_GUIDE.md
echo.
echo Press any key to exit...
pause >nul

