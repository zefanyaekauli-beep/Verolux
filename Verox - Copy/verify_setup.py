#!/usr/bin/env python3
"""
Verolux1st - Setup Verification Script
Verifies that the system is properly installed and configured
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_node_version():
    """Check Node.js version"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def check_git_version():
    """Check Git version"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
            return True
        else:
            print("❌ Git not found")
            return False
    except FileNotFoundError:
        print("❌ Git not found")
        return False

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        "Backend",
        "Frontend",
        "Backend/models",
        "Frontend/src",
        "Frontend/src/components",
        "Frontend/src/pages",
        "Frontend/src/stores"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            all_exist = False
    
    return all_exist

def check_files():
    """Check if required files exist"""
    required_files = [
        "Backend/requirements.txt",
        "Frontend/package.json",
        "Backend/backend_server.py",
        "Frontend/src/App.jsx",
        "Backend/health_check.py",
        "Backend/download_models.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist

def check_python_dependencies():
    """Check if Python dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import ultralytics
        import cv2
        import numpy
        print("✅ Python dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        return False

def check_node_dependencies():
    """Check if Node.js dependencies are installed"""
    node_modules = Path("Frontend/node_modules")
    if node_modules.exists():
        print("✅ Node.js dependencies installed")
        return True
    else:
        print("❌ Node.js dependencies not installed")
        return False

def check_models():
    """Check if AI models are available"""
    model_path = Path("Backend/models/weight.pt")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ AI model: {size_mb:.1f} MB")
        return True
    else:
        print("⚠️ AI model not found (will download on first run)")
        return True

def main():
    print("🔍 Verolux1st - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Node.js Version", check_node_version),
        ("Git Version", check_git_version),
        ("Directories", check_directories),
        ("Files", check_files),
        ("Python Dependencies", check_python_dependencies),
        ("Node.js Dependencies", check_node_dependencies),
        ("AI Models", check_models)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📊 Verification Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup verification complete! System is ready to run.")
        print("\n🚀 To start the system:")
        print("   Windows: QUICK_START.bat")
        print("   Linux/macOS: ./start_verolux_complete.sh")
        return 0
    elif passed >= total * 0.8:
        print("\n⚠️ Most checks passed. System should work with minor issues.")
        return 1
    else:
        print("\n❌ Multiple issues found. Please run the installation script.")
        print("   Windows: install_verolux.bat")
        print("   Linux/macOS: ./install_verolux.sh")
        return 2

if __name__ == "__main__":
    sys.exit(main())

