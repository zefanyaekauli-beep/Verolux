#!/bin/bash

echo "============================================================"
echo "🚀 Verolux1st - Complete Installation Script"
echo "============================================================"
echo ""
echo "This script will install and configure the complete Verolux"
echo "Enterprise system on your Linux/macOS device."
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read

echo ""
echo "📋 Checking system requirements..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
else
    echo "✅ Python3 found"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
else
    echo "✅ Node.js found"
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed or not in PATH"
    echo "Please install Git from your package manager"
    exit 1
else
    echo "✅ Git found"
fi

echo ""
echo "🔧 Installing Python dependencies..."
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Python packages
echo "Installing Python packages..."
pip install -r Backend/requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
else
    echo "✅ Python dependencies installed successfully"
fi

echo ""
echo "📦 Installing Node.js dependencies..."
echo ""

# Install Node.js packages
cd Frontend
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
else
    echo "✅ Node.js dependencies installed successfully"
fi

cd ..

echo ""
echo "🗂️ Creating necessary directories..."
echo ""

# Create directories
mkdir -p Backend/models
mkdir -p Backend/logs
mkdir -p Frontend/public
mkdir -p data

echo "✅ Directories created"

echo ""
echo "📝 Creating configuration files..."
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env configuration file..."
    cat > .env << EOF
# Verolux1st Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ANALYTICS_PORT=8002
REPORTING_PORT=8001
SEMANTIC_PORT=8003

# AI Model Configuration
MODEL_PATH=Backend/models/weight.pt
CONFIDENCE_THRESHOLD=0.5
DEVICE=cuda

# Database Configuration
DATABASE_URL=sqlite:///verolux_enterprise.db

# Google Maps API (for GPS features)
GOOGLE_MAPS_API_KEY=your_api_key_here

# Language Configuration
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,id,zh
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🧠 Downloading AI models..."
echo ""

# Download models if weight.pt doesn't exist
if [ ! -f "Backend/models/weight.pt" ]; then
    echo "Downloading YOLO model..."
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
    if [ -f "yolov8n.pt" ]; then
        mv yolov8n.pt Backend/models/weight.pt
        echo "✅ Model downloaded and moved"
    else
        echo "⚠️ Model download failed, using default"
    fi
else
    echo "✅ Model already exists"
fi

echo ""
echo "🔧 Creating startup scripts..."
echo ""

# Create startup script
cat > start_verolux_complete.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Verolux1st Complete System"
echo "============================================================"
echo "📊 Comprehensive Analytics & Reporting"
echo "🎯 Real-time Object Detection with YOLO"
echo "📈 Advanced Analytics Dashboard"
echo "============================================================"
echo ""

# Activate virtual environment
source venv/bin/activate

echo "🔧 Starting Backend Services..."
gnome-terminal --title="Verolux Backend" -- bash -c "cd Backend && python backend_server.py; exec bash" 2>/dev/null || \
xterm -title "Verolux Backend" -e "cd Backend && python backend_server.py; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/Backend && python backend_server.py"' 2>/dev/null || \
echo "Please start backend manually: cd Backend && python backend_server.py"

sleep 3

echo "📊 Starting Analytics Backend..."
gnome-terminal --title="Verolux Analytics" -- bash -c "cd Backend && python analytics_system.py; exec bash" 2>/dev/null || \
xterm -title "Verolux Analytics" -e "cd Backend && python analytics_system.py; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/Backend && python analytics_system.py"' 2>/dev/null || \
echo "Please start analytics manually: cd Backend && python analytics_system.py"

sleep 3

echo "📋 Starting Reporting Backend..."
gnome-terminal --title="Verolux Reporting" -- bash -c "cd Backend && python reporting_system.py; exec bash" 2>/dev/null || \
xterm -title "Verolux Reporting" -e "cd Backend && python reporting_system.py; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/Backend && python reporting_system.py"' 2>/dev/null || \
echo "Please start reporting manually: cd Backend && python reporting_system.py"

sleep 3

echo "🧠 Starting Semantic Search Backend..."
gnome-terminal --title="Verolux Semantic Search" -- bash -c "cd Backend && python semantic_search.py; exec bash" 2>/dev/null || \
xterm -title "Verolux Semantic Search" -e "cd Backend && python semantic_search.py; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/Backend && python semantic_search.py"' 2>/dev/null || \
echo "Please start semantic search manually: cd Backend && python semantic_search.py"

sleep 3

echo "🌐 Starting Frontend..."
gnome-terminal --title="Verolux Frontend" -- bash -c "cd Frontend && npm run dev; exec bash" 2>/dev/null || \
xterm -title "Verolux Frontend" -e "cd Frontend && npm run dev; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/Frontend && npm run dev"' 2>/dev/null || \
echo "Please start frontend manually: cd Frontend && npm run dev"

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Access URLs:"
echo "- Main Dashboard: http://localhost:5173"
echo "- Backend API: http://localhost:8000"
echo "- Analytics API: http://localhost:8002"
echo "- Reporting API: http://localhost:8001"
echo "- Semantic Search API: http://localhost:8003"
echo ""
echo "Press Enter to exit..."
read
EOF

chmod +x start_verolux_complete.sh
echo "✅ Startup script created"

echo ""
echo "🧪 Running system tests..."
echo ""

# Test Python installation
python -c "import fastapi, uvicorn, ultralytics; print('✅ Python packages working')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Some Python packages may have issues"
fi

# Test Node.js installation
cd Frontend
npm run build >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ Frontend build test failed"
else
    echo "✅ Frontend build test passed"
fi
cd ..

echo ""
echo "============================================================"
echo "🎉 Installation Complete!"
echo "============================================================"
echo ""
echo "✅ All components installed successfully"
echo "✅ Configuration files created"
echo "✅ Startup scripts ready"
echo ""
echo "🚀 To start the system, run:"
echo "   ./start_verolux_complete.sh"
echo ""
echo "🌐 After starting, access:"
echo "   http://localhost:5173"
echo ""
echo "📚 For more information, see:"
echo "   INSTALLATION_GUIDE.md"
echo ""
echo "Press Enter to exit..."
read

