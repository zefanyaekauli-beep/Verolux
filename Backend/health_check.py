#!/usr/bin/env python3
"""
Simple health check for Verolux backend
"""
import requests
import sys

def check_backend_health():
    """Check if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Backend Status: {data.get('status', 'unknown')}")
            print(f"Model Loaded: {data.get('model_loaded', False)}")
            return True
        else:
            print(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    if check_backend_health():
        print("[OK] Backend health check passed")
        sys.exit(0)
    else:
        print("[ERROR] Backend health check failed")
        sys.exit(1)