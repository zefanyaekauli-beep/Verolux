#!/bin/bash
# Verolux Enterprise - Start All Systems
# Starts Backend + Frontend in separate terminals

set -e

echo "============================================"
echo "Verolux Enterprise - Starting All Systems"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -d "Backend" ]; then
    echo "Error: Backend directory not found"
    echo "Please run this script from the Verolux root directory"
    exit 1
fi

if [ ! -d "Frontend" ]; then
    echo "Error: Frontend directory not found"
    echo "Please run this script from the Verolux root directory"
    exit 1
fi

echo "Step 1: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found!"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi
echo "[OK] Python found: $(python3 --version)"

echo ""
echo "Step 2: Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found!"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi
echo "[OK] Node.js found: $(node --version)"

echo ""
echo "Step 3: Checking Backend dependencies..."
if [ ! -d "Backend/venv" ]; then
    echo "[INFO] Creating virtual environment..."
    cd Backend
    python3 -m venv venv
    source venv/bin/activate
    echo "[INFO] Installing dependencies..."
    pip install -q -r requirements.txt
    cd ..
    echo "[OK] Dependencies installed"
else
    echo "[OK] Virtual environment exists"
fi

echo ""
echo "Step 4: Checking Frontend dependencies..."
if [ ! -d "Frontend/node_modules" ]; then
    echo "[INFO] Installing Node.js dependencies..."
    cd Frontend
    npm install
    cd ..
    echo "[OK] Dependencies installed"
else
    echo "[OK] Node modules exist"
fi

echo ""
echo "Step 5: Starting Backend..."
echo "[INFO] Starting backend in background..."

cd Backend
source venv/bin/activate
nohup python backend_server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "[OK] Backend started (PID: $BACKEND_PID)"
echo "     Log: logs/backend.log"

# Wait for backend to start
sleep 3

echo ""
echo "Step 6: Starting Frontend..."
echo "[INFO] Starting frontend in background..."

cd Frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "[OK] Frontend started (PID: $FRONTEND_PID)"
echo "     Log: logs/frontend.log"

echo ""
echo "============================================"
echo "[OK] Verolux System Starting!"
echo "============================================"
echo ""
echo "Services started:"
echo "  Backend  (PID $BACKEND_PID) - http://localhost:8000"
echo "  Frontend (PID $FRONTEND_PID) - http://localhost:5173"
echo ""
echo "Waiting 10 seconds for services to initialize..."
sleep 10

echo ""
echo "Testing services..."
python Backend/simple_test.py || true

echo ""
echo "============================================"
echo "Access your system:"
echo "  Dashboard:  http://localhost:5173"
echo "  API Docs:   http://localhost:8000/docs"
echo "  Status:     http://localhost:8000/status/production"
echo "============================================"
echo ""
echo "Process IDs saved to .verolux_pids"
echo "$BACKEND_PID" > .verolux_pids
echo "$FRONTEND_PID" >> .verolux_pids
echo ""
echo "To stop the system, run: ./STOP_VEROLUX.sh"
echo ""

# Try to open browser (works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173 &
elif command -v open &> /dev/null; then
    open http://localhost:5173 &
fi

echo "System is running!"
echo "View logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""













