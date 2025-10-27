#!/usr/bin/env python3
"""
Verolux1st - Health Check Script
Checks the health of all system components
"""

import requests
import time
import sys
from pathlib import Path

def check_backend_health(port=8000, timeout=5):
    """Check if backend is running and healthy"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend (port {port}): {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend (port {port}): HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend (port {port}): {e}")
        return False

def check_analytics_health(port=8002, timeout=5):
    """Check if analytics backend is running"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics (port {port}): {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Analytics (port {port}): HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Analytics (port {port}): {e}")
        return False

def check_reporting_health(port=8001, timeout=5):
    """Check if reporting backend is running"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reporting (port {port}): {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Reporting (port {port}): HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Reporting (port {port}): {e}")
        return False

def check_semantic_health(port=8003, timeout=5):
    """Check if semantic search backend is running"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Semantic Search (port {port}): {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Semantic Search (port {port}): HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Semantic Search (port {port}): {e}")
        return False

def check_frontend_health(port=5173, timeout=5):
    """Check if frontend is running"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=timeout)
        if response.status_code == 200:
            print(f"✅ Frontend (port {port}): Running")
            return True
        else:
            print(f"❌ Frontend (port {port}): HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend (port {port}): {e}")
        return False

def check_model_files():
    """Check if required model files exist"""
    print("\n🔍 Checking model files...")
    
    model_path = Path("Backend/models/weight.pt")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ YOLO model: {model_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"❌ YOLO model: {model_path} not found")
        return False

def check_database():
    """Check if database exists"""
    print("\n🔍 Checking database...")
    
    db_path = Path("Backend/verolux_enterprise.db")
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ Database: {db_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"⚠️ Database: {db_path} not found (will be created on first run)")
        return True

def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'ultralytics',
        'opencv-python',
        'numpy',
        'sentence-transformers',
        'scikit-learn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        return False
    
    return True

def main():
    print("🏥 Verolux1st - Health Check")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check model files
    model_ok = check_model_files()
    
    # Check database
    db_ok = check_database()
    
    print("\n🌐 Checking running services...")
    
    # Check all services
    backend_ok = check_backend_health()
    analytics_ok = check_analytics_health()
    reporting_ok = check_reporting_health()
    semantic_ok = check_semantic_health()
    frontend_ok = check_frontend_health()
    
    # Summary
    print("\n📊 Health Check Summary:")
    print("=" * 30)
    
    services_running = sum([
        backend_ok,
        analytics_ok,
        reporting_ok,
        semantic_ok,
        frontend_ok
    ])
    
    total_services = 5
    
    print(f"Services Running: {services_running}/{total_services}")
    print(f"Dependencies: {'✅ OK' if deps_ok else '❌ Missing'}")
    print(f"Model Files: {'✅ OK' if model_ok else '❌ Missing'}")
    print(f"Database: {'✅ OK' if db_ok else '❌ Missing'}")
    
    if services_running == total_services and deps_ok and model_ok:
        print("\n🎉 All systems healthy!")
        return 0
    elif services_running > 0:
        print(f"\n⚠️ Partial system running ({services_running}/{total_services} services)")
        return 1
    else:
        print("\n❌ No services running")
        return 2

if __name__ == "__main__":
    sys.exit(main())

