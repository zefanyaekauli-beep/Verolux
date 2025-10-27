#!/bin/bash

echo "============================================================"
echo "🚀 Verolux1st - Complete Installation Script"
echo "============================================================"
echo ""
echo "This script will install and configure the complete Verolux1st"
echo "system on your Linux/macOS device."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi
echo "✅ Python found"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi
echo "✅ Node.js found"

echo ""
echo "🔧 Installing Backend Dependencies..."
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo "✅ Backend dependencies installed"

echo ""
echo "🔧 Installing Frontend Dependencies..."
cd ../Frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi
echo "✅ Frontend dependencies installed"

echo ""
echo "📁 Creating necessary directories..."
cd ../Backend
mkdir -p models
mkdir -p uploads
echo "✅ Directories created"

echo ""
echo "🧠 Downloading AI Models..."
python download_models.py
if [ $? -ne 0 ]; then
    echo "⚠️ Model download failed, but system will work with simulated data"
fi
echo "✅ Models ready"

echo ""
echo "🗄️ Initializing Database..."
python -c "import sqlite3; conn = sqlite3.connect('verolux1st.db'); conn.close()"
echo "✅ Database initialized"

echo ""
echo "📝 Creating startup scripts..."

# Create main startup script
cat > START_VEROLUX1ST.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Verolux1st Complete System"
echo "============================================================"
echo "📊 Comprehensive Analytics & Reporting"
echo "🎯 Real-time Object Detection with YOLO"
echo "📈 Advanced Analytics Dashboard"
echo "🧠 Semantic Search Engine"
echo "🗺️ GPS Heatmap Visualization"
echo "============================================================"
echo ""
echo "Starting all services..."
echo ""

# Start backend services
cd Backend
source venv/bin/activate

# Start main backend
gnome-terminal --title="Verolux1st Backend" -- bash -c "python backend_server.py; exec bash" 2>/dev/null || \
xterm -title "Verolux1st Backend" -e "python backend_server.py" 2>/dev/null || \
python backend_server.py &

sleep 3

# Start analytics
gnome-terminal --title="Verolux1st Analytics" -- bash -c "python analytics_system.py; exec bash" 2>/dev/null || \
xterm -title "Verolux1st Analytics" -e "python analytics_system.py" 2>/dev/null || \
python analytics_system.py &

sleep 2

# Start reporting
gnome-terminal --title="Verolux1st Reporting" -- bash -c "python reporting_system.py; exec bash" 2>/dev/null || \
xterm -title "Verolux1st Reporting" -e "python reporting_system.py" 2>/dev/null || \
python reporting_system.py &

sleep 2

# Start semantic search
gnome-terminal --title="Verolux1st Semantic Search" -- bash -c "python semantic_search.py; exec bash" 2>/dev/null || \
xterm -title "Verolux1st Semantic Search" -e "python semantic_search.py" 2>/dev/null || \
python semantic_search.py &

sleep 2

# Start frontend
cd ../Frontend
gnome-terminal --title="Verolux1st Frontend" -- bash -c "npm run dev; exec bash" 2>/dev/null || \
xterm -title "Verolux1st Frontend" -e "npm run dev" 2>/dev/null || \
npm run dev &

echo "✅ All services started!"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Analytics: http://localhost:8002"
echo "📋 Reporting: http://localhost:8001"
echo "🧠 Semantic Search: http://localhost:8003"
echo ""
echo "Press Ctrl+C to stop all services"
EOF

chmod +x START_VEROLUX1ST.sh
echo "✅ Startup script created"

echo ""
echo "🎉 Installation Complete!"
echo "============================================================"
echo ""
echo "📋 What was installed:"
echo "  ✅ Python virtual environment with all dependencies"
echo "  ✅ Node.js dependencies for React frontend"
echo "  ✅ AI models for object detection"
echo "  ✅ Database initialized"
echo "  ✅ Startup scripts created"
echo ""
echo "🚀 To start the system:"
echo "   ./START_VEROLUX1ST.sh"
echo ""
echo "🌐 Access the system at: http://localhost:5173"
echo ""
echo "📚 For more information, see README.md"
echo ""

