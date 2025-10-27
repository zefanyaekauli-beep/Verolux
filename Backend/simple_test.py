"""
Simple Test Script
Basic health check for the backend
"""

import requests
import sys

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("Backend is running and healthy")
            return True
        else:
            print(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Backend is not responding: {e}")
        return False

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)




