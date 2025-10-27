#!/usr/bin/env python3
"""
Simple Video Inference System Startup Script
"""

import subprocess
import sys
import os
import time
import signal
import threading

def start_backend():
    """Start the simple inference backend"""
    print("Starting Simple Video Inference Backend...")
    try:
        # Change to Backend directory
        os.chdir('Backend')
        
        # Start the simple inference server
        process = subprocess.Popen([
            sys.executable, 'simple_video_inference.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Backend server started on http://localhost:8000")
        return process
    except Exception as e:
        print(f"Error starting backend: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("Starting Frontend Development Server...")
    try:
        # Change to Frontend directory
        os.chdir('Frontend')
        
        # Start the frontend server
        process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Frontend server started on http://localhost:5173")
        return process
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("Simple Video Inference System")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists('Backend/simple_video_inference.py'):
        print("Backend/simple_video_inference.py not found!")
        return
    
    if not os.path.exists('Frontend/package.json'):
        print("Frontend/package.json not found!")
        return
    
    if not os.path.exists('weight.pt'):
        print("weight.pt not found in root directory!")
        print("   Please ensure weight.pt is in the project root")
    
    if not os.path.exists('videoplayback.mp4'):
        print("videoplayback.mp4 not found in root directory!")
        print("   Please ensure videoplayback.mp4 is in the project root")
    
    print("\nStarting services...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("Failed to start backend")
        return
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("Failed to start frontend")
        backend_process.terminate()
        return
    
    print("\nSimple Video Inference System is running!")
    print("Frontend: http://localhost:5173")
    print("Backend: http://localhost:8000")
    print("Video Stream: http://localhost:8000/stream")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("Backend process stopped")
                break
                
            if frontend_process.poll() is not None:
                print("Frontend process stopped")
                break
                
    except KeyboardInterrupt:
        print("\nStopping services...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("All services stopped")

if __name__ == "__main__":
    main()
