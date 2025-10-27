#!/bin/bash
# Stop all Verolux services

echo "============================================"
echo "Verolux Enterprise - Stopping All Systems"
echo "============================================"
echo ""

# Check for PID file
if [ -f ".verolux_pids" ]; then
    echo "Stopping processes from PID file..."
    
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            echo "Stopped process $pid"
        fi
    done < .verolux_pids
    
    rm .verolux_pids
    echo "[OK] Services stopped from PID file"
else
    echo "No PID file found, attempting to find and kill processes..."
    
    # Kill Python backend
    pkill -f "backend_server.py" && echo "Stopped backend"
    
    # Kill Node frontend
    pkill -f "vite" && echo "Stopped frontend"
fi

echo ""

# Stop Docker containers if running
if [ -f "docker-compose.production.yml" ]; then
    docker-compose -f docker-compose.production.yml down > /dev/null 2>&1
fi

if [ -f "docker-compose.hardened.yml" ]; then
    docker-compose -f docker-compose.hardened.yml down > /dev/null 2>&1
fi

echo "============================================"
echo "Verolux System Stopped"
echo "============================================"
echo ""
echo "To restart: ./START_VEROLUX.sh"
echo ""













