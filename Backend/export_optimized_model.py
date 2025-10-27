#!/usr/bin/env python3
"""
Export YOLO model to optimized formats for maximum FPS
Supports: TensorRT INT8, TensorRT FP16, ONNX
"""

import os
import sys
import argparse
from pathlib import Path

def export_tensorrt_int8(model_path: str, output_dir: str = "models"):
    """Export to TensorRT INT8 (fastest, requires calibration)"""
    try:
        from ultralytics import YOLO
        
        print(f"🚀 Loading model: {model_path}")
        model = YOLO(model_path)
        
        print("📦 Exporting to TensorRT INT8...")
        export_path = model.export(
            format='engine',        # TensorRT
            half=False,             # Don't use FP16, use INT8
            int8=True,              # Enable INT8 quantization
            workspace=4,            # GPU memory in GB
            verbose=True,
            batch=1,
            imgsz=416,              # Optimized size for 30 FPS
            simplify=True,
            device=0                # GPU 0
        )
        
        print(f"✅ INT8 TensorRT model exported: {export_path}")
        print(f"   Expected FPS gain: +40-50%")
        return export_path
        
    except Exception as e:
        print(f"❌ INT8 export failed: {e}")
        print("   Trying FP16 instead...")
        return export_tensorrt_fp16(model_path, output_dir)


def export_tensorrt_fp16(model_path: str, output_dir: str = "models"):
    """Export to TensorRT FP16 (fast, no calibration needed)"""
    try:
        from ultralytics import YOLO
        
        print(f"🚀 Loading model: {model_path}")
        model = YOLO(model_path)
        
        print("📦 Exporting to TensorRT FP16...")
        export_path = model.export(
            format='engine',        # TensorRT
            half=True,              # Use FP16
            int8=False,
            workspace=4,
            verbose=True,
            batch=1,
            imgsz=416,
            simplify=True,
            device=0
        )
        
        print(f"✅ FP16 TensorRT model exported: {export_path}")
        print(f"   Expected FPS gain: +30-40%")
        return export_path
        
    except Exception as e:
        print(f"❌ FP16 export failed: {e}")
        return None


def export_onnx(model_path: str, output_dir: str = "models"):
    """Export to ONNX (portable, good performance)"""
    try:
        from ultralytics import YOLO
        
        print(f"🚀 Loading model: {model_path}")
        model = YOLO(model_path)
        
        print("📦 Exporting to ONNX...")
        export_path = model.export(
            format='onnx',
            opset=12,
            simplify=True,
            dynamic=False,
            imgsz=416
        )
        
        print(f"✅ ONNX model exported: {export_path}")
        print(f"   Expected FPS gain: +20-30% (with ONNX Runtime)")
        return export_path
        
    except Exception as e:
        print(f"❌ ONNX export failed: {e}")
        return None


def optimize_pytorch_model(model_path: str):
    """Optimize PyTorch model with FP16 and JIT compilation"""
    try:
        from ultralytics import YOLO
        import torch
        
        print(f"🚀 Loading model: {model_path}")
        model = YOLO(model_path)
        
        # Convert to FP16
        if torch.cuda.is_available():
            print("🔧 Converting to FP16...")
            model.model.half()
            
            # Fuse layers
            print("🔧 Fusing layers...")
            model.fuse()
            
            # Save optimized model
            optimized_path = model_path.replace('.pt', '_fp16_optimized.pt')
            torch.save(model.model.state_dict(), optimized_path)
            
            print(f"✅ Optimized PyTorch model saved: {optimized_path}")
            print(f"   Expected FPS gain: +15-25%")
            return optimized_path
        else:
            print("⚠️  CUDA not available, skipping FP16 optimization")
            return None
            
    except Exception as e:
        print(f"❌ PyTorch optimization failed: {e}")
        return None


def main():
    # Set console encoding to UTF-8 for emoji support
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="Export YOLO model to optimized formats")
    parser.add_argument(
        '--model', 
        type=str, 
        default='models/weight.pt',
        help='Path to YOLO model (.pt file)'
    )
    parser.add_argument(
        '--format', 
        type=str, 
        choices=['int8', 'fp16', 'onnx', 'pytorch', 'all'],
        default='all',
        help='Export format'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"❌ Model not found: {args.model}")
        print(f"   Available models:")
        models_dir = Path('models')
        if models_dir.exists():
            for pt_file in models_dir.glob('*.pt'):
                print(f"   - {pt_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("🎯 YOLO Model Optimization Tool")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Format: {args.format}")
    print("=" * 70)
    print()
    
    # Export based on format
    if args.format == 'int8' or args.format == 'all':
        export_tensorrt_int8(args.model, args.output_dir)
        print()
    
    if args.format == 'fp16' or args.format == 'all':
        export_tensorrt_fp16(args.model, args.output_dir)
        print()
    
    if args.format == 'onnx' or args.format == 'all':
        export_onnx(args.model, args.output_dir)
        print()
    
    if args.format == 'pytorch' or args.format == 'all':
        optimize_pytorch_model(args.model)
        print()
    
    print("=" * 70)
    print("✅ Model optimization complete!")
    print("=" * 70)
    print()
    print("📝 Usage:")
    print("   1. Set MODEL_PATH environment variable to optimized model")
    print("   2. Restart backend_server.py")
    print("   3. Monitor FPS improvement in WebSocket responses")
    print()


if __name__ == "__main__":
    main()

