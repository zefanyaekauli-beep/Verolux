#!/usr/bin/env python3
"""
Verolux System Diagnostics
Checks model, CUDA, and video feed issues
"""
import sys
import os
from colorama import init, Fore, Style

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def print_ok(text):
    print(f"{Fore.GREEN}[OK] {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}[ERROR] {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}[WARNING] {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.CYAN}[INFO] {text}{Style.RESET_ALL}")

print_header("Verolux System Diagnostics")

# ===== CHECK 1: Python & Packages =====
print_header("1. Checking Python Environment")

print(f"Python version: {sys.version}")
print_ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Check required packages
required_packages = {
    'torch': 'PyTorch (for AI models)',
    'cv2': 'OpenCV (for video processing)',
    'ultralytics': 'Ultralytics (for YOLO)',
    'fastapi': 'FastAPI (for API)',
    'numpy': 'NumPy (for arrays)',
}

print("\nChecking required packages:")
missing_packages = []

for package, description in required_packages.items():
    try:
        if package == 'cv2':
            import cv2
            print_ok(f"{description:40} - Version {cv2.__version__}")
        elif package == 'torch':
            import torch
            print_ok(f"{description:40} - Version {torch.__version__}")
        elif package == 'ultralytics':
            import ultralytics
            print_ok(f"{description:40} - Version {ultralytics.__version__}")
        elif package == 'fastapi':
            import fastapi
            print_ok(f"{description:40} - Version {fastapi.__version__}")
        elif package == 'numpy':
            import numpy
            print_ok(f"{description:40} - Version {numpy.__version__}")
    except ImportError:
        print_error(f"{description:40} - NOT INSTALLED")
        missing_packages.append(package)

if missing_packages:
    print_error(f"\nMissing packages: {', '.join(missing_packages)}")
    print_info("Install with: pip install -r requirements.txt")
    sys.exit(1)

# ===== CHECK 2: CUDA / GPU =====
print_header("2. Checking CUDA / GPU")

try:
    import torch
    
    if torch.cuda.is_available():
        print_ok(f"CUDA is available!")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU Count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print_ok(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Test GPU
        try:
            x = torch.randn(100, 100).cuda()
            print_ok("GPU test passed - can allocate memory")
        except Exception as e:
            print_error(f"GPU test failed: {e}")
    else:
        print_warning("CUDA is NOT available - will use CPU")
        print_info("System will work but slower (~5 FPS instead of 30 FPS)")
        print_info("To use GPU:")
        print_info("  1. Install NVIDIA GPU drivers")
        print_info("  2. Install CUDA Toolkit 11.8 or 12.x")
        print_info("  3. Reinstall PyTorch with CUDA:")
        print_info("     pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")

except ImportError:
    print_error("PyTorch not installed!")
    print_info("Install with: pip install torch")

# ===== CHECK 3: Models =====
print_header("3. Checking AI Models")

model_dir = "./models"
if not os.path.exists(model_dir):
    print_error(f"Models directory not found: {model_dir}")
    print_info("Creating models directory...")
    os.makedirs(model_dir, exist_ok=True)

models_to_check = [
    ("weight.pt", "Main YOLO model"),
    ("weight.onnx", "ONNX model (optional)"),
    ("yolov8n.pt", "YOLOv8 nano (fallback)"),
    ("yolov8n-pose.pt", "YOLOv8 pose model (optional)")
]

found_models = []
for model_file, description in models_to_check:
    path = os.path.join(model_dir, model_file)
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / 1024 / 1024
        print_ok(f"{description:40} - {size_mb:.1f} MB")
        found_models.append(model_file)
    else:
        print_warning(f"{description:40} - NOT FOUND")

if not found_models:
    print_error("\nNo models found!")
    print_info("Downloading models...")
    print_info("Run: python download_models.py")
    print_info("Or manually download YOLOv8 model:")
    print_info("  from ultralytics import YOLO")
    print_info("  model = YOLO('yolov8n.pt')  # Auto-downloads")
elif "weight.pt" not in found_models and "yolov8n.pt" not in found_models:
    print_warning("\nMain model (weight.pt) not found, will try to download...")
    print_info("Run: python download_models.py")

# ===== CHECK 4: Video Devices =====
print_header("4. Checking Video Devices")

try:
    import cv2
    
    # Test webcam
    print("Testing webcam access...")
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print_ok(f"Webcam 0 available - Resolution: {w}x{h}")
            cap.release()
        else:
            print_warning("Webcam opened but cannot read frame")
            cap.release()
    else:
        print_warning("Webcam 0 not available")
        print_info("If you have a webcam, check if another app is using it")
        print_info("If no webcam, you can use:")
        print_info("  - RTSP camera: rtsp://camera-ip/stream")
        print_info("  - Video file: file:///path/to/video.mp4")
        print_info("  - YouTube: youtube:VIDEO_ID")
    
    # Test OpenCV build info
    print(f"\nOpenCV Build Info:")
    print(f"   Version: {cv2.__version__}")
    print(f"   CUDA support: {cv2.cuda.getCudaEnabledDeviceCount() > 0 if hasattr(cv2, 'cuda') else 'No'}")

except Exception as e:
    print_error(f"OpenCV error: {e}")

# ===== CHECK 5: Backend Server =====
print_header("5. Checking Backend Configuration")

print(f"Working directory: {os.getcwd()}")
print(f"Backend directory exists: {os.path.exists('Backend')}")
print(f"Models directory: {os.path.exists('Backend/models') or os.path.exists('./models')}")
print(f"Config directory: {os.path.exists('Backend/config') or os.path.exists('./config')}")

# Check if backend_server.py exists
if os.path.exists('backend_server.py'):
    print_ok("backend_server.py found")
elif os.path.exists('Backend/backend_server.py'):
    print_ok("Backend/backend_server.py found")
else:
    print_error("backend_server.py not found!")

# ===== CHECK 6: Dependencies =====
print_header("6. Checking Dependencies")

try:
    import fastapi
    import uvicorn
    import websockets
    print_ok("FastAPI and dependencies installed")
except ImportError as e:
    print_error(f"Missing web framework dependencies: {e}")
    print_info("Install with: pip install -r requirements.txt")

# ===== SUMMARY & RECOMMENDATIONS =====
print_header("DIAGNOSTIC SUMMARY & RECOMMENDATIONS")

issues = []
recommendations = []

# Check CUDA
try:
    import torch
    if not torch.cuda.is_available():
        issues.append("CUDA not available (will use CPU - slower)")
        recommendations.append(
            "For GPU acceleration:\n"
            "  1. Install NVIDIA drivers\n"
            "  2. Install CUDA Toolkit 11.8 or 12.x\n"
            "  3. Reinstall PyTorch: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118"
        )
except:
    issues.append("PyTorch not installed")
    recommendations.append("Install PyTorch: pip install torch")

# Check models
if not found_models:
    issues.append("No YOLO models found")
    recommendations.append(
        "Download models:\n"
        "  python download_models.py\n"
        "  OR let it auto-download on first run"
    )

# Check webcam
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        issues.append("Webcam not available")
        recommendations.append(
            "Use alternative video source:\n"
            "  - RTSP camera: source=rtsp://camera-ip/stream\n"
            "  - Video file: source=file:///path/to/video.mp4\n"
            "  - YouTube: source=youtube:VIDEO_ID"
        )
    cap.release()
except:
    pass

if not issues:
    print(f"{Fore.GREEN}{'='*60}")
    print("✅ ALL SYSTEMS READY!")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    print("Your system is ready to run!")
    print("\nTo start:")
    print("  python backend_server.py")
    print("\nOr use the startup script:")
    print("  START_VEROLUX.bat")
else:
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"⚠️  FOUND {len(issues)} ISSUE(S)")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    for i, issue in enumerate(issues, 1):
        print(f"{Fore.YELLOW}{i}. {issue}{Style.RESET_ALL}")
    
    if recommendations:
        print(f"\n{Fore.CYAN}Recommendations:{Style.RESET_ALL}\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}\n")

print(f"\n{Fore.CYAN}Quick Fixes:{Style.RESET_ALL}")
print("\n1. Install all dependencies:")
print("   pip install -r requirements.txt")
print("\n2. Download models:")
print("   python download_models.py")
print("\n3. For GPU support (optional):")
print("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
print("\n4. Test again:")
print("   python diagnose_system.py")
print()













