#!/usr/bin/env python3
"""
Verolux Enterprise - Model Download Script
Downloads and sets up AI models for the system
"""

import os
import sys
import argparse
from pathlib import Path

def download_yolo_model(model_name="yolov8n.pt", force_download=False):
    """Download YOLO model"""
    try:
        from ultralytics import YOLO
        print(f"🧠 Downloading {model_name}...")
        
        # Create models directory
        models_dir = Path("Backend/models")
        models_dir.mkdir(exist_ok=True)
        
        # Download model
        model = YOLO(model_name)
        
        # Move to models directory
        model_path = models_dir / "weight.pt"
        if model_path.exists() and not force_download:
            print(f"✅ Model already exists at {model_path}")
            return str(model_path)
        
        # Save model
        model.save(str(model_path))
        print(f"✅ Model saved to {model_path}")
        return str(model_path)
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return None

def download_semantic_model():
    """Download semantic search model"""
    try:
        from sentence_transformers import SentenceTransformer
        print("🧠 Downloading semantic search model...")
        
        # Download model (this will cache it)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Semantic search model downloaded")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading semantic model: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'ultralytics',
        'sentence_transformers',
        'fastapi',
        'uvicorn',
        'opencv-python',
        'numpy',
        'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r Backend/requirements.txt")
        return False
    
    print("✅ All dependencies found")
    return True

def main():
    parser = argparse.ArgumentParser(description="Download AI models for Verolux Enterprise")
    parser.add_argument("--force-download", action="store_true", help="Force download even if model exists")
    parser.add_argument("--yolo-model", default="yolov8n.pt", help="YOLO model to download")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check")
    
    args = parser.parse_args()
    
    print("🚀 Verolux Enterprise - Model Downloader")
    print("=" * 50)
    
    # Check dependencies
    if not args.skip_deps:
        if not check_dependencies():
            print("\n❌ Please install missing dependencies first")
            sys.exit(1)
    
    # Download YOLO model
    yolo_path = download_yolo_model(args.yolo_model, args.force_download)
    if not yolo_path:
        print("❌ Failed to download YOLO model")
        sys.exit(1)
    
    # Download semantic model
    if not download_semantic_model():
        print("⚠️ Failed to download semantic model (will download on first use)")
    
    print("\n🎉 Model download complete!")
    print(f"📁 Models saved to: Backend/models/")
    print(f"🔧 YOLO model: {yolo_path}")
    print("\n🚀 You can now start the system!")

if __name__ == "__main__":
    main()

