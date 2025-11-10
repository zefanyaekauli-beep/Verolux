#!/usr/bin/env python3
"""
Simple Model Downloader
Downloads YOLO models if not present
"""
import os
from pathlib import Path

print("Downloading YOLO models...")
print()

# Create models directory
models_dir = Path("./models")
models_dir.mkdir(exist_ok=True)

# Check if main model exists
if os.path.exists("./models/weight.pt"):
    print("✅ Main model (weight.pt) already exists")
else:
    print("📦 Downloading YOLOv8n model...")
    
    try:
        from ultralytics import YOLO
        
        # Download YOLOv8n (will auto-download)
        model = YOLO('yolov8n.pt')
        
        # Find where it was downloaded
        import ultralytics
        model_path = model.ckpt_path
        
        print(f"✅ Model downloaded to: {model_path}")
        
        # Copy to our models directory
        import shutil
        target = "./models/weight.pt"
        shutil.copy(model_path, target)
        
        print(f"✅ Model copied to: {target}")
        print()
        print("Main model is ready!")
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print()
        print("Manual download:")
        print("  1. Download from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt")
        print("  2. Save to: Backend/models/weight.pt")

# Download pose model (optional)
if not os.path.exists("./models/yolov8n-pose.pt"):
    print()
    print("📦 Downloading YOLOv8 Pose model (optional)...")
    
    try:
        from ultralytics import YOLO
        
        model = YOLO('yolov8n-pose.pt')
        model_path = model.ckpt_path
        
        import shutil
        target = "./models/yolov8n-pose.pt"
        shutil.copy(model_path, target)
        
        print(f"✅ Pose model ready: {target}")
        
    except Exception as e:
        print(f"⚠️  Pose model download skipped: {e}")
        print("   (Not critical - pose detection is optional)")

print()
print("="*60)
print("✅ Model setup complete!")
print("="*60)
print()
print("Models available in ./models/:")
for f in os.listdir("./models"):
    if f.endswith(('.pt', '.onnx', '.engine')):
        size_mb = os.path.getsize(f"./models/{f}") / 1024 / 1024
        print(f"  - {f:30} ({size_mb:.1f} MB)")

print()
print("To start the system:")
print("  python backend_server.py")
print()




















